"""Single-camera face and QR inference; reconstructed, hardware validation pending."""
import argparse
import json
import logging
import math
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from .matching import match_identity


def speech_worker(events, executable):
    while True:
        message = events.get()
        try:
            if message is None:
                return
            try:
                subprocess.run([executable, "--", message[:300]], check=True, timeout=20,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except (OSError, subprocess.SubprocessError) as error:
                logging.warning("Speech failed: %s", error)
        finally:
            events.task_done()


def main():
    import cv2
    import face_recognition
    from pyzbar.pyzbar import decode

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery", type=Path, required=True)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--cooldown", type=float, default=5.0)
    parser.add_argument("--speak", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if not math.isfinite(args.threshold) or args.threshold <= 0:
        parser.error("threshold must be finite and positive")
    if not math.isfinite(args.cooldown) or args.cooldown < 0:
        parser.error("cooldown must be finite and nonnegative")
    gallery = json.loads(args.gallery.read_text(encoding="utf-8"))
    records = gallery["records"]
    if gallery.get("schema_version") != 1 or not records:
        parser.error("expected a nonempty schema version 1 gallery")
    match_identity([0.0] * 128, records, args.threshold)
    executable = shutil.which("espeak") if args.speak else None
    if args.speak and executable is None:
        parser.error("eSpeak executable not found")
    events = queue.Queue(maxsize=4)
    worker = None
    if executable:
        worker = threading.Thread(target=speech_worker, args=(events, executable), daemon=True)
        worker.start()
    last_spoken = {}

    def announce(key, message):
        now = time.monotonic()
        if now - last_spoken.get(key, -math.inf) < args.cooldown:
            return
        last_spoken[key] = now
        if len(last_spoken) > 256:
            oldest = min(last_spoken, key=last_spoken.get)
            del last_spoken[oldest]
        logging.info("%s", message)
        if executable:
            try:
                events.put_nowait(message)
            except queue.Full:
                logging.debug("Speech queue full; dropped stale announcement")

    camera = cv2.VideoCapture(args.camera)
    try:
        if not camera.isOpened():
            raise RuntimeError("camera could not be opened")
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("camera frame capture failed")
            height, width = frame.shape[:2]
            frame = cv2.resize(frame, (500, max(1, round(height * 500 / width))))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            embeddings = face_recognition.face_encodings(rgb, boxes)
            for (top, right, bottom, left), embedding in zip(boxes, embeddings):
                name, distance = match_identity(embedding.tolist(), records, args.threshold)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 220, 100), 2)
                cv2.putText(frame, f"{name} d={distance:.3f}", (left, max(15, top - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 220, 100), 1)
                announce(("face", name), "Unknown person" if name == "Unknown" else f"Recognized {name}")
            for barcode in decode(frame):
                payload = barcode.data.decode("utf-8", errors="replace")[:300]
                payload = " ".join(payload.split())
                announce(("code", payload), f"Code reads: {payload}")
            cv2.imshow("Assistive Vision", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        if worker:
            # Drop queued stale messages and request worker shutdown.
            while True:
                try:
                    events.get_nowait()
                    events.task_done()
                except queue.Empty:
                    break
            events.put_nowait(None)
            worker.join(timeout=21)


if __name__ == "__main__":
    main()
