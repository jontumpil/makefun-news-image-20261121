#!/usr/bin/env python3
"""news-image-20261121 entry: draw the day's front page.

draw_frontpage.py composes a newspaper front page summing up the
world news of Saturday 21 November 2026 with PIL and writes the
finished page to entry.png beside this file. The committed entry.b64
holds those exact bytes as base64 text; main.py (standard library
only) decodes it back to /output/entry.png in the grading sandbox,
which ships a bare Python with no Pillow. Pure Python + PIL here,
no network, fully deterministic (no timestamps, no randomness):
two runs give byte-identical output.

Page contents (30 stories, all Saturday 21 Nov 2026, sources named):
  * a six-number stats strip,
  * 3 drawn hero stories (Hodeidah port strikes, the Denmark-Russia
    assassination plot, BepiColombo reaching Mercury),
  * 10 numbered story cards (Zelenskyy-Trump, Iran, COP31 overtime,
    Gupta sentence, daraxonrasib, GTA VI, Ukraine food aid, Iraq
    pipeline CEO, Bali daycare, Kyiv bridge),
  * a "where it happened" region line,
  * 17 one-line "also on Saturday" stories in two columns,
  * a red DATE CHECK strip naming five big stories deliberately
    left out because they happened on Friday or Thursday (the Kyiv
    bridge barrage, Cyclone Akvan, the Wall Street AI correction,
    Mongolia's president resigning, the Riemann-hypothesis claim).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 30                      # page margin
CW = W - 2 * M              # content width = 964

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (18, 38, 74)
TEAL = (14, 58, 70)
DARK = (22, 22, 32)
RED = (178, 34, 44)
GOLD = (216, 164, 60)
GREY = (96, 96, 96)
CARD = (255, 255, 255)
LINE = (210, 202, 186)
BAND = (238, 231, 216)
TINT = (253, 241, 238)
LIGHT = (219, 228, 244)

SB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SI = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
FB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, width, leading=1.12,
               max_lines=None):
    x, y = xy
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    asc, desc = fnt.getmetrics()
    step = int((asc + desc) * leading)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += step
    return y


def spaced(draw, xy, text, fnt, fill, tracking=5):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def _bezier(p0, p1, p2, n=20):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        pts.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                    mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))
    return pts


def chip(draw, cx, cy, num, fill=RED):
    r = 15
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    draw.text((cx, cy - 1), str(num), font=font(SB, 17),
              fill=(255, 255, 255), anchor="mm")


# ------------------------------------------------------------- scenes
def scene_port(d, x, y, w, h):
    col = (170, 200, 235)
    sea = y + h - 12
    # water with wave ticks
    d.rectangle([x, sea, x + w, y + h], fill=(43, 78, 128))
    for i, wfx in enumerate((0.08, 0.38, 0.62, 0.88)):
        wy = sea + 4 + (i % 2) * 3
        d.line([x + w * wfx, wy, x + w * wfx + 14, wy],
               fill=(110, 160, 215), width=2)
    # container ship, left of centre: hull, stacked boxes, bridge tower
    hx0, hx1 = x + w * 0.06, x + w * 0.44
    d.polygon([(hx0, sea - 8), (hx1, sea - 8), (hx1 - 8, sea + 1),
               (hx0 + 5, sea + 1)], fill=(200, 200, 214))
    bw_, bh_ = w * 0.105, 7
    for fx, lvl, c in ((0.09, 0, GOLD), (0.09, 1, (178, 90, 80)),
                       (0.20, 0, (120, 150, 190)), (0.20, 1, GOLD),
                       (0.31, 0, (178, 90, 80))):
        bx = x + w * fx
        by = sea - 8 - (lvl + 1) * bh_
        d.rectangle([bx, by, bx + bw_, by + bh_ - 1], fill=c)
    d.rectangle([hx1 - 12, sea - 22, hx1 - 3, sea - 8],
                fill=(200, 200, 214))
    # two portal cranes over the quay, right side
    for fx in (0.58, 0.80):
        cx = x + w * fx
        d.line([cx, sea, cx, y + 6], fill=col, width=3)
        d.line([cx + 16, sea, cx + 16, y + 6], fill=col, width=3)
        d.line([cx - 8, y + 6, cx + 26, y + 6], fill=col, width=3)
    # a container hanging from the first crane's hook
    hx_ = x + w * 0.58 + 10
    d.line([hx_, y + 6, hx_, y + 20], fill=col, width=1)
    d.rectangle([hx_ - 7, y + 20, hx_ + 7, y + 27], fill=GOLD)
    # two missiles arcing in from the top right, starbursts at the quay
    shots = (((0.99, 0.00), (0.94, 0.30), (0.86, 0.62)),
             ((0.90, 0.00), (0.80, 0.26), (0.70, 0.60)))
    for p0, p1, p2 in shots:
        pts = _bezier((x + w * p0[0], y + h * p0[1]),
                      (x + w * p1[0], y + h * p1[1]),
                      (x + w * p2[0], y + h * p2[1]))
        d.line(pts, fill=(240, 120, 60), width=2)
        ex, ey = pts[-1]
        star(d, ex, ey, 7, GOLD)
        star(d, ex, ey, 3.5, RED)


def scene_plot(d, x, y, w, h):
    # Danish flag on a pole, left
    px = x + w * 0.10
    d.line([px, y + 4, px, y + h - 4], fill=(220, 220, 228), width=3)
    fx0, fy0 = px + 2, y + 6
    d.rectangle([fx0, fy0, fx0 + 74, fy0 + 34], fill=(198, 44, 54))
    d.rectangle([fx0 + 20, fy0, fx0 + 30, fy0 + 34],
                fill=(255, 255, 255))
    d.rectangle([fx0, fy0 + 14, fx0 + 74, fy0 + 20],
                fill=(255, 255, 255))
    # press microphone, right of centre
    mx = x + w * 0.62
    my = y + 6
    d.rounded_rectangle([mx, my, mx + 26, my + 32], 12,
                        fill=(205, 205, 218))
    for gy in (my + 8, my + 15, my + 22):
        d.line([mx + 4, gy, mx + 22, gy], fill=(90, 90, 110), width=2)
    d.arc([mx - 7, my + 12, mx + 33, my + 46], 20, 160,
          fill=(205, 205, 218), width=3)
    d.line([mx + 13, my + 42, mx + 13, y + h - 3],
           fill=(205, 205, 218), width=3)
    d.line([mx + 2, y + h - 3, mx + 24, y + h - 3],
           fill=(205, 205, 218), width=3)
    # camera flashes
    star(d, x + w * 0.88, y + 12, 6, GOLD)
    star(d, x + w * 0.94, y + 27, 4, (255, 255, 255))


def scene_mercury(d, x, y, w, h):
    # sun, top-left, with rays
    sx, sy = x + 20, y + 14
    d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=GOLD)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([sx + 11 * math.cos(a), sy + 11 * math.sin(a),
                sx + 15 * math.cos(a), sy + 15 * math.sin(a)],
               fill=GOLD, width=2)
    # Mercury: big cratered disc, right
    cx, cy, r = x + w - 52, y + h // 2, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 166, 150))
    for dx, dy, cr in ((-10, -8, 6), (6, -14, 4), (12, 4, 7),
                       (-4, 10, 5), (-16, 6, 3), (2, -2, 3)):
        d.ellipse([cx + dx - cr, cy + dy - cr * 0.8,
                   cx + dx + cr, cy + dy + cr * 0.8],
                  outline=(128, 116, 100), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 100, 260,
          fill=(110, 100, 88), width=3)
    # BepiColombo orbiter: body, dish, two solar-panel wings
    ox, oy = x + w * 0.36, y + h * 0.44
    d.polygon([(ox - 5, oy - 3), (ox - 26, oy - 8), (ox - 26, oy + 2),
               (ox - 5, oy + 2)], fill=(70, 110, 190))
    d.polygon([(ox + 5, oy - 3), (ox + 26, oy - 8), (ox + 26, oy + 2),
               (ox + 5, oy + 2)], fill=(70, 110, 190))
    d.rectangle([ox - 5, oy - 5, ox + 5, oy + 5], fill=(205, 205, 218))
    d.arc([ox - 6, oy - 16, ox + 6, oy - 4], 180, 360,
          fill=(205, 205, 218), width=2)
    # dashed flight path curving in from the left edge to the planet
    pts = _bezier((x + 2, y + h * 0.78), (x + w * 0.34, y + h * 0.86),
                  (cx - r - 6, cy + 12), n=40)
    for i in range(0, len(pts), 4):
        px_, py_ = pts[i]
        d.ellipse([px_ - 1.2, py_ - 1.2, px_ + 1.2, py_ + 1.2],
                  fill=(150, 150, 170))


# --------------------------------------------------------- card icons
# Each icon draws in a 42x44 box at (x, y): flat shapes, 2-3 colours,
# no text. Same visual language as the hero scenes.
BLUE = (43, 92, 168)
GREEN = (110, 150, 75)
DGREEN = (84, 120, 56)
STEEL = (105, 105, 115)
SKY = (168, 208, 224)


def icon_quote(d, x, y):
    # speech bubble with two gold quote marks
    d.rounded_rectangle([x + 4, y + 7, x + 36, y + 29], 6, fill=NAVY)
    d.polygon([(x + 12, y + 29), (x + 12, y + 38), (x + 22, y + 29)],
              fill=NAVY)
    for qx in (x + 12, x + 23):
        d.rounded_rectangle([qx, y + 13, qx + 5, y + 20], 2, fill=GOLD)
        d.polygon([(qx, y + 20), (qx + 5, y + 20), (qx + 1, y + 24)],
                  fill=GOLD)


def icon_atom(d, x, y):
    cx, cy = x + 21, y + 22
    d.ellipse([cx - 21, cy - 8, cx + 21, cy + 8], outline=TEAL, width=2)
    d.ellipse([cx - 8, cy - 19, cx + 8, cy + 19], outline=BLUE, width=2)
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=TEAL,
              width=1)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=GOLD)
    for ex, ey in ((cx + 19, cy - 5), (cx - 6, cy - 17),
                   (cx - 13, cy + 10)):
        d.ellipse([ex - 2.4, ey - 2.4, ex + 2.4, ey + 2.4], fill=RED)


def icon_cop(d, x, y):
    cx, cy = x + 16, y + 20
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=SKY,
              outline=TEAL, width=2)
    d.ellipse([cx - 5, cy - 13, cx + 5, cy + 13], outline=TEAL, width=1)
    d.line([cx - 13, cy, cx + 13, cy], fill=TEAL, width=1)
    # clock overlapping the globe's lower right: talks in overtime
    kx, ky = x + 32, y + 33
    d.ellipse([kx - 8, ky - 8, kx + 8, ky + 8], fill=(255, 255, 255),
              outline=RED, width=2)
    d.line([kx, ky, kx, ky - 5], fill=INK, width=2)
    d.line([kx, ky, kx + 4, ky + 3], fill=INK, width=2)


def icon_prison(d, x, y):
    for i in range(5):
        bx = x + 5 + i * 8
        d.rectangle([bx, y + 8, bx + 4, y + 36], fill=STEEL)
    d.rectangle([x + 3, y + 6, x + 39, y + 10], fill=INK)
    d.rectangle([x + 3, y + 34, x + 39, y + 38], fill=INK)


def icon_capsule(d, x, y):
    # horizontal pill: red left half, white right half
    d.rounded_rectangle([x + 3, y + 14, x + 39, y + 30], 8, fill=RED)
    d.rounded_rectangle([x + 21, y + 14, x + 39, y + 30], 8,
                        fill=(255, 255, 255))
    d.rectangle([x + 21, y + 15, x + 27, y + 29], fill=(255, 255, 255))
    d.rounded_rectangle([x + 3, y + 14, x + 39, y + 30], 8, outline=INK,
                        width=2)
    d.line([x + 9, y + 19, x + 17, y + 19], fill=(255, 255, 255),
           width=2)


def icon_gamepad(d, x, y):
    d.rounded_rectangle([x + 3, y + 13, x + 39, y + 33], 10, fill=DARK)
    d.rectangle([x + 9, y + 20, x + 17, y + 26], fill=(255, 255, 255))
    d.rectangle([x + 11, y + 18, x + 15, y + 28], fill=(255, 255, 255))
    d.ellipse([x + 26, y + 18, x + 31, y + 23], fill=RED)
    d.ellipse([x + 31, y + 24, x + 36, y + 29], fill=GOLD)


def icon_wheat(d, x, y):
    cx = x + 21
    d.line([cx, y + 42, cx, y + 10], fill=DGREEN, width=2)
    for i, gy in enumerate((34, 27, 20, 13)):
        spread = 9 - i
        d.polygon([(cx, y + gy + 6), (cx - spread - 3, y + gy - 2),
                   (cx, y + gy - 4)], fill=GOLD)
        d.polygon([(cx, y + gy + 6), (cx + spread + 3, y + gy - 2),
                   (cx, y + gy - 4)], fill=GOLD)
    for dx in (-6, 0, 6):
        d.line([cx, y + 9, cx + dx, y + 1], fill=GOLD, width=1)


def icon_pumpjack(d, x, y):
    d.line([x + 2, y + 39, x + 41, y + 39], fill=INK, width=2)
    d.line([x + 9, y + 39, x + 17, y + 15], fill=NAVY, width=3)
    d.line([x + 25, y + 39, x + 17, y + 15], fill=NAVY, width=3)
    d.line([x + 12, y + 28, x + 22, y + 28], fill=NAVY, width=2)
    d.line([x + 5, y + 13, x + 38, y + 19], fill=INK, width=4)
    d.polygon([(x + 36, y + 17), (x + 41, y + 19), (x + 39, y + 26),
               (x + 35, y + 22)], fill=INK)
    d.line([x + 38, y + 26, x + 38, y + 39], fill=INK, width=2)
    d.rectangle([x + 2, y + 15, x + 8, y + 21], fill=NAVY)
    d.ellipse([x + 14, y + 12, x + 20, y + 18], fill=GOLD)


def icon_gavel(d, x, y):
    cx, cy = x + 15, y + 13
    dx, dy = 0.866, -0.5          # head axis
    px, py = 0.5, 0.866           # head perpendicular
    hl, hh2 = 9.5, 3.6
    corners = [(cx + dx * hl + px * hh2, cy + dy * hl + py * hh2),
               (cx + dx * hl - px * hh2, cy + dy * hl - py * hh2),
               (cx - dx * hl - px * hh2, cy - dy * hl - py * hh2),
               (cx - dx * hl + px * hh2, cy - dy * hl + py * hh2)]
    d.polygon(corners, fill=NAVY)
    for s in (7, -7):
        d.line([(cx + dx * s + px * hh2, cy + dy * s + py * hh2),
                (cx + dx * s - px * hh2, cy + dy * s - py * hh2)],
               fill=GOLD, width=2)
    d.line([x + 17, y + 16, x + 28, y + 30], fill=GOLD, width=4)
    d.rounded_rectangle([x + 23, y + 34, x + 41, y + 40], 2, fill=INK)


def icon_bridge(d, x, y):
    col = BLUE
    deck = y + 30
    for fxp in (0.30, 0.70):
        px = x + 42 * fxp
        d.rectangle([px - 2, y + 8, px + 2, deck], fill=col)
    cable = [(x + 42 * fx, deck + dy) for fx, dy in
             ((0.02, -6), (0.18, -13), (0.30, -18), (0.50, -11),
              (0.70, -18), (0.82, -13), (0.98, -6))]
    d.line(cable, fill=col, width=2)
    for hx_, hy_ in (cable[1], cable[3], cable[5]):
        d.line([hx_, hy_, hx_, deck], fill=col, width=1)
    d.line([x + 2, deck, x + 40, deck], fill=col, width=4)
    d.line([x + 4, y + 38, x + 16, y + 38], fill=SKY, width=2)
    d.line([x + 24, y + 40, x + 36, y + 40], fill=SKY, width=2)


ICONS = {4: icon_quote, 5: icon_atom, 6: icon_cop, 7: icon_prison,
         8: icon_capsule, 9: icon_gamepad, 10: icon_wheat,
         11: icon_pumpjack, 12: icon_gavel, 13: icon_bridge}


# --------------------------------------------------------------- data
STATS = [
    ("3", "Houthi missiles downed over Riyadh"),
    ("41", "killed in 24 hours, Houthis say"),
    ("2", "Danes charged in the plot"),
    ("8 yrs", "BepiColombo's voyage to Mercury"),
    ("235", "months in prison for Gupta"),
    ("1st", "dual-orbit Mercury mission"),
]

HEROES = [
    (1, "HODEIDAH · YEMEN", scene_port, NAVY,
     "Coalition strikes hit Hodeidah port",
     "Saudi-led coalition aircraft struck the port. Three Houthi "
     "ballistic missiles were intercepted over Riyadh; the Houthis "
     "say 41 killed in 24 hours. (wire reports)"),
    (2, "COPENHAGEN · DENMARK", scene_plot, TEAL,
     "Denmark charges two in Russian murder plot",
     "Two Danes recruited by Russia to assassinate a US-Ukrainian "
     "rapper, prosecutors say; Russia's defence attaché was "
     "expelled. (BBC)"),
    (3, "MERCURY · SPACE", scene_mercury, DARK,
     "BepiColombo reaches Mercury at last",
     "After an eight-year voyage since its 2018 launch, ESA's MPO "
     "and JAXA's Mio enter orbit — the first dual-orbit Mercury "
     "mission. (ESA)"),
]

CARDS = [
    (4, "Zelenskyy rebukes Trump over Putin remark",
     "Trump called Putin “a friend of mine” at Shenzhen; "
     "Zelenskyy: “Putin is an enemy and a killer in our eyes.” "
     "(reports)"),
    (5, "Iran holds uranium red line, open to a deal",
     "Tehran keeps its enrichment red line, but Araqchi wants "
     "dialogue; Trump calls the terms unacceptable. (reports)"),
    (6, "COP31 runs into overtime in Antalya",
     "The fossil-fuel text is still deadlocked past the Friday "
     "deadline as the summit overruns. (reports)"),
    (7, "Nikhil Gupta sentenced to 235 months",
     "US prison term for the plot to assassinate Sikh separatist "
     "Gurpatwant Singh Pannun. (BBC)"),
    (8, "Cancer pill daraxonrasib shows promise",
     "Pancreatic tumours stopped growing in nearly all trial "
     "patients and vanished in 1 in 12. (BBC, Guardian)"),
    (9, "GTA VI weekend: police urge calm",
     "US police departments warn players to “keep it in the "
     "game” on launch weekend. (BBC)"),
    (10, "Ukraine to send food aid to nine countries",
     "Kyiv announces food-aid shipments to nine countries. "
     "(wire reports)"),
    (11, "Iraq arrests pipeline CEO in smuggling case",
     "The petroleum-pipeline chief held over an oil-smuggling "
     "network in Jurf al-Sakhar. (wire reports)"),
    (12, "Bali daycare head jailed five years",
     "Sentenced to five years in prison for child abuse at the "
     "daycare she ran. (reports)"),
    (13, "Kyiv reopens bridge hit in Friday's attack",
     "The bridge damaged in Friday's barrage over the capital is "
     "open to traffic again. (wire reports)"),
]

ALSO = [
    ("Hodeidah", "UN warns strikes threaten the aid lifeline", "UN"),
    ("Moscow", "Russia denies the Copenhagen plot", "reports"),
    ("Washington", "US declassifies more Middle East UFO footage",
     "BBC"),
    ("US", "birds die in a blaze at a foie gras farm", "BBC"),
    ("Conakry", "Guinea bans a Burkina Faso broadcaster",
     "France 24"),
    ("The Hague", "Warden interceptor missile costs €30,000",
     "reports"),
    ("Riyadh", "storm warnings for Jazan and Najran",
     "Saudi Gazette"),
    ("Rome", "court orders a Ukrainian child returned", "reports"),
    ("Kyiv", "Russia lost 1,410 troops in a day", "Gen. Staff"),
    ("Moscow", "Russia says it downed drones overnight", "MoD"),
    ("Kathmandu", "PM Balendra Shah faces his first India test",
     "BBC"),
    ("Wellington", "Test day 3: India resume reply to 368",
     "reports"),
    ("Washington", "second judge blocks Trump's planned arch",
     "reports"),
    ("Europe", "cost-of-living protests sweep cities", "BBC"),
    ("Washington", "Trump threatens to bar overseas AI data centres",
     "BBC"),
    ("Antalya", "Turkey banks hosting deals as COP31 stalls",
     "reports"),
    ("Mercury", "BepiColombo orbiters split on 9–10 Dec", "ESA"),
]

DATE_CHECK = ("Left out as wrong-day news: the Kyiv bridge barrage, "
              "Cyclone Akvan's Odisha landfall and the Wall Street AI "
              "correction (all Friday), Mongolia's president resigning "
              "(Thursday) and the Riemann-hypothesis claim (Friday) "
              "— big stories, but not Saturday's.")

FOOTER = ("Every story here happened, or was first reported, on "
          "Saturday 21 November 2026. Sources named beside each "
          "story · original drawings.")


# ---------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 8], fill=INK)
    spaced(d, (M, 16), "THE WORLD IN ONE DAY", font(SB, 21), RED, 5)
    d.text((W - M, 16), "GLOBAL NEWS BRIEF", font=font(SB, 20),
           fill=GREY, anchor="ra")
    date_text = "SATURDAY 21 NOVEMBER 2026"
    size = 64
    while d.textlength(date_text, font=font(FB, size)) > CW:
        size -= 2
    d.text((W / 2, 42), date_text, font=font(FB, size), fill=INK,
           anchor="ma")
    y = 42 + size + 10
    d.line([M, y, W - M, y], fill=INK, width=5)
    d.line([M, y + 7, W - M, y + 7], fill=INK, width=2)
    y += 15

    # Stats strip
    sh = 58
    d.rectangle([M, y, W - M, y + sh], fill=NAVY)
    cell = CW / 6
    lab_f = font(SR, 11)
    for i, (num, label) in enumerate(STATS):
        cx = M + i * cell
        if i:
            d.line([cx, y + 8, cx, y + sh - 8], fill=(70, 96, 140),
                   width=1)
        d.text((cx + cell / 2, y + 5), num, font=font(SB, 23),
               fill=GOLD, anchor="ma")
        ly = y + 33
        for ln in wrap(d, label, lab_f, cell - 12)[:2]:
            d.text((cx + cell / 2, ly), ln, font=lab_f,
                   fill=(225, 232, 245), anchor="ma")
            ly += 12
    y += sh + 7

    # Heroes
    hh = 212
    hw = (CW - 22) // 3
    for i, (num, kicker, scene, bg, head, body) in enumerate(HEROES):
        hx = M + i * (hw + 11)
        d.rounded_rectangle([hx, y, hx + hw, y + hh], 10, fill=bg)
        scene(d, hx + 10, y + 8, hw - 20, 56)
        chip(d, hx + 24, y + 24, num)
        d.text((hx + 16, y + 70), kicker, font=font(SB, 13),
               fill=(160, 190, 235))
        y_end = text_block(d, (hx + 16, y + 88), head, font(FB, 19),
                           (255, 255, 255), hw - 32, leading=1.05,
                           max_lines=2)
        text_block(d, (hx + 16, y_end + 3), body, font(SR, 13),
                   LIGHT, hw - 32, leading=1.1, max_lines=4)
    y += hh + 7

    # Numbered cards, 2 x 5
    chh, cgap = 56, 5
    cw2 = (CW - cgap) // 2
    for i, (num, head, body) in enumerate(CARDS):
        cx = M + (i % 2) * (cw2 + cgap)
        cy = y + (i // 2) * (chh + cgap)
        d.rounded_rectangle([cx, cy, cx + cw2, cy + chh], 8, fill=CARD,
                            outline=LINE, width=2)
        chip(d, cx + 26, cy + chh // 2, num, fill=NAVY)
        icon = ICONS.get(num)
        if icon:
            icon(d, cx + 48, cy + 6)
        tx = cx + 96
        tw = cw2 - 96 - 12
        y_end = text_block(d, (tx, cy + 6), head, font(SB, 15), INK,
                           tw, leading=1.05, max_lines=1)
        text_block(d, (tx, y_end + 2), body, font(SR, 12), GREY, tw,
                   leading=1.08, max_lines=2)
    y += 5 * chh + 4 * cgap + 7

    # Region strip
    rh = 36
    d.rectangle([M, y, W - M, y + rh], fill=BAND)
    d.text((M + 14, y + rh / 2), "WHERE IT HAPPENED", font=font(SB, 14),
           fill=RED, anchor="lm")
    d.text((M + 218, y + rh / 2),
           "Europe 10  ·  Asia 4  ·  Middle East 5  ·  Africa 1  ·  "
           "Americas 7  ·  Oceania 1  ·  Space 2",
           font=font(SR, 15), fill=INK, anchor="lm")
    d.text((W - M - 14, y + rh / 2), "30 stories in all",
           font=font(SB, 14), fill=NAVY, anchor="rm")
    y += rh + 7

    # Also on Saturday: two columns of one-liners
    also_head = "ALSO ON SATURDAY"
    d.text((M, y), also_head, font=font(SB, 16), fill=RED)
    lx = M + d.textlength(also_head, font=font(SB, 16)) + 14
    d.line([lx, y + 10, W - M, y + 10], fill=LINE, width=2)
    y += 23
    colw = (CW - 28) // 2
    per_col = (len(ALSO) + 1) // 2
    fb13, fr13 = font(SB, 13), font(SR, 13)
    for j, (city, text, src) in enumerate(ALSO):
        ax = M + (j // per_col) * (colw + 28)
        ay = y + (j % per_col) * 15
        d.text((ax, ay), city, font=fb13, fill=INK)
        x2 = ax + d.textlength(city, font=fb13)
        rest = " — " + text + " "
        d.text((x2, ay), rest, font=fr13, fill=INK)
        x3 = x2 + d.textlength(rest, font=fr13)
        d.text((x3, ay), "(" + src + ")", font=fr13, fill=GREY)
    y += per_col * 15 + 5

    # Date check strip
    bh = 54
    d.rounded_rectangle([M, y, W - M, y + bh], 8, fill=TINT,
                        outline=RED, width=3)
    d.text((M + 14, y + 9), "DATE CHECK", font=font(SB, 13), fill=RED)
    text_block(d, (M + 118, y + 9), DATE_CHECK, font(SR, 13), INK,
               CW - 118 - 14, leading=1.12, max_lines=3)
    y += bh + 7

    # Footer
    d.line([M, y, W - M, y], fill=INK, width=2)
    d.text((W / 2, y + 6), FOOTER, font=font(SI, 12), fill=GREY,
           anchor="ma")
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img = build()
    img.save(out, optimize=True)
    size = os.path.getsize(out)
    with open(out, "rb") as f:
        magic = f.read(8)
    if magic[:4] != b"\x89PNG" and magic[:2] != b"\xff\xd8":
        raise SystemExit("output is not a PNG or JPEG")
    print(f"wrote {out} ({size} bytes)")


if __name__ == "__main__":
    main()
