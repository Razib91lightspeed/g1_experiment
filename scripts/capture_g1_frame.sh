#!/usr/bin/env bash
set -euo pipefail

OUTPUT="$HOME/Desktop/razib/g1_experiment/camera/g1_frame.jpg"
TEMP="${OUTPUT}.partial"

trap 'rm -f "$TEMP"' EXIT

# Capture directly from G1 to DEVBOX over SSH.
# No image is written to the robot's filesystem.

ssh -T unitree@10.11.1.2 \
  'timeout 15 gst-launch-1.0 -q \
    v4l2src device=/dev/video6 num-buffers=1 \
    ! videoconvert \
    ! jpegenc \
    ! fdsink fd=1' \
  > "$TEMP"

# Check JPEG signature before replacing the existing frame.
python3 - "$TEMP" <<'PY'
import sys
from PIL import Image

with Image.open(sys.argv[1]) as image:
    image.verify()

print("JPEG image verified")
PY

mv "$TEMP" "$OUTPUT"

echo "Captured: $OUTPUT"
ls -lh "$OUTPUT"
