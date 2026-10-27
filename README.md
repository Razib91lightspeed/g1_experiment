# Raapple — Unitree G1 Physical AI Experiments

Experimental development workspace for **Raapple**, a Unitree G1 humanoid robot at FieldLab, Tampere University of Applied Sciences (TAMK).

The project connects the G1's forehead camera to NVIDIA DGX Spark for vision-language model (VLM) inference and explores robot perception, task decisions, and speech through the Unitree SDK2.

The current implementation supports camera capture, AI-based scene descriptions, basic person-visibility decisions, and native G1 text-to-speech. Robot movement is not enabled.

## 1. System Architecture

```text
Unitree G1 (10.11.1.2)
    |
    | Forehead RGB camera (/dev/video6)
    | Image streamed over SSH
    v
DEVBOX (10.11.0.30)
    |
    | Python perception client
    | SSH tunnel (127.0.0.1:8000)
    v
NVIDIA DGX Spark (10.11.0.50)
    |
    | Qwen3-VL-4B-Instruct
    | Image understanding / scene description
    v
DEVBOX
    |
    | Decision: wave / no_action
    | DRY RUN ONLY
    |
    +--> G1 audio experiments
         Unitree SDK2 AudioClient
         Native TTS through robot eth0
```

The robot's internal interface is `eth0` (`192.168.123.164`). Its lab Wi-Fi interface is `wlan0` (`10.11.1.2`).

## 2. Repository Structure

```text
g1_experiment/
├── audio/
│   ├── CMakeLists.txt
│   ├── g1_speak.cpp
│   └── include/
│       └── unitree/robot/g1/audio/
│           ├── g1_audio_api.hpp
│           └── g1_audio_client.hpp
├── controller/
│   ├── __init__.py
│   └── vision_decision.py
├── scripts/
│   └── capture_g1_frame.sh
├── spark_client/
│   ├── __init__.py
│   ├── describe_scene.py
│   └── vlm_client.py
├── camera/                   # Local captures; ignored by Git
├── .gitignore
└── README.md
```

## 3. Prerequisites

The tested development environment consists of:

| Component | Description |
|---|---|
| Unitree G1 | ARM64 robot with forehead camera and native audio |
| DEVBOX | Ubuntu x86_64, Python and Unitree SDK2 |
| NVIDIA DGX Spark | ARM64 NVIDIA GB10, GPU inference |
| VLM | Qwen/Qwen3-VL-4B-Instruct |
| SDK | Unitree SDK2 C++ |
| Network | Lab-local network with SSH connectivity |

The VLM server is hosted separately on Spark under `~/Desktop/razib/ai_models/services/qwen3_vl/`. Its container and model weights are not included in this repository.

## 4. Python Environment

On DEVBOX:

```bash
cd ~/Desktop/razib/g1_experiment

python3 -m venv .venv
source .venv/bin/activate

python -m pip install requests pillow
```

Activate the environment again in future terminal sessions:

```bash
cd ~/Desktop/razib/g1_experiment
source .venv/bin/activate
```

## 5. Spark VLM Connection

The Qwen API runs on NVIDIA DGX Spark and is accessed from DEVBOX through a local SSH tunnel.

Check the existing tunnel:

```bash
systemctl --user status g1-spark-tunnel.service
```

Verify the model API:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "model": "Qwen/Qwen3-VL-4B-Instruct",
  "cuda_available": true
}
```

The API uses the OpenAI-compatible endpoint:

```text
POST http://127.0.0.1:8000/v1/chat/completions
```

The working model is hosted on Spark, not on the robot.

## 6. Capture an Image from G1

The G1 forehead camera is available as `/dev/video6` in the tested configuration.

On DEVBOX:

```bash
cd ~/Desktop/razib/g1_experiment

