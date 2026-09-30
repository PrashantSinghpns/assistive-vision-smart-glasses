"""Generate a JSON embedding gallery from a private enrollment directory."""
import argparse
import json
import logging
from pathlib import Path


def main():
    import cv2
    import face_recognition

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if not args.dataset.is_dir():
        parser.error("dataset directory does not exist")
    records = []
    for path in sorted(args.dataset.glob("*/*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        image = cv2.imread(str(path))
        if image is None:
            logging.warning("Unreadable image: %s", path)
            continue
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model="hog")
        if len(locations) != 1:
            logging.warning("Expected one face, found %d: %s", len(locations), path)
            continue
        embedding = face_recognition.face_encodings(rgb, locations)[0]
        records.append({"name": path.parent.name, "embedding": embedding.tolist()})
    if not records:
        parser.error("no valid enrollment images")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"schema_version": 1, "records": records}), encoding="utf-8")
    logging.info("Saved %d embeddings", len(records))


if __name__ == "__main__":
    main()
