"""Local Whisper speech-to-text via faster-whisper."""

from __future__ import annotations

import asyncio
import time
from functools import lru_cache

import numpy as np

from app.core.config import Settings
from app.core.errors import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


class WhisperSTT:
    """Transcribe PCM16 / float32 audio with a local Whisper model."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = None
        self._device = settings.whisper_device
        self._compute_type = settings.whisper_compute_type
        self._lock = asyncio.Lock()

    @property
    def model_name(self) -> str:
        return self._settings.whisper_model

    async def warmup(self) -> None:
        """Load the model and run a tiny decode to validate the device."""
        await asyncio.to_thread(self._ensure_model)
        silence = np.zeros(16000, dtype=np.float32)
        try:
            await self.transcribe_float32(silence, sample_rate=16000)
        except Exception as exc:  # noqa: BLE001
            logger.warning("whisper_warmup_transcribe_failed", error=str(exc))
            if self._device != "cpu":
                self._fallback_cpu()
                await self.transcribe_float32(silence, sample_rate=16000)

    def _fallback_cpu(self) -> None:
        logger.warning("whisper_falling_back_to_cpu", previous_device=self._device)
        self._model = None
        self._device = "cpu"
        self._compute_type = "int8"
        self._ensure_model()

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        from faster_whisper import WhisperModel

        logger.info(
            "whisper_loading",
            model=self._settings.whisper_model,
            device=self._device,
            compute_type=self._compute_type,
        )
        try:
            self._model = WhisperModel(
                self._settings.whisper_model,
                device=self._device,
                compute_type=self._compute_type,
            )
        except Exception as exc:  # noqa: BLE001
            if self._device != "cpu":
                logger.warning("whisper_load_cuda_failed", error=str(exc))
                self._device = "cpu"
                self._compute_type = "int8"
                self._model = WhisperModel(
                    self._settings.whisper_model,
                    device="cpu",
                    compute_type="int8",
                )
            else:
                raise
        return self._model

    async def transcribe_pcm16(
        self,
        pcm16: bytes,
        *,
        sample_rate: int = 16000,
    ) -> tuple[str, float]:
        """Transcribe little-endian PCM16 mono audio. Returns (text, latency_ms)."""
        if not pcm16:
            return "", 0.0
        audio = np.frombuffer(pcm16, dtype=np.int16).astype(np.float32) / 32768.0
        return await self.transcribe_float32(audio, sample_rate=sample_rate)

    async def transcribe_float32(
        self,
        audio: np.ndarray,
        *,
        sample_rate: int = 16000,
    ) -> tuple[str, float]:
        """Transcribe float32 mono waveform in [-1, 1]."""
        if audio.size == 0:
            return "", 0.0
        if sample_rate != 16000:
            audio = _resample_linear(audio, sample_rate, 16000)

        async with self._lock:
            started = time.perf_counter()
            try:
                text = await asyncio.to_thread(self._transcribe_sync, audio)
            except AppError:
                if self._device != "cpu":
                    self._fallback_cpu()
                    text = await asyncio.to_thread(self._transcribe_sync, audio)
                else:
                    raise
            latency_ms = (time.perf_counter() - started) * 1000.0

        logger.info(
            "whisper_transcribed",
            chars=len(text),
            latency_ms=round(latency_ms, 1),
            device=self._device,
        )
        return text, latency_ms

    def _transcribe_sync(self, audio: np.ndarray) -> str:
        model = self._ensure_model()
        try:
            segments, _info = model.transcribe(
                audio,
                language=self._settings.whisper_language or None,
                beam_size=1,
                best_of=1,
                vad_filter=True,
                condition_on_previous_text=False,
                without_timestamps=True,
            )
            return " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:  # noqa: BLE001
            raise AppError(
                "Whisper transcription failed",
                code="whisper_error",
                status_code=502,
                details={"error": str(exc), "device": self._device},
            ) from exc


def _resample_linear(audio: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    if src_rate == dst_rate or audio.size == 0:
        return audio
    duration = audio.shape[0] / float(src_rate)
    target_len = max(1, int(duration * dst_rate))
    x_old = np.linspace(0.0, 1.0, num=audio.shape[0], endpoint=False)
    x_new = np.linspace(0.0, 1.0, num=target_len, endpoint=False)
    return np.interp(x_new, x_old, audio).astype(np.float32)


@lru_cache
def get_whisper_stt() -> WhisperSTT:
    """Process-wide Whisper singleton."""
    from app.core.config import get_settings

    return WhisperSTT(get_settings())
