#!/usr/bin/env bash
# Download a calm Piper voice for Sarathi narration (no API keys).
set -euo pipefail

VOICE_DIR="${PIPER_VOICE_DIR:-$HOME/.local/share/sarathi/piper}"
VOICE_NAME="${PIPER_VOICE_NAME:-en_US-lessac-medium}"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium"

mkdir -p "$VOICE_DIR"
cd "$VOICE_DIR"

if [[ ! -f "${VOICE_NAME}.onnx" ]]; then
  echo "Downloading ${VOICE_NAME}.onnx ..."
  curl -fL -o "${VOICE_NAME}.onnx" "${BASE_URL}/${VOICE_NAME}.onnx"
fi

if [[ ! -f "${VOICE_NAME}.onnx.json" ]]; then
  echo "Downloading ${VOICE_NAME}.onnx.json ..."
  curl -fL -o "${VOICE_NAME}.onnx.json" "${BASE_URL}/${VOICE_NAME}.onnx.json"
fi

echo "Piper voice ready at: ${VOICE_DIR}/${VOICE_NAME}.onnx"
