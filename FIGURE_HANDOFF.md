# Commit After Sanitization Figure Handoff

Current story lock:

- canonical Qwen anchor is benchmark-closed
- calibrated recovery, not universal positive transfer
- `commit_cfguard` is the safer commitment-family variant on the canonical anchor

Priority order:

1. state-machine comparison: `commit_old` vs `commit_repair`
2. threat-model / defense overview
3. canonical task10 main-results figure or styled table
4. mechanism ablation: `commit_repair` vs `sanitize_only`

Current quantitative anchors:

- `7B none`: attack rate `10.20%`
- `7B commit_repair`: original rate `79.71%`, recommit `360`
- `7B commit_cfguard`: original rate `80.39%`, recommit `360`
- `7B commit_sanitize_only`: original rate `70.59%`, recommit `0`
- `14B none`: attack rate `10.39%`
- `14B commit_repair`: original rate `84.31%`, recommit `360`
- `14B commit_cfguard`: original rate `86.27%`, recommit `360`
- `14B commit_sanitize_only`: original rate `86.27%`, recommit `0`

Must preserve in captions and design:

- persistent memory poisoning is real
- recommit is a real extra control decision
- utility is family-dependent even when recommit is reachable

Must avoid:

- `commit_repair` is uniformly better
- non-Qwen generalization language
- SOTA / leaderboard framing
