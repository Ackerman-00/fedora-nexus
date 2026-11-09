You are the model-ranking turn of this repository's scheduled run. Work fast
(under 10 minutes) and change exactly one file: tools/model-rank.txt.

1. Search the web for today's strongest FREE coding models on OpenCode Zen.
   Queries to try: "opencode zen free coding models <month> <year>",
   "artificial analysis coding index <month> <year>", "<model> coding
   benchmark free". Prefer independent published scores over vendor claims; a
   model with no independent score ranks below one that has a score.
2. Read the committed order in tools/model-rank.txt and the live catalog:
   curl -sS https://opencode.ai/inference/v1/models
3. Rewrite tools/model-rank.txt: one model id per line, grouped in tiers,
   each model preceded by a single `#` line with its score, its source and
   today's UTC date. The strongest free model goes first. Keep the owner veto
   (glm-5.3-flash-free, jev-1.13-free) out of the file, drop ids the catalog no
   longer serves, and give every new free id a tier.
4. Do not commit. Do not touch any other file, no tests, no summaries.
5. Print one final line and nothing after it:

model-rank: <leader-id> first - <sources you checked>, checked <YYYY-MM-DD>
