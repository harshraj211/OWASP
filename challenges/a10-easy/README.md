# A10 Easy: Information Disclosure Through Concurrency Exceptions (QuantEdge Capital)

### Category: OWASP Top 10:2025 - A10 Mishandling of Exceptional Conditions
* **Difficulty:** Easy (Hard-Calibrated Race Condition & Memory Reconstruction)
* **Default Port:** 6028
* **Target Category:** A10:2025 – Mishandling of Exceptional Conditions

---

### Challenge Description
QuantEdge Capital operates a high-frequency algorithmic risk optimization platform. Data analysts submit portfolio covariance factors and matrix partition hints to compute volatility curves via `/api/v1/matrix/optimize` or `/portfolio`.

Under the hood, matrix worker threads utilize an unsynchronized shared memory partition (`SharedWorkerState.active_slice_ref`) referenced by the nested configuration parameter `matrix_config.worker_slice_ref`.

When requests are sent sequentially, the computation executes smoothly without disclosure. However, when two concurrent requests hit the worker thread with conflicting slice references simultaneously, an unhandled dirty-read race condition occurs (`WorkerMemoryCollisionException`).

Because the platform fails to safely catch this concurrency fault, the resulting stack trace exposes an unhandled register memory slice truncated to exactly **8 bytes** per hit. To retrieve the 32-character confidential master key, students must develop a concurrent racing harness to repeatedly collide conflicting worker slices across offsets `0x00`, `0x08`, `0x10`, and `0x18`, assemble the key, and authenticate against the confidential vault.

### Objective
1. Inspect the matrix optimization endpoint and uncover the nested `matrix_config.worker_slice_ref` parameter.
2. Develop a multi-threaded Python race script to send overlapping requests with conflicting slice references.
3. Trigger `WorkerMemoryCollisionException` crashes and harvest the 8-byte memory fragments from the stack trace dumps.
4. Assemble the four 8-byte chunks into the 32-character master key.
5. Authenticate against `/api/v1/internal/confidential-vault?token=<RECONSTRUCTED_KEY>` to retrieve the dynamic flag.
