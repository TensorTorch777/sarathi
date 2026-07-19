"""Voice mode — Whisper STT, streamed answers, Piper TTS, interruptible session."""

from __future__ import annotations

import asyncio
import base64
import json
import time
from typing import Any
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.api.v1.deps import CurrentUserDep
from app.application.dto.answer import GenerateAnswerQuery
from app.application.use_cases.answer.stream_answer import StreamAnswerUseCase
from app.core.config import get_settings
from app.core.di.providers import get_token_store
from app.core.errors import AppError, UnauthorizedError
from app.core.logging import get_logger
from app.core.security import decode_token
from app.domain.enums import TokenType
from app.infrastructure.db.repositories import SqlAlchemyUserRepository
from app.infrastructure.db.session import get_session_factory
from app.infrastructure.voice.piper_tts import get_piper_tts
from app.infrastructure.voice.spoken_text import answer_to_spoken, iter_speakable_sentences
from app.infrastructure.voice.whisper_stt import get_whisper_stt

logger = get_logger(__name__)
router = APIRouter(prefix="/voice")


class SpeakRequest(BaseModel):
    """Request body for one-shot TTS."""

    text: str = Field(min_length=1, max_length=8000)


class TranscribeResponse(BaseModel):
    """Whisper transcription result."""

    text: str
    latency_ms: float


@router.get("/status")
async def voice_status(_user: CurrentUserDep) -> dict[str, Any]:
    """Report whether local voice services are configured."""
    settings = get_settings()
    from pathlib import Path

    model = Path(settings.piper_model_path).expanduser()
    return {
        "enabled": settings.voice_enabled,
        "whisper_model": settings.whisper_model,
        "whisper_device": settings.whisper_device,
        "piper_model_path": str(model),
        "piper_ready": model.exists(),
        "tts_sample_rate": settings.tts_sample_rate,
        "stt_target_ms": settings.voice_stt_target_ms,
    }


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    _user: CurrentUserDep,
    file: UploadFile = File(...),
    sample_rate: int = Query(default=16000, ge=8000, le=48000),
) -> TranscribeResponse:
    """Transcribe an uploaded audio blob with local Whisper."""
    settings = get_settings()
    if not settings.voice_enabled:
        raise AppError("Voice mode is disabled", code="voice_disabled", status_code=503)

    raw = await file.read()
    if not raw:
        return TranscribeResponse(text="", latency_ms=0.0)

    stt = get_whisper_stt()
    # Accept raw PCM16 or try to decode via soundfile for wav/webm/ogg.
    content_type = (file.content_type or "").lower()
    if "wav" in content_type or "webm" in content_type or "ogg" in content_type or raw[:4] == b"RIFF":
        text, latency = await _transcribe_container(raw, stt)
    else:
        text, latency = await stt.transcribe_pcm16(raw, sample_rate=sample_rate)
    return TranscribeResponse(text=text, latency_ms=latency)


@router.post("/speak")
async def speak_text(
    body: SpeakRequest,
    _user: CurrentUserDep,
) -> Response:
    """Synthesize calm narration audio (WAV) with Piper."""
    settings = get_settings()
    if not settings.voice_enabled:
        raise AppError("Voice mode is disabled", code="voice_disabled", status_code=503)
    tts = get_piper_tts()
    spoken = answer_to_spoken(body.text)
    wav = await tts.synthesize_wav(spoken)
    return Response(content=wav, media_type="audio/wav")