bash scripts/capture_g1_frame.sh
```

The script acquires one JPEG frame from the robot through SSH and saves it locally as:

```text
camera/g1_frame.jpg
```

The image is not saved on the G1 by this capture procedure.

The camera device may need to be checked again if the robot hardware or device enumeration changes.

## 7. Describe the Scene with Qwen3-VL

With the Python environment active, Spark API available, and a captured image present:

```bash
python spark_client/describe_scene.py camera/g1_frame.jpg
```

This sends the image to the Qwen model and prints a natural-language scene description.

During testing, the model described a chair and other visible objects in the FieldLab environment.

These are exploratory inference results, not formally validated perception accuracy.

## 8. Vision Decision Controller

Run the current perception and decision prototype:

```bash
python controller/vision_decision.py
```

Current logic:

```text
Capture new camera frame
        |
        v
Qwen3-VL image inference
        |
        v
Person visible?
    /         \
  Yes          No
   |            |
  wave       no_action
   |            |
   +------------+
        |
        v
DRY RUN — NO ROBOT MOVEMENT
```

The `wave` output is only a proposed action. This project does not currently execute waving or locomotion.

## 9. G1 Native Text-to-Speech

The G1 speech prototype uses the C++ Unitree SDK2 `AudioClient`.

The native audio client was successfully tested on the robot itself using the internal network interface:

```cpp
unitree::robot::ChannelFactory::Instance()->Init(0, "eth0");
```

English text-to-speech is requested through:

```cpp
audio.TtsMaker("Hello, I am Raapple.", 1);
```

### Running the tested executable on G1

From DEVBOX:

```bash
ssh -T unitree@10.11.1.2 \
  'cd /home/unitree/g1_audio_test && timeout 40 ./build/g1_speak'
```

Successful SDK response:

```text
GetVolume result: 0
TtsMaker result: 0
Speech request completed.
```

### Building on G1

The tested SDK location is:

```text
/home/unitree/Desktop/razib/unitree_sdk2_g1
```

The robot uses `aarch64` libraries.

A local compatibility copy of the audio headers is included under `audio/include/` because the installed G1 SDK header contains a `PlayStream()` call incompatible with its base client API.

In this test-only copy, the unused `PlayStream()` method is disabled. Native `TtsMaker()` remains available.

**Build portability note:** The repository's current CMake configuration was originally prepared for DEVBOX and requires machine-specific path and architecture adjustments for G1. The robot-side test build used its existing ARM64 SDK and locally modified configuration. A portable build system is future work.

### Voice quality

The G1 native TTS currently uses the default English voice. More natural male speech through an external neural TTS model has not yet been integrated.

## 10. Current Project Status

| Feature | Status |
|---|---|
| G1 forehead camera capture | Working |
| DEVBOX to Spark SSH tunnel | Working |
| Qwen3-VL API inference | Working |
| AI scene description | Working |
| Person-visibility decision prototype | Working (experimental) |
| Action selection | Dry run |
| G1 native English TTS | Working |
| Natural male voice | Planned |
| Dynamic VLM-to-TTS integration | Planned |
| G1 waving | Not implemented |
| Autonomous movement | Disabled |

## 11. Next Development Steps

1. Make the audio program accept text dynamically without recompilation.
2. Integrate live Qwen3-VL scene descriptions with G1 speech.
3. Evaluate an external neural TTS model for a natural male voice.
4. Improve camera inference latency and investigate continuous perception.
5. Add structured task decisions and controlled execution interfaces.
6. Introduce supervised robot gestures only after safety and motion-interface validation.
7. Make the audio build reproducible across DEVBOX and G1.

## 12. Safety and Data Handling

- Robot movement is disabled in the current application.
- The perception controller operates in dry-run mode.
- The camera capture script streams images to DEVBOX without writing them to robot storage.
- Captured images, Python environments, build outputs, credentials, and model weights must not be committed.
- All physical robot actions require separate safety validation and explicit operator approval.

## License

No project license has been selected.

Third-party components, including Unitree SDK2 and Qwen model artifacts, remain subject to their respective licenses.
