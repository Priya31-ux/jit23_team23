
import time
from pathlib import Path

import cv2
import numpy as np
from picamera2 import Picamera2
from speech import speak

BASE = Path.home() / "SightSense"
DETECTOR_PATH = BASE / "face_models" / "face_detection_yunet_2023mar.onnx"
RECOGNIZER_PATH = BASE / "face_models" / "face_recognition_sface_2021dec.onnx"
DATABASE_PATH = BASE / "face_models" / "face_database.npz"

WIDTH, HEIGHT = 640, 480

# Starting threshold only; test unknown people before relying on names.
MATCH_THRESHOLD = 0.45

# Avoid repeating the same spoken announcement too often.
ANNOUNCEMENT_COOLDOWN = 5
NO_FACE_RESET_SECONDS = 3


def main():
    data = np.load(DATABASE_PATH)
    names = data["names"].tolist()
    embeddings = data["embeddings"].astype(np.float32)

    detector = cv2.FaceDetectorYN.create(
        str(DETECTOR_PATH), "", (WIDTH, HEIGHT),
        score_threshold=0.85,
        nms_threshold=0.3,
        top_k=5000,
    )
    recognizer = cv2.FaceRecognizerSF.create(
        str(RECOGNIZER_PATH), ""
    )

    camera = Picamera2()
    camera.configure(
        camera.create_video_configuration(
            main={"size": (WIDTH, HEIGHT), "format": "RGB888"},
            buffer_count=2,
        )
    )

    last_spoken_label = None
    last_spoken_time = 0.0
    no_face_since = None

    try:
        camera.start()
        time.sleep(1)

        print("SightSense person recognition with Kannada voice is running.")
        print("Press Ctrl+C to stop.")

        while True:
            rgb = camera.capture_array()
            frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            detector.setInputSize((frame.shape[1], frame.shape[0]))
            _, faces = detector.detect(frame)

            label = None
            score = None

            if faces is not None and len(faces) > 0:
                # Select the largest face for this initial single-person test.
                face = max(faces, key=lambda f: f[2] * f[3])
                aligned = recognizer.alignCrop(frame, face)
                embedding = recognizer.feature(aligned).flatten()

                norm = float(np.linalg.norm(embedding))
                if norm > 1e-12:
                    embedding /= norm
                    scores = embeddings @ embedding
                    best_index = int(np.argmax(scores))
                    score = float(scores[best_index])

                    if score >= MATCH_THRESHOLD:
                        label = names[best_index]
                    else:
                        label = "Unknown"

                no_face_since = None
            else:
                if no_face_since is None:
                    no_face_since = time.monotonic()
                elif time.monotonic() - no_face_since >= NO_FACE_RESET_SECONDS:
                    last_spoken_label = None

            now = time.monotonic()

            if label is not None:
                print(f"Match: {label}, similarity: {score:.2f}")

                should_speak = (
                    label != last_spoken_label
                    or now - last_spoken_time >= ANNOUNCEMENT_COOLDOWN
                )

                if should_speak:
                    if label == "Sreepriya":
                        message = "ಮುಂದೆ ಸ್ರೀಪ್ರಿಯಾ ಇದ್ದಾರೆ."
                    elif label == "Unknown":
                        message = "ಮುಂದೆ ಒಬ್ಬ ವ್ಯಕ್ತಿ ಇದ್ದಾರೆ."
                    else:
                        message = f"ಮುಂದೆ {label} ಇದ್ದಾರೆ."

                    print("Speaking Kannada:", message)
                    speak(message, "Kannada")

                    last_spoken_label = label
                    last_spoken_time = time.monotonic()

            # Keep the processing loop from running unnecessarily fast.
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping person recognition...")

    finally:
        camera.stop()
        camera.close()
        print("Camera released. Stopped.")


if __name__ == "__main__":
    main()
