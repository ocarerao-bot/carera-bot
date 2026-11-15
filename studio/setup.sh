#!/usr/bin/env bash
# Sets up the CarEra video studio at /home/claude/vid (all scripts use these absolute paths).
set -e
R="$(cd "$(dirname "$0")" && pwd)"
V=/home/claude/vid
mkdir -p $V/src $V/assets $V/fonts $V/voice
cp "$R"/src/* $V/src/; cp "$R"/assets/* $V/assets/; cp "$R"/fonts/* $V/fonts/
python3 -c "import kokoro_onnx, rembg, soundfile, scipy" 2>/dev/null || pip install -q --break-system-packages kokoro-onnx rembg soundfile scipy onnxruntime
B=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s $V/voice/kokoro-v1.0.onnx ] || curl -sSL -o $V/voice/kokoro-v1.0.onnx $B/kokoro-v1.0.onnx
[ -s $V/voice/voices-v1.0.bin ] || curl -sSL -o $V/voice/voices-v1.0.bin $B/voices-v1.0.bin
fc-list | grep -q "Inter-Black" || echo "WARN: Inter font missing - copy $V/fonts/Inter-Black.otf to /usr/share/fonts/opentype/inter/"
mkdir -p /usr/share/fonts/opentype/inter && [ -f /usr/share/fonts/opentype/inter/Inter-Black.otf ] || cp $V/fonts/Inter-Black.otf /usr/share/fonts/opentype/inter/
which ffmpeg >/dev/null || echo "WARN: ffmpeg missing"
echo "studio ready at $V"
