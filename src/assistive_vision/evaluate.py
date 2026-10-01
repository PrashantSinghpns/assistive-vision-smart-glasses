"""Evaluate known identities and unknown rejection using private held-out embeddings."""
import argparse
import json
import math
from pathlib import Path
from .gallery import load_gallery, validate_embedding
from .matching import match_identity

def evaluate(records, samples, threshold=0.6):
    if not isinstance(samples, list) or not samples:
        raise ValueError("Evaluation requires a nonempty sample list")
    names = {record["name"] for record in records}
    known = unknown = correct_known = wrong_known = rejected_known = accepted_unknown = 0
    for sample in samples:
        if not isinstance(sample, dict):
            raise ValueError("Samples must be JSON objects")
        expected = sample.get("expected")
        if not isinstance(expected, str) or (expected != "Unknown" and expected not in names):
            raise ValueError("Expected identity must be enrolled or exactly Unknown")
        validate_embedding(sample.get("embedding"))
        predicted, _ = match_identity(sample["embedding"], records, threshold)
        if expected == "Unknown":
            unknown += 1
            accepted_unknown += predicted != "Unknown"
        else:
            known += 1
            correct_known += predicted == expected
            rejected_known += predicted == "Unknown"
            wrong_known += predicted not in {expected, "Unknown"}
    return {"threshold": threshold, "samples": len(samples), "known_samples": known,
            "unknown_samples": unknown, "correct_known": correct_known,
            "wrong_known_identity": wrong_known, "rejected_known": rejected_known,
            "accepted_unknown": accepted_unknown,
            "known_identification_accuracy": correct_known / known if known else None,
            "known_rejection_rate": rejected_known / known if known else None,
            "unknown_false_acceptance_rate": accepted_unknown / unknown if unknown else None}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery", type=Path, required=True)
    parser.add_argument("--queries", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--output", type=Path, default=Path("outputs/matching_metrics.json"))
    args = parser.parse_args()
    if not math.isfinite(args.threshold) or args.threshold <= 0:
        parser.error("threshold must be finite and positive")
    try:
        report = evaluate(load_gallery(args.gallery), json.loads(args.queries.read_text(encoding="utf-8")), args.threshold)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
