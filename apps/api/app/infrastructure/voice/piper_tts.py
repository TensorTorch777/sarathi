"""Local Piper TTS — calm, natural narration without cloud APIs."""

from __future__ import annotations

import asyncio
import io
import time
import wave
from functools import lru_cache
from pathlib import Path

from app.core.config import Settings
from app.core.errors import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


class PiperTTS:
    """Synthesize speech with a local Piper voice model."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._voice = None
        self._sample_rate = int(settings.tts_sample_rate)
        self._lock = asyncio.Lock()

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    async def warmup(self) -> None:
        """Load Piper voice weights."""
        await asyncio.to_thread(self._ensure_voice)

    def _ensure_voice(self):
        if self._voice is not None:
            return self._voice
        from piper import PiperVoice

        model_path = Path(self._settings.piper_model_path).expanduser()
        if not model_path.exists():
            raise AppError(
                f"Piper model not found at {model_path}. "
                "Run scripts/voice/download_piper_voice.sh",
                code="piper_model_missing",
                status_code=503,
            )
        logger.info("piper_loading", model=str(model_path))
        self._voice = PiperVoice.load(model_path, use_cuda=self._settings.piper_use_cuda)
        try:
            self._sample_rate = int(self._voice.config.sample_rate)
        except Exception:  # noqa: BLE001
            self._sample_rate = int(self._settings.tts_sample_rate)
        return self._voice

    async def synthesize_pcm16(self, text: str) -> tuple[bytes, float]:
        """Return PCM16 mono bytes and latency_ms for speakable text."""
        cleaned = " ".join(text.split()).strip()
        if not cleaned:
            return b"", 0.0

        async with self._lock:
            started = time.perf_counter()
            pcm = await asyncio.to_thread(self._synthesize_sync, cleaned)
            latency_ms = (time.perf_counter() - started) * 1000.0
        return pcm, latency_ms

    async def synthesize_wav(self, text: str) -> bytes:
        """Return a complete WAV container for HTTP responses."""
        pcm, _ = await self.synthesize_pcm16(text)
        return _pcm16_to_wav(pcm, self.sample_rate)

    def _synthesize_sync(self, text: str) -> bytes:
        from piper.config import SynthesisConfig

        voice = self._ensure_voice()
        # Slightly slower + softer for a calm contemplative tone.
        config = SynthesisConfig(
            length_scale=float(self._settings.tts_length_scale),
            noise_scale=float(self._settings.tts_noise_scale),
            noise_w_scale=float(self._settings.tts_noise_w_scale),
        )
        try:
            chunks = list(voice.synthesize(text, syn_config=config))
        except Exception as exc:  # noqa: BLE001
            raise AppError(
                "Piper TTS synthesis failed",
                code="piper_error",
                status_code=502,
                details={"error": str(exc)},
            ) from exc
        return b"".join(chunk.audio_int16_bytes for chunk in chunks)


def _pcm16_to_wav(pcm16: bytes, sample_rate: int) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm16)
    return buffer.getvalue()


def pcm16_duration_ms(pcm16: bytes, sample_rate: int) -> float:
    """Duration of PCM16 mono audio in milliseconds."""
    if not pcm16 or sample_rate <= 0:
        return 0.0
    frames = len(pcm16) // 2
    return (frames / float(sample_rate)) * 1000.0


@lru_cache
def get_piper_tts() -> PiperTTS:
    """Process-wide Piper singleton."""
    from app.core.config import get_settings

    return PiperTTS(get_settings())
