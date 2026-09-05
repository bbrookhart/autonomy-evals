# Current limitations
No real-model results or human labels are supplied. Mock fixtures prove execution only and intentionally have constant scores. No judge calibration, successful pilot, or validated composite is claimed.

Thirty base scenarios are a small convenience sample. Heldout leaves the pilot with fewer than 30. Topics are one-to-one with base cases, limiting random-effect decomposition. Confidence/validation are crossed, but update timing and escalating pressure are fixed. Values updates often change feasibility rather than contradict a personal preference; report separately.

Semantic scores require LLM or human judgment. Deterministic counts are not truth detectors. Blind labels cannot conceal all style cues. Grader calibration and controlled verbosity/hedging/family diagnostics require separate execution. Independent model families do not guarantee independent biases.

Provider SDKs, current model availability, credentials and API behavior need live smoke testing. Character-based token estimation is approximate; missing prices and usage remain unknown. Failed request billing may not be available. Resume avoids regenerating saved turns but cannot guarantee exactly-once remote billing if a process dies after receiving an API answer and before its checkpoint write.

Native Inspect task and canonical CLI have different artifact formats. CLI gives portable full scoring/reporting; native task currently provides conversation logs and deterministic surface diagnostics. Reports do not convert native logs automatically.
