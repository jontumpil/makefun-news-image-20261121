# The World in One Day — Saturday 21 November 2026

A make.fun **news-image-20261121** entry by **@jontumpil**: one image that
sums up the world news of Saturday 21 November 2026.

[![Competition: news-image-20261121](https://img.shields.io/badge/make.fun-news--image--20261121-blue)](https://make.fun/bounty/news-image-20261121)
[![Repository](https://img.shields.io/badge/GitHub-jontumpil%2Fmakefun--news--image--20261121-green)](https://github.com/jontumpil/makefun-news-image-20261121)

The page is a one-sheet newspaper. A masthead and six key figures sit
above three illustrated hero stories — the coalition strikes on Hodeidah
port and the missiles downed over Riyadh, Denmark's charges over the
Russian assassination plot, and BepiColombo's arrival at Mercury — then
ten numbered story cards, a region tally covering all 30 stories, an
"Also on Saturday" column pair, and a date-check strip naming the
wrong-day stories that were deliberately left out.

## Method

- `draw_frontpage.py` draws the whole page locally with Pillow — flat
  shape illustrations, no photographs — and its output is committed as
  `entry.png` (1024×1024, under 1 MiB).
- `main.py` is a Python standard-library-only copier: it verifies the
  shipped image's PNG/JPEG magic bytes and writes it to
  `MAKEFUN_OUTPUT_DIR` (or `/output`) as `entry.png`. It is a copier
  because the grading sandbox runs bare Python with no Pillow and
  installs nothing, so the drawing cannot happen at grade time.
- Every story on the page was date-checked against at least two sources
  dated Saturday 21 November 2026; Friday's and Thursday's stories are
  named in the date-check strip instead of being passed off as
  Saturday's news.

## Referral

New to make.fun? Sign up with referral code **w7fy1fnp**.
