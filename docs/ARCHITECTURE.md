# Architecture and implementation decisions

## Original project block diagram

![Camera, face recognition, QR decoding, ultrasonic distance detection, and speech output in the smart glasses system](assets/system-block-diagram-dark.svg)

The team-supplied diagram documents the academic system design. Its "Object Detection" branch uses an ultrasonic sensor to trigger proximity alerts. The reference implementation below covers camera-based recognition and decoding; the sensor adapter is still pending.

## ML pipeline

Enrollment decodes a private image, converts OpenCV BGR to RGB, detects exactly one face with the HOG backend, and extracts a 128-value pretrained dlib embedding. A JSON gallery maps vectors to identity labels. JSON replaces the report's pickle format to avoid executable deserialization of model metadata.

Inference applies the same color conversion and feature extraction. Euclidean nearest-neighbor matching selects an enrolled sample, then rejects distances exceeding a configured threshold. This differs from the report's multiple-match identity voting; it is a documented reconstruction choice. Distance is a similarity proxy, not calibrated confidence or accuracy.

## Runtime boundaries

One frame source serves both recognition and Pyzbar decoding. Camera capture and inference are synchronous. Only speech playback runs in a background thread, with a bounded queue and repeat cooldown. Slow vision processing can still reduce frame throughput; concurrency alone is not a latency guarantee.

The application targets an OpenCV-compatible USB camera, with optional preview or `--headless` execution. A frame limit supports bounded smoke checks. CSI integration, GPIO proximity alerts, original GUI modes, email alerts, and semantic object detection are not implemented here.

## Report code issues addressed

- Inference BGR/RGB mismatch: explicit RGB conversion.
- Pickle artifacts: non-executable JSON gallery.
- Multiple functions opening the same camera: shared capture stream.
- Blocking speech in inference: bounded asynchronous speech worker.
- Shell command audio playback: argument-list subprocess invocation.
- Unbounded repeated announcements: cooldown and bounded event bookkeeping.

These engineering improvements belong to this reconstruction and should not be presented as verified features of the original academic code.
