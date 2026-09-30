"""Single-camera face and QR inference; reconstructed, hardware validation pending."""
import argparse
import logging
import math
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from .matching import match_identity
from .gallery import load_gallery


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery", type=Path, required=True)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--cooldown", type=float, default=5.0)
    parser.add_argument("--speak", action="store_true")
    parser.add_argument("--headless", action="store_true", help="disable the preview window; stop with Ctrl+C")
    parser.add_argument("--max-frames", type=int, default=0, help="stop after N frames; 0 runs continuously")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if not math.isfinite(args.threshold) or args.threshold <= 0:
        parser.error("threshold must be finite and positive")
    if not math.isfinite(args.cooldown) or args.cooldown < 0:
        parser.error("cooldown must be finite and nonnegative")
    if args.max_frames < 0 or args.camera < 0:
        parser.error("camera and max-frames must be nonnegative")
    try:
        records = load_gallery(args.gallery)
    except ValueError as error:
        parser.error(str(error))
    try:
        import cv2
        import face_recognition
        from pyzbar.pyzbar import decode
    except ImportError as error:
        parser.error(f"vision dependencies unavailable: {error}. Install the vision extra and ZBar.")
    executable = shutil.which("espeak") if args.speak else None
    if args.speak and executable is None:
        parser.error("eSpeak executable not found")
    events = queue.Queue(maxsize=4)
    worker = None
    if executable:
        worker = threading.Thread(target=speech_worker, args=(events, executable), daemon=True)
    last_spoken = {}

    def announce(key, message):
        now = time.monotonic()
        if now - last_spoken.get(key, -math.inf) < args.cooldown:
            return
        if executable:
            try:
                events.put_nowait(message)
            except queue.Full:
                logging.debug("Speech queue full; dropped announcement")
                return
        last_spoken[key] = now
        if len(last_spoken) > 256:
            oldest = min(last_spoken, key=last_spoken.get)
            del last_spoken[oldest]
        logging.info("%s", message)
    camera = cv2.VideoCapture(args.camera)
    try:
        if not camera.isOpened():
            raise RuntimeError("camera could not be opened")
        if worker:
            worker.start()
        processed = 0
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
            processed += 1
            if not args.headless:
                cv2.imshow("Assistive Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            if args.max_frames and processed >= args.max_frames:
                break
    except KeyboardInterrupt:
        logging.info("Stopped by user")
    except (RuntimeError, cv2.error) as error:
        parser.error(str(error))
    finally:
        camera.release()
        if not args.headless:
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                logging.debug("Preview cleanup unavailable")
        if worker and worker.ident is not None:
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
