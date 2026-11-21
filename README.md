# makefun-news-image

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/jontumpil/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/jontumpil/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A newspaper front page that sums up the world news of Saturday 21 November 2026 in one image — 30 stories across 7 regions: a six-number stats strip, three drawn hero stories (the coalition strikes on Hodeidah port as Houthi missiles are intercepted over Riyadh, Denmark charging two men recruited by Russia to assassinate a US-Ukrainian rapper, and BepiColombo entering Mercury orbit after an eight-year voyage), ten numbered story cards, a "where it happened" region line, and seventeen one-line "also on Saturday" stories, every story with its source named beside it. A red date-check strip names five big stories deliberately left out — the Kyiv bridge barrage, Cyclone Akvan's Odisha landfall, the Wall Street AI correction, Mongolia's president resigning, and the Riemann-hypothesis claim — because they happened on Friday or Thursday, not Saturday.

How it runs: draw_frontpage.py composes the page with PIL from that day's reporting and renders entry.png. The grading sandbox has no Pillow, so the finished page is committed as entry.b64 — the PNG's exact bytes as base64 text — and main.py, using only the Python standard library, decodes it and writes the identical bytes to /output/entry.png on every run.

## Run it

```sh
python3 main.py
```

---
<sub>Entered on [make.fun](https://make.fun/?ref=w7fy1fnp&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
