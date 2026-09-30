# Hardware integration

Documented components: Raspberry Pi 4, Raspberry Pi/USB camera, HC-SR04, speaker/earphones, portable power source, and wearable frame.

## Resolve wiring before integration

The report's wiring table gives TRIG GPIO23 / ECHO GPIO24, while its Combined.py assigns TRIG=24 / ECHO=23. Both use BCM numbering. Confirm actual wiring before adding a GPIO adapter; there is no validated default pin assignment in this reconstruction.

The report describes a 50 cm alert threshold in evaluation but uses 15 cm in one code excerpt. Make the operational threshold explicit and assess it experimentally.

HC-SR04 ECHO requires suitable voltage conditioning for Raspberry Pi GPIO. Confirm electrical compatibility and pinout against component documentation before connecting the sensor. The reference package intentionally contains no wiring-ready GPIO script.

## Adapter requirements

A future sensor adapter should return distance or a typed timeout error, impose deadlines on both echo edges, use monotonic timing, clean up GPIO resources, and arbitrate obstacle alerts ahead of noncritical speech. Do not reproduce the report's unlimited GPIO polling loops.

Use `distance_cm = echo_duration_seconds * speed_of_sound_cm_per_second / 2`; specify the environmental assumption for speed of sound. Invalid or timed-out readings must not be interpreted as a clear path.
