# A10 Medium: Multi-Node Consensus State Machine Desynchronization (Synapse SCADA Grid)

### Category: OWASP Top 10:2025 - A10 Mishandling of Exceptional Conditions
* **Difficulty:** Medium (10/10 Calibrated)
* **Default Port:** 6029
* **Concept:** Mathematical Domain Exception, Stage 2 Ingestion Crash, Multi-Node Quorum Collapse & Fail-Open Bypass

---

### Challenge Description
Synapse SCADA oversees a high-voltage regional power transmission grid. Substation feeder lines and the Emergency Core circuit are safeguarded by a **Triple Modular Redundancy (TMR)** consensus engine consisting of three distributed telemetry ingestion daemons:
- `Node-Alpha` (500kV Main Bus)
- `Node-Beta` (230kV Thermal Feeder)
- `Node-Gamma` (Tie-Line Intertie)

Under nominal conditions, physical breaker interlocks are strictly maintained as long as a quorum of at least **2 out of 3 nodes** is healthy.

When telemetry frames are received via `POST /grid/telemetry` or `POST /api/v1/telemetry/submit`, the ingestion pipeline performs two stages:
1. **Stage 1 (Schema Validation):** Validates that all fields are numeric floating-point values. Standard non-numeric or string injection attempts are cleanly trapped and rejected with HTTP 400.
2. **Stage 2 (Grid Physics Stability Engine):** Calculates the Surge Impedance Loading (SIL) stability index:
   $$\text{SIL} = \frac{\sqrt{V^2 - 25 \cdot Q}}{P}$$

### The Vulnerability
The mathematical evaluation in Stage 2 lacks defensive domain checks and exception recovery. Submitting valid numeric inputs that violate mathematical domain invariants (such as active power $P = 0$ causing `ZeroDivisionError`, or $25Q > V^2$ causing negative radical `ValueError`) triggers an unhandled exception inside the worker thread.

When a node experiences an unhandled mathematical exception, its daemon crashes into a quarantined `FAULT` state for **20 seconds** before a watchdog supervisor re-initializes it.

Because consensus requires 2 healthy nodes, crashing a single node degrades the quorum to 2/3, which still holds the interlocks. However, if an attacker coordinates unhandled crashes across **at least 2 nodes** within the 20-second watchdog recovery window, the consensus engine experiences an unhandled `QuorumLossException`. Due to an insecure fail-open emergency grid preservation routine, all physical interlocks disengage, unlocking `/core/override` and releasing the system flag.

### Objective
1. Inspect `/substations`, `/system/safety-interlock`, and `/grid/telemetry`.
2. Discover the Stage 2 mathematical calculation and identify numeric boundary inputs that trigger unhandled exceptions (e.g., $P = 0$ or $25Q > V^2$).
3. Develop an automated exploit script to send crash frames to both `Node-Alpha` and `Node-Beta` within their 20-second recovery window.
4. With quorum collapsed (<2 healthy nodes), request `/core/override` to retrieve the dynamic flag.
