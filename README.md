# SightSense – AI-Powered Assistive Vision for the Visually Impaired

SightSense is a Raspberry Pi 5-based assistive-technology prototype that uses a camera, computer vision and spoken feedback to help a user understand nearby objects and people. The project is designed to provide short audio descriptions of the surroundings and, in a separate face-recognition mode, identify registered people.

> **Safety notice:** SightSense is an experimental assistive prototype. It can miss objects, misidentify people, produce delayed or incorrect descriptions, and may stop working when the camera, network or API is unavailable. It is **not** a replacement for a white cane, guide dog, established mobility aid or human assistance. Test it in controlled, safe environments.

---

## Contents

- [Features](#features)
- [How it works](#how-it-works)
- [Hardware and software](#hardware-and-software)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run SightSense](#run-sightsense)
- [Face recognition setup](#face-recognition-setup)
- [Useful Raspberry Pi commands](#useful-raspberry-pi-commands)
- [Troubleshooting](#troubleshooting)
- [Limitations and future improvements](#limitations-and-future-improvements)

## Features

### 1. Live surroundings description

- Captures frames from the Raspberry Pi camera using **Picamera2**.
- Sends selected camera frames to Google's Gemini vision model for scene understanding.
- Requests a concise description in English with simple Kannada support in the prompt.
- Sends the generated response to the speech module for audio playback.
- Uses a 640 × 480 camera configuration and a pause between spoken descriptions to avoid continuous repeated announcements.

### 2. Text-to-speech output

- Uses the **Sarvam AI** speech API through the `sarvamai` Python package.
- Generates speech audio and plays the resulting WAV file using `aplay`.
- The configured voice in the working version is `bulbul:v3` with the `ishita` speaker.
- The speech module includes a language mapping for Indian languages, including Kannada and Tamil.

### 3. Face detection and recognition

The face-recognition mode is a separate camera workflow from the Gemini surroundings-description mode.

- Detects faces with OpenCV's `FaceDetectorYN` using the YuNet model.
- Extracts face features with OpenCV's `FaceRecognizerSF` using the SFace model.
- Compares a detected face with the saved face database.
- Uses a configurable similarity threshold and announcement cooldown to reduce repeated spoken identification.
- The project database is stored as `face_models/face_database.npz`.

### 4. Translation support

A separate `translator.py` module has been used for translation experiments. Earlier versions used `deep_translator` and Argos Translate, with caching/rate-limiting work to reduce repeated requests. Translation availability depends on the current implementation, installed language models and network/API access. The Gemini prompt's English/simple-Kannada response and the Sarvam speech language setting are separate from this optional translator module.

---

## How it works

### Surroundings-description flow

```text
Raspberry Pi Camera
        |
        v
     Picamera2
        |
        v
 Capture RGB frame (640 x 480)
        |
        v
 Send image + prompt to Gemini Vision
        |
        v
 Receive concise scene description
        |
        v
       speech.py
        |
        v
 Sarvam AI text-to-speech
        |
        v
       aplay
        |
        v
 Speaker / earphones
```

### Face-recognition flow

```text
Raspberry Pi Camera
        |
        v
     Picamera2
        |
        v
 OpenCV YuNet face detection
        |
        v
 OpenCV SFace feature extraction
        |
        v
 Compare with face_database.npz
        |
        v
 Apply similarity threshold
        |
        v
 Announce registered identity / unknown face
```

The two flows are documented separately because the Gemini scene-description script and face-recognition script have been developed and run as separate modes. Do not assume that both are started by one command unless a launcher has been added to the repository.

---

## Hardware and software

### Hardware

- Raspberry Pi 5
- Compatible Raspberry Pi camera module (the tested camera setup used an IMX219 sensor)
- microSD card with Raspberry Pi OS
- Raspberry Pi power supply
- Speaker or earphones
- Camera cable and other required connections
- Internet connection for Gemini and Sarvam API calls

### Software environment recorded during development

| Component | Working / recorded environment |
|---|---|
| Board | Raspberry Pi 5 |
| Operating system | Debian GNU/Linux 13 (Trixie) / Raspberry Pi OS environment |
| Architecture | 64-bit ARM (`aarch64`) |
| Python | Python 3.13.x (3.13.5 recorded) |
| OpenCV | 4.13.0 recorded |
| Camera library | Picamera2 / libcamera |
| Scene understanding | Google Gemini API (`gemini-flash-lite-latest`) |
| Speech | Sarvam AI (`sarvamai`) and `aplay` |
| Face detection | YuNet ONNX model |
| Face recognition | SFace ONNX model |

Versions may differ on another Raspberry Pi image. Use the commands below to inspect the actual environment before changing packages.

---

## Project structure

The following is the logical structure based on the modules and model files used during development. Keep your repository's actual filenames if they differ; in particular, the face-database enrollment script name was not confirmed in the available project notes.

```text
SightSense/
├── live_gemini.py                 # Live camera + Gemini scene description
├── live_face_voice.py             # Live face detection/recognition mode
├── speech.py                      # Sarvam AI speech generation and playback
├── translator.py                  # Optional translation helper / experiments
├── .env                           # API keys (never commit this file)
├── venv/                          # Python virtual environment (not committed)
└── face_models/
    ├── face_detection_yunet_2023mar.onnx
    ├── face_recognition_sface_2021dec.onnx
    └── face_database.npz           # Registered face names and feature data
```

Other files, test scripts, logs or model files may exist in your local checkout. Add them to this tree when you confirm their names.

---

## Requirements

- Raspberry Pi 5 running a compatible 64-bit Raspberry Pi OS / Debian-based system.
- Camera supported by `libcamera` and Picamera2.
- Working speaker/audio output.
- Internet access for cloud-based Gemini and Sarvam features.
- A Google Gemini API key.
- A Sarvam AI API key.
- YuNet and SFace ONNX model files for face-recognition mode.

## Installation

### 1. Update Raspberry Pi OS

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Reconnect to the Raspberry Pi after it restarts.

### 2. Install system packages

Picamera2 and camera support are best installed through the Raspberry Pi OS package manager.

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip python3-picamera2 python3-opencv python3-numpy python3-pil alsa-utils
```

If your OS image uses a different package name or already has a package installed, check with `apt policy <package-name>` before changing the environment.

### 3. Clone or open the project

If the project is already on the Raspberry Pi:

```bash
cd ~/SightSense
```

If it is hosted in a Git repository, clone it using your repository URL:

```bash
git clone <YOUR_REPOSITORY_URL> SightSense
cd SightSense
```

Replace `<YOUR_REPOSITORY_URL>` with the actual repository URL.

### 4. Create and activate the virtual environment

Picamera2 is installed as a system package on Raspberry Pi OS. Create the virtual environment with access to system-installed packages:

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

### 5. Install Python packages

The following packages correspond to the imports and services recorded for the working Gemini/speech implementation:

```bash
pip install python-dotenv google-genai Pillow sarvamai
```

Check that OpenCV and Picamera2 are visible from the activated environment:

```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "from picamera2 import Picamera2; print('Picamera2 import OK')"
```

If either import fails, verify that the virtual environment was created with `--system-site-packages` and that the relevant Raspberry Pi OS package is installed. Avoid installing a second, conflicting OpenCV wheel before checking the system package.

### 6. Install face-recognition model files

The face-recognition code expects these ONNX model files:

```text
face_models/face_detection_yunet_2023mar.onnx
face_models/face_recognition_sface_2021dec.onnx
```

Create the directory if it does not exist:

```bash
mkdir -p face_models
```

Place the YuNet and SFace ONNX files in that directory. The filenames must match the paths used by `live_face_voice.py` (or update the paths in the script if your filenames differ).

---

## Configuration

### 1. Create the `.env` file

From the project root:

```bash
nano .env
```

Add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
```

Replace the example values with your own keys. Do not add quotation marks unless your code specifically expects them.

Save in nano with `Ctrl + O`, press `Enter`, then exit with `Ctrl + X`.

### 2. Protect API keys

Add the following entries to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

Never upload `.env`, API keys, private face data or personal recordings to a public repository.

### 3. Verify the API keys

```bash
source venv/bin/activate
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('GEMINI_API_KEY:', 'loaded' if os.getenv('GEMINI_API_KEY') else 'missing'); print('SARVAM_API_KEY:', 'loaded' if os.getenv('SARVAM_API_KEY') else 'missing')"
```

This prints only whether each key is present; it does not expose the key values.

---

## Run SightSense

Run commands from the project root (`~/SightSense`). Activate the virtual environment before starting a script.

### Mode 1: Live surroundings description with Gemini

```bash
cd ~/SightSense
source venv/bin/activate
python live_gemini.py
```

The script initializes Picamera2, captures frames at 640 × 480, sends image input to the configured Gemini model (`gemini-flash-lite-latest`) and passes the generated description to `speech.py` for spoken output.

Press `Ctrl + C` in the terminal to stop the script.

### Mode 2: Face detection and recognition

```bash
cd ~/SightSense
source venv/bin/activate
python live_face_voice.py
```

This mode requires both ONNX model files and a correctly prepared `face_models/face_database.npz` database. Press `Ctrl + C` to stop it.

**Face database note:** The database used by the project stores registered names and face feature data. The exact enrollment script/command is not confirmed here, so this README does not invent one. Use the enrollment code already present in your checkout to create or update `face_database.npz` before starting recognition.

### Run the two modes

Run one mode at a time unless the scripts have been explicitly designed to share the camera and audio resources. Both modes may attempt to access the same camera and speaker.

---

## Face recognition setup

### Model files

| File | Purpose |
|---|---|
| `face_detection_yunet_2023mar.onnx` | Detects face locations using YuNet |
| `face_recognition_sface_2021dec.onnx` | Extracts face features using SFace |
| `face_database.npz` | Stores registered identities and corresponding face data |

### Recorded recognition settings

The face-recognition implementation has used the following starting values:

```python
WIDTH, HEIGHT = 640, 480
MATCH_THRESHOLD = 0.45
ANNOUNCEMENT_COOLDOWN = 5
NO_FACE_RESET_SECONDS = 3
```

These values are implementation settings, not guaranteed accuracy levels. Tune and validate them using consenting test participants and different lighting, camera distances and angles. Do not rely on a face match as a security or identity-verification mechanism.

---

## Useful Raspberry Pi commands

### Check Python and platform

```bash
python3 --version
uname -m
cat /etc/os-release
```

### Check camera detection

```bash
rpicam-hello --list-cameras
```

On older images, the camera utility may be named `libcamera-hello`. If neither command exists, check whether the Raspberry Pi camera applications are installed.

### Check Picamera2

```bash
source ~/SightSense/venv/bin/activate
python -c "from picamera2 import Picamera2; cam = Picamera2(); print(cam.global_camera_info())"
```

### Check OpenCV

```bash
source ~/SightSense/venv/bin/activate
python -c "import cv2; print(cv2.__version__); print('YuNet:', hasattr(cv2, 'FaceDetectorYN')); print('SFace:', hasattr(cv2, 'FaceRecognizerSF'))"
```

### Check audio output

```bash
aplay -l
```

### Check project files

```bash
cd ~/SightSense
ls -la
find . -maxdepth 2 -type f -not -path './venv/*' -not -path './.git/*'
```

### Activate / deactivate the environment

```bash
cd ~/SightSense
source venv/bin/activate
```

When finished:

```bash
deactivate
```

### Stop a running program

In the terminal where the script is running:

```text
Ctrl + C
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'cv2'`

Check whether OpenCV is installed and visible to the virtual environment:

```bash
sudo apt install -y python3-opencv
source ~/SightSense/venv/bin/activate
python -c "import cv2; print(cv2.__version__)"
```

If the environment was created without system package access, recreate it (only after preserving any project-specific packages):

```bash
cd ~/SightSense
deactivate 2>/dev/null || true
rm -rf venv
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install --upgrade pip
pip install python-dotenv google-genai Pillow sarvamai
```

### `ModuleNotFoundError: No module named 'picamera2'`

Install Picamera2 through apt and make sure the virtual environment can see system packages:

```bash
sudo apt install -y python3-picamera2
```

Then recreate the environment with `--system-site-packages` if necessary.

### Camera opens but no frame is returned

A camera device opening successfully does not always mean that a frame is available. Check the camera is detected and test Picamera2 independently:

```bash
rpicam-hello --list-cameras
```

```bash
python -c "from picamera2 import Picamera2; c=Picamera2(); c.start(); f=c.capture_array(); print('Frame:', None if f is None else f.shape); c.stop()"
```

Check the ribbon cable orientation and connection, camera compatibility, and whether another program is already using the camera. Prefer Picamera2 for the Raspberry Pi camera rather than assuming `cv2.VideoCapture(0)` will return frames.

### `FaceDetectorYN` or `FaceRecognizerSF` is missing

Check the OpenCV build:

```bash
python -c "import cv2; print(cv2.__version__); print(hasattr(cv2, 'FaceDetectorYN')); print(hasattr(cv2, 'FaceRecognizerSF'))"
```

The face module requires an OpenCV build that exposes these APIs. Confirm the installed Raspberry Pi OS OpenCV package/build before replacing it with another package.

### ONNX model file not found

Confirm that both model files exist at the paths expected by the script:

```bash
ls -lh ~/SightSense/face_models/
```

Check spelling and capitalization. Linux paths are case-sensitive.

### Gemini API key missing or API request fails

Confirm `.env` is in the project root and contains `GEMINI_API_KEY`. Verify internet access and that the API key is active and permitted to use the configured Gemini model.

### Sarvam speech does not play

Check that `SARVAM_API_KEY` is present, `sarvamai` is installed, audio output is connected, and `aplay` is available:

```bash
python -c "import sarvamai; print('Sarvam package import OK')"
aplay -l
```

### Translation requests fail or are rate-limited

The optional translation module has previously encountered service rate limits. Avoid making repeated requests for identical text; use caching and request throttling where implemented. Translation may also require network access or a downloaded language model.

---

## Limitations and future improvements

- Gemini scene descriptions and Sarvam speech require internet connectivity and valid API credentials.
- Cloud response time can vary with network quality and service availability.
- The system may fail to detect small, distant, occluded or poorly lit objects.
- Face recognition can produce false matches or fail to recognize a registered person.
- Speech output can be difficult to hear in noisy environments.
- Translation quality and supported languages depend on the selected service and configuration.
- The current scripts are separate modes; a unified launcher and shared resource manager would be a future improvement.
- The prototype must be evaluated for latency, detection quality, reliability and usability before any real-world assistive use.

Possible future work:

1. Add a unified menu or launcher for surroundings description and face-recognition modes.
2. Add a documented face enrollment utility and database backup workflow.
3. Improve offline operation and reduce dependence on cloud services where practical.
4. Add obstacle-distance estimation and carefully validated directional audio cues.
5. Measure precision, recall, response time and frame rate in controlled scenarios.
6. Conduct usability testing with informed consent and appropriate institutional approval.

---

## Development notes

This README records the implementation details and commands that were available from the SightSense development history. Confirm the exact filenames, dependency versions, face-database enrollment procedure and any additional scripts against the current repository before publishing. Do not commit API keys, registered face data or private test images.

## License

Add the license selected by the project team. Do not claim a license until one has been chosen and added to the repository.