@router.websocket("/session")
async def voice_session(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    """Full-duplex voice turn: STT → streamed answer → streamed TTS.

    Client messages:
      - {type: "utterance", audio_b64: "...", sample_rate: 16000, format: "pcm_s16le"}
      - {type: "interrupt"}
      - {type: "ping"}

    Server messages:
      - ready | partial/final transcript | answer deltas | audio chunks | done | error
    """
    settings = get_settings()
    if not settings.voice_enabled:
        await websocket.close(code=1013, reason="Voice disabled")
        return

    try:
        user_id = await _authenticate_ws(token)
    except UnauthorizedError as exc:
        await websocket.close(code=4401, reason=str(exc))
        return

    await websocket.accept()
    await websocket.send_json(
        {
            "type": "ready",
            "whisper_model": settings.whisper_model,
            "tts_sample_rate": get_piper_tts().sample_rate,
            "stt_target_ms": settings.voice_stt_target_ms,
        },
    )

    interrupt_event = asyncio.Event()
    turn_task: asyncio.Task[None] | None = None

    try:
        while True:
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = payload.get("type")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong", "t": time.time()})
                continue

            if msg_type == "interrupt":
                interrupt_event.set()
                if turn_task and not turn_task.done():
                    turn_task.cancel()
                await websocket.send_json({"type": "interrupted"})
                continue

            if msg_type == "utterance":
                interrupt_event = asyncio.Event()
                if turn_task and not turn_task.done():
                    turn_task.cancel()
                    try:
                        await turn_task
                    except (asyncio.CancelledError, Exception):  # noqa: BLE001
                        pass
                turn_task = asyncio.create_task(
                    _run_voice_turn(
                        websocket,
                        payload,
                        interrupt_event,
                        user_id=user_id,
                    ),
                )
                continue

            await websocket.send_json(
                {"type": "error", "message": f"Unknown message type: {msg_type}"},
            )
    except WebSocketDisconnect:
        logger.info("voice_session_disconnected")
    finally:
        interrupt_event.set()
        if turn_task and not turn_task.done():
            turn_task.cancel()


async def _authenticate_ws(token: str) -> UUID:
    settings = get_settings()
    payload = decode_token(token, settings=settings, expected_type=TokenType.ACCESS)
    token_store = await get_token_store()
    if await token_store.is_access_token_denylisted(payload.jti):
        raise UnauthorizedError("Token has been revoked")

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await SqlAlchemyUserRepository(session).get_by_id(payload.sub)
        if user is None or not user.is_active:
            raise UnauthorizedError("User is inactive or not found")
        return user.id


async def _run_voice_turn(
    websocket: WebSocket,
    payload: dict[str, Any],
    interrupt_event: asyncio.Event,
    *,
    user_id: UUID,
) -> None:
    settings = get_settings()
    turn_started = time.perf_counter()
    try:
        audio_b64 = payload.get("audio_b64") or ""
        sample_rate = int(payload.get("sample_rate") or 16000)
        conversation_id_raw = payload.get("conversation_id")
        conversation_id = UUID(conversation_id_raw) if conversation_id_raw else None
        pcm = base64.b64decode(audio_b64)

        stt = get_whisper_stt()
        text, stt_ms = await stt.transcribe_pcm16(pcm, sample_rate=sample_rate)
        if interrupt_event.is_set():
            return

        await websocket.send_json(
            {
                "type": "final_transcript",
                "text": text,
                "latency_ms": round(stt_ms, 1),
            },
        )
        if not text:
            await websocket.send_json(
                {"type": "error", "message": "No speech detected. Please try again."},
            )
            return

        session_factory = get_session_factory()
        async with session_factory() as session:
            use_case = await _build_stream_use_case(session, settings)
            tts = get_piper_tts()
            full_answer = ""
            spoken_cursor = 0
            first_audio_sent = False
            first_audio_elapsed_ms: float | None = None
            bridge_spoken = False

            async for event in use_case.execute(
                GenerateAnswerQuery(
                    message=text,
                    conversation_id=conversation_id,
                    top_k=3,
                    voice_fast=True,
                    user_id=user_id,
                ),
            ):
                if interrupt_event.is_set():
                    await websocket.send_json({"type": "interrupted"})
                    return

                if event["type"] == "meta":
                    await websocket.send_json(
                        {"type": "meta", **{k: v for k, v in event.items() if k != "type"}},
                    )
                    # Early calm bridge from the top verse — cuts perceived latency.
                    verses = event.get("verses") or []
                    if verses and not bridge_spoken and not interrupt_event.is_set():
                        primary = verses[0]
                        citation = primary.get("citation") or "the Gita"
                        translation = (primary.get("translation") or "").strip()
                        if translation:
                            bridge = (
                                f"From {citation}. {translation} "
                                "Let me reflect on this with you."
                            )
                            elapsed = await _send_tts_chunk(
                                websocket,
                                tts,
                                bridge,
                                mark_first=True,
                                turn_started=turn_started,
                                stt_ms=stt_ms,
                            )
                            first_audio_sent = True
                            first_audio_elapsed_ms = elapsed
                            bridge_spoken = True
                    continue

                if event["type"] == "delta":
                    delta = str(event.get("text") or "")
                    full_answer += delta
                    await websocket.send_json({"type": "answer_delta", "text": delta})

                    spoken = answer_to_spoken(full_answer)
                    pending = spoken[spoken_cursor:].lstrip()
                    sentences, _remainder = iter_speakable_sentences(pending)
                    for sentence in sentences:
                        if interrupt_event.is_set():
                            await websocket.send_json({"type": "interrupted"})
                            return
                        # Advance cursor by finding the sentence in spoken text.
                        idx = spoken.find(sentence, spoken_cursor)
                        if idx >= 0:
                            spoken_cursor = idx + len(sentence)
                        elapsed = await _send_tts_chunk(
                            websocket,
                            tts,
                            sentence,
                            mark_first=not first_audio_sent,
                            turn_started=turn_started,
                            stt_ms=stt_ms,
                        )
                        if not first_audio_sent:
                            first_audio_sent = True
                            first_audio_elapsed_ms = elapsed
                    continue

                if event["type"] == "done":
                    full_answer = str(event.get("answer") or full_answer)
                    spoken = answer_to_spoken(full_answer)
                    leftover = spoken[spoken_cursor:].strip()
                    if leftover and not interrupt_event.is_set():
                        elapsed = await _send_tts_chunk(
                            websocket,
                            tts,
                            leftover,
                            mark_first=not first_audio_sent,
                            turn_started=turn_started,
                            stt_ms=stt_ms,
                        )
                        if not first_audio_sent:
                            first_audio_sent = True
                            first_audio_elapsed_ms = elapsed

                    total_ms = (time.perf_counter() - turn_started) * 1000.0
                    await websocket.send_json(
                        {
                            "type": "done",
                            "answer": full_answer,
                            "emotions": event.get("emotions", []),
                            "topics": event.get("topics", []),
                            "rewritten_query": event.get("rewritten_query", ""),
                            "citations": event.get("citations", []),
                            "verses": event.get("verses", []),
                            "transcript": text,
                            "metrics": {
                                "stt_ms": round(stt_ms, 1),
                                "total_ms": round(total_ms, 1),
                                "first_audio_ms": (
                                    round(first_audio_elapsed_ms, 1)
                                    if first_audio_elapsed_ms is not None
                                    else None
                                ),
                                "first_audio_under_2s": (
                                    first_audio_elapsed_ms is not None
                                    and first_audio_elapsed_ms <= 2000.0
                                ),
                            },
                        },
                    )
    except asyncio.CancelledError:
        await websocket.send_json({"type": "interrupted"})
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("voice_turn_failed", error=str(exc))
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:  # noqa: BLE001
            pass


async def _send_tts_chunk(
    websocket: WebSocket,
    tts: Any,
    text: str,
    *,
    mark_first: bool,
    turn_started: float,
    stt_ms: float,
) -> float:
    pcm, tts_ms = await tts.synthesize_pcm16(text)
    elapsed = (time.perf_counter() - turn_started) * 1000.0
    if not pcm:
        return elapsed
    await websocket.send_json(
        {
            "type": "audio",
            "format": "pcm_s16le",
            "sample_rate": tts.sample_rate,
            "text": text,
            "audio_b64": base64.b64encode(pcm).decode("ascii"),
            "tts_ms": round(tts_ms, 1),
            "first_audio": mark_first,
            "elapsed_ms": round(elapsed, 1),
            "stt_ms": round(stt_ms, 1),
        },
    )
    return elapsed


async def _build_stream_use_case(session: Any, settings: Any) -> StreamAnswerUseCase:
    from app.infrastructure.answer.factory import build_generate_answer_use_case

    base = await build_generate_answer_use_case(session=session, settings=settings)
    return StreamAnswerUseCase(base)


async def _transcribe_container(raw: bytes, stt: Any) -> tuple[str, float]:
    import io

    import numpy as np
    import soundfile as sf

    try:
        audio, rate = sf.read(io.BytesIO(raw), dtype="float32", always_2d=False)
    except Exception as exc:  # noqa: BLE001
        raise AppError(
            "Could not decode audio. Send wav/webm or raw PCM16.",
            code="audio_decode_error",
            status_code=400,
            details={"error": str(exc)},
        ) from exc
    if getattr(audio, "ndim", 1) > 1:
        audio = np.mean(audio, axis=1)
    return await stt.transcribe_float32(audio, sample_rate=int(rate))
