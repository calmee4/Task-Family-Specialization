# MemoryGuard Figure Handoff

Current story lock:

- mechanism-first draft
- not benchmark-final
- do not imply leaderboard closure

Priority order:

1. state-machine comparison: `commit_old` vs `commit_repair`
2. threat-model / defense overview
3. canonical task10 main-results figure or styled table
4. mechanism ablation: `commit_repair` vs `sanitize_only`

Current quantitative anchors:

- `7B none`: attack rate `10.20%`
- `7B commit_repair`: original rate `70.54%`, recommit `360`
- `7B commit_sanitize_only`: original rate `70.59%`, recommit `0`
- `14B none`: attack rate `8.32%`
- `14B commit_repair`: original rate `77.78%`, recommit `197`
- `14B commit_sanitize_only`: original rate `80.78%`, recommit `0`

Must preserve in captions and design:

- persistent memory poisoning is real
- recommit is a real extra control decision
- current table is not denominator-aligned

Must avoid:

- `commit_repair` is the strongest defense
- benchmark-final language
- SOTA / leaderboard framing
