"""Dependency-free Euclidean nearest-neighbor identity matching."""
import math


def match_identity(query, records, threshold=0.6):
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be finite and positive")
    if len(query) != 128 or not all(math.isfinite(x) for x in query):
        raise ValueError("expected 128 finite embedding values")
    best_name, best_distance = "Unknown", math.inf
    for record in records:
        vector = record["embedding"]
        if len(vector) != 128 or not all(math.isfinite(x) for x in vector):
            raise ValueError("invalid enrolled embedding")
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(query, vector)))
        if distance < best_distance:
            best_name, best_distance = record["name"], distance
    return (best_name if best_distance <= threshold else "Unknown", best_distance)
