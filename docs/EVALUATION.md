# Evaluation protocol

## Evidence currently available

| Metric | June 2025 report observation | Verification status |
|---|---|---|
| Face recognition latency | <1 s ideal light; 1.5–2 s difficult light | Author-reported, logs unavailable |
| QR decoding latency | 0.5–1 s | Author-reported, logs unavailable |
| QR working distance | 10–30 cm | Author-reported |
| Ultrasonic range | 30 cm–3 m | Author-reported |
| Integrated response | <2 s | Author-reported; timing endpoints unclear |
| Battery duration | 4–5 h | Author-reported; battery specification absent |

The report also discusses 85% confidence and 60–70% thresholds. Its provided embedding code does not establish how those percentages were calculated. Do not relabel them as test accuracy or convert them into embedding distances.

## Required experimental procedure

1. Collect consent-based identities across separate capture sessions. Keep enrollment and evaluation images disjoint.
2. Include unenrolled people to assess open-set errors. Calibrate threshold on a validation split, then freeze it before test evaluation.
3. Record camera resolution, Raspberry Pi model, OS, dependency versions, enrollment counts, lighting, distance, occlusion, and run IDs.
4. Measure detection recall, known-person identification accuracy, false acceptance of unknown people, and false rejection of known people. Report sample counts and denominators.
5. Measure frame processing p50/p95 latency, audio onset latency, dropped audio events, FPS, CPU, memory, and warm-up behavior.
6. Evaluate QR success rate across payload types, lighting, angles, and distances. Report ultrasonic error against a reference distance with sensor timeout events.
7. Publish aggregate results and reproducible scripts; retain biometric inputs privately.

No raw benchmark results are included. Automated tests cover identity matching, malformed galleries, CLI errors, and simulated camera cleanup/headless behavior. They do not validate model accuracy, audio latency, accessibility, or hardware reliability.
