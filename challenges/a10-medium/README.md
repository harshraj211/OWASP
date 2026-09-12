# A10 Medium: Unhandled Exception Denial of Service / Fail-Open (Synapse SCADA Grid)

### Category: OWASP Top 10:2025 - A10 Mishandling of Exceptional Conditions
* **Difficulty:** Medium (Very Difficult Level)
* **Default Port:** 6029
* **Concept:** Telemetry Parser Exception, Daemon Crash, Fail-Open Emergency Bypass

---

### Challenge Description
Synapse SCADA oversees high-voltage regional power grid telemetry. Substation feeder bus controls and the Emergency Core are guarded by an automated Safety Interlock Daemon. Under normal conditions, manual access to the Emergency Core is strictly forbidden.

However, to prevent total regional grid collapse in the event of software exceptions, the supervisor implements a "Fail-Safe Emergency Override" protocol: whenever an unhandled exception occurs in the sensor ingestion analyzer, all safety interlocks fail open for 60 seconds.

### Objective
1. Inspect the Telemetry Ingestion endpoint at `/grid/telemetry`.
2. Craft a malformed sensor JSON frame (e.g. invalid type in the `harmonics` calculation array) to trigger an unhandled exception in the safety daemon.
3. Observe the crash and the activation of the 60-second fail-open emergency bypass.
4. Immediately navigate to `/core/override` to extract the dynamic flag.
