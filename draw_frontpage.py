#!/usr/bin/env python3
"""Draw the front page for the make.fun news-image-20261121 entry.

The page is a one-sheet newspaper, "The World in One Day", summing up the
world news of Saturday 21 November 2026 on a 1024x1024 cream sheet:
a masthead, a strip of six key figures, three illustrated hero stories,
ten numbered story cards, a region tally, an "also on Saturday" column
pair, a date-check strip and a footer.

Run it with Pillow available; it writes entry.png next to itself.
The shipped entry.png is exactly this program's output. The program is
deterministic: fixed geometry, fixed text, no randomness, no clock.
"""

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 28
CONTENT_R = PAGE_W - MARGIN  # right edge of the content column

PAPER = (247, 241, 222)
INK = (36, 31, 25)
FAINT = (110, 100, 84)
RED = (172, 30, 28)
NAVY = (18, 32, 64)
NAVY_CARD = (24, 40, 78)
TEAL_CARD = (12, 90, 90)
DARK_CARD = (25, 23, 40)
GOLD = (233, 198, 102)
CARD_BG = (253, 250, 240)
CARD_LINE = (196, 186, 152)
BEIGE = (233, 221, 189)
DATE_BG = (250, 237, 229)
WHITE = (252, 252, 248)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_BOLD = FONT_DIR + "DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- text

def text_w(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[2] - box[0]


def wrap(draw, s, fnt, width):
    """Greedy word wrap; returns the list of lines that fit `width`."""
    lines = []
    current = ""
    for word in s.split():
        trial = word if not current else current + " " + word
        if text_w(draw, trial, fnt) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw, cx, y, s, fnt, fill):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


def draw_tracked(draw, cx, y, s, fnt, fill, tracking):
    """Draw text centred on cx with extra space between the letters."""
    widths = [text_w(draw, ch, fnt) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def draw_block(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- icons
# Every icon is drawn on its own transparent tile and pasted onto the
# page, so rotated pieces (atom rings, the capsule, the gavel) are easy:
# draw flat, rotate the tile, paste with its own alpha as the mask.

def new_tile(w, h):
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return tile, ImageDraw.Draw(tile)


def paste_rotated(page, tile, angle, cx, cy):
    spun = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    page.paste(spun, (int(cx - spun.width / 2), int(cy - spun.height / 2)), spun)


def starburst(draw, cx, cy, r_out, r_in, fill, points=8):
    """A small jagged star, used for flashes and missile bursts."""
    import math

    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def icon_quote(page, cx, cy, colour):
    tile, d = new_tile(46, 40)
    d.rounded_rectangle([4, 3, 42, 28], radius=6, fill=colour)
    d.polygon([(12, 27), (12, 37), (24, 27)], fill=colour)
    for qx in (15, 27):
        d.ellipse([qx, 10, qx + 5, 15], fill=WHITE)
        d.polygon([(qx - 1, 19), (qx + 6, 19), (qx + 3, 12)], fill=WHITE)
    page.paste(tile, (int(cx - 23), int(cy - 20)), tile)


def icon_atom(page, cx, cy, colour):
    ring, d = new_tile(48, 48)
    d.ellipse([3, 16, 45, 32], outline=colour, width=3)
    for angle in (0, 60, 120):
        paste_rotated(page, ring, angle, cx, cy)
    dot, d2 = new_tile(48, 48)
    d2.ellipse([20, 20, 28, 28], fill=colour)
    page.paste(dot, (int(cx - 24), int(cy - 24)), dot)


def icon_globe_clock(page, cx, cy, colour):
    tile, d = new_tile(48, 48)
    d.ellipse([3, 3, 39, 39], outline=colour, width=3)
    d.ellipse([14, 3, 28, 39], outline=colour, width=2)
    d.line([3, 21, 39, 21], fill=colour, width=2)
    d.ellipse([26, 26, 46, 46], fill=WHITE, outline=colour, width=3)
    d.line([36, 36, 36, 30], fill=colour, width=2)
    d.line([36, 36, 41, 38], fill=colour, width=2)
    page.paste(tile, (int(cx - 24), int(cy - 24)), tile)


def icon_bars(page, cx, cy, colour):
    tile, d = new_tile(44, 44)
    d.rectangle([5, 5, 39, 39], outline=colour, width=3)
    for bx in (13, 21, 29):
        d.line([bx, 5, bx, 39], fill=colour, width=4)
    d.line([5, 22, 39, 22], fill=colour, width=3)
    page.paste(tile, (int(cx - 22), int(cy - 22)), tile)


def icon_capsule(page, cx, cy, colour):
    tile, d = new_tile(52, 24)
    d.rounded_rectangle([2, 3, 50, 21], radius=10, outline=colour, width=3)
    d.rounded_rectangle([4, 5, 26, 19], radius=8, fill=colour)
    paste_rotated(page, tile, -38, cx, cy)


def icon_gamepad(page, cx, cy, colour):
    tile, d = new_tile(50, 38)
    d.rounded_rectangle([2, 6, 48, 30], radius=12, fill=colour)
    d.rectangle([11, 14, 23, 18], fill=WHITE)
    d.rectangle([15, 10, 19, 26], fill=WHITE)
    d.ellipse([32, 11, 38, 17], fill=WHITE)
    d.ellipse([39, 19, 45, 25], fill=WHITE)
    page.paste(tile, (int(cx - 25), int(cy - 19)), tile)


def icon_wheat(page, cx, cy, colour):
    tile, d = new_tile(40, 48)
    d.line([20, 46, 20, 8], fill=colour, width=3)
    # grains: small leaf shapes leaning off the stalk in pairs
    for i, gy in enumerate((12, 20, 28, 36)):
        d.polygon([(20, gy + 8), (8, gy), (20, gy - 4)], outline=colour, width=2)
        d.polygon([(20, gy + 8), (32, gy), (20, gy - 4)], outline=colour, width=2)
    d.polygon([(20, 10), (15, 0), (20, 3), (25, 0)], fill=colour)
    page.paste(tile, (int(cx - 20), int(cy - 24)), tile)


def icon_pumpjack(page, cx, cy, colour):
    tile, d = new_tile(50, 44)
    d.line([4, 40, 46, 40], fill=colour, width=3)
    d.polygon([(18, 40), (26, 40), (22, 14)], outline=colour, width=3)
    d.line([6, 10, 42, 16], fill=colour, width=4)
    d.polygon([(42, 16), (48, 22), (42, 26), (38, 18)], fill=colour)
    d.line([9, 12, 9, 24], fill=colour, width=3)
    d.rectangle([5, 24, 13, 30], outline=colour, width=2)
    d.ellipse([28, 32, 38, 40], outline=colour, width=2)
    page.paste(tile, (int(cx - 25), int(cy - 22)), tile)


def icon_gavel(page, cx, cy, colour):
    tile, d = new_tile(52, 52)
    # head: two striking blocks joined by a band, drawn flat then tilted
    d.rectangle([8, 6, 22, 20], fill=colour)
    d.rectangle([30, 6, 44, 20], fill=colour)
    d.rectangle([21, 9, 31, 17], fill=colour)
    d.line([26, 17, 40, 44], fill=colour, width=5)
    paste_rotated(page, tile, -28, cx, cy)
    base, d2 = new_tile(52, 52)
    d2.rectangle([12, 45, 42, 49], fill=colour)
    page.paste(base, (int(cx - 26), int(cy - 26)), base)


def icon_bridge(page, cx, cy, colour):
    tile, d = new_tile(52, 44)
    deck_y = 30
    d.line([2, deck_y, 50, deck_y], fill=colour, width=4)
    for tx in (14, 38):
        d.line([tx, 8, tx, 40], fill=colour, width=3)

    def cable_y(x):
        # parabola sagging between the tower tops (14, 8) and (38, 8)
        if x <= 14:
            return 16 - (x - 2) * 8 / 12
        if x >= 38:
            return 8 + (x - 38) * 8 / 12
        t = (x - 26) / 12
        return 8 + 11 * (1 - t * t)

    pts = [(x, cable_y(x)) for x in range(2, 51)]
    d.line(pts, fill=colour, width=2)
    for hx in (8, 20, 26, 32, 44):
        d.line([hx, cable_y(hx), hx, deck_y], fill=colour, width=1)
    d.line([2, 40, 50, 40], fill=colour, width=2)
    page.paste(tile, (int(cx - 26), int(cy - 22)), tile)


# ---------------------------------------------------------------- heroes

def scene_port(page, x, y, w, h):
    """Hodeidah port: cranes, a container ship, two missile arcs."""
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + w, y + h], fill=(42, 62, 112))
    sea_y = y + h - 26
    d.rectangle([x, sea_y, x + w, y + h], fill=(15, 32, 70))
    # two portal cranes
    for gx in (x + 26, x + 118):
        d.line([gx, sea_y, gx, y + 14], fill=(210, 214, 220), width=4)
        d.line([gx + 34, sea_y, gx + 34, y + 14], fill=(210, 214, 220), width=4)
        d.line([gx - 8, y + 14, gx + 62, y + 14], fill=(210, 214, 220), width=4)
        d.line([gx, y + 44, gx + 34, y + 14], fill=(160, 166, 176), width=2)
        d.line([gx, y + 44, gx + 34, y + 70], fill=(160, 166, 176), width=2)
    # container hanging from the second crane
    d.line([x + 152, y + 14, x + 152, y + 38], fill=(220, 224, 230), width=2)
    d.rectangle([x + 138, y + 38, x + 166, y + 54], fill=(206, 120, 44))
    # container ship at the right
    hull_y = sea_y + 6
    d.polygon([(x + 196, hull_y), (x + 288, hull_y), (x + 278, hull_y + 14),
               (x + 204, hull_y + 14)], fill=(120, 44, 38))
    cols = [(196, 92, 60), (70, 130, 180), (196, 92, 60), (88, 150, 96)]
    for i, c in enumerate(cols):
        d.rectangle([x + 202 + i * 20, hull_y - 14, x + 220 + i * 20, hull_y - 2],
                    fill=c)
    d.rectangle([x + 262, hull_y - 26, x + 276, hull_y - 2], fill=(210, 214, 220))
    # two orange missile arcs ending in bursts over the port
    import math

    for (sx, ex, peak) in ((x + 292, x + 96, y + 4), (x + 292, x + 44, y + 18)):
        sy, ey = sea_y - 8, y + 34
        cy = 2 * peak - 0.5 * (sy + ey)  # quadratic Bezier control height
        pts = []
        for t_i in range(25):
            t = t_i / 24
            px = sx + (ex - sx) * t
            py = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
            pts.append((px, py))
        d.line(pts, fill=(255, 150, 50), width=3)
        starburst(d, ex, ey, 13, 5, (255, 190, 70))
    d.line([x, sea_y, x + w, sea_y], fill=(120, 160, 210), width=2)


def scene_denmark(page, x, y, w, h):
    """A Danish flag on a pole beside a press microphone, flash stars."""
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + w, y + h], fill=(30, 122, 122))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(9, 66, 66))
    # flag pole and Danish flag
    pole_x = x + 52
    d.line([pole_x, y + 10, pole_x, y + h - 14], fill=(225, 228, 230), width=4)
    fx, fy, fw, fh = pole_x + 4, y + 12, 96, 62
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(198, 32, 44))
    d.rectangle([fx + 26, fy, fx + 38, fy + fh], fill=WHITE)
    d.rectangle([fx, fy + 25, fx + fw, fy + 37], fill=WHITE)
    # press microphone, tilted, with a foam head and a press cube
    mic, md = new_tile(120, 120)
    md.rounded_rectangle([46, 6, 74, 52], radius=12, fill=(38, 38, 44))
    for gy in (16, 26, 36):
        md.line([50, gy, 70, gy], fill=(120, 124, 132), width=2)
    md.rectangle([55, 52, 65, 66], fill=(90, 92, 100))
    md.rectangle([42, 66, 78, 92], fill=(240, 240, 244))
    md.rectangle([48, 72, 72, 86], outline=(198, 32, 44), width=3)
    md.line([60, 92, 60, 112], fill=(38, 38, 44), width=5)
    paste_rotated(page, mic, 24, x + 208, y + 62)
    # camera flashes
    starburst(d, x + 128, y + 26, 12, 4, (255, 244, 180), points=6)
    starburst(d, x + 262, y + 18, 10, 4, (255, 244, 180), points=6)
    starburst(d, x + 282, y + 96, 9, 3, (255, 255, 255), points=6)


def scene_mercury(page, x, y, w, h):
    """BepiColombo: a small orbiter on a dashed path to a cratered disc."""
    d = ImageDraw.Draw(page)
    d.rectangle([x, y, x + w, y + h], fill=(13, 11, 27))
    for (sx, sy, r) in ((30, 18, 2), (86, 40, 1), (140, 14, 2), (196, 30, 1),
                        (238, 58, 2), (52, 84, 1), (110, 96, 2), (268, 10, 1)):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(210, 214, 235))
    # sun in the top-left corner, with short rays
    sun_c = (x + 25, y + 23)
    d.ellipse([sun_c[0] - 15, sun_c[1] - 15, sun_c[0] + 15, sun_c[1] + 15],
              fill=(250, 205, 80))
    import math

    for k in range(6):
        a = math.radians(15 + k * 58)
        d.line([sun_c[0] + 20 * math.cos(a), sun_c[1] + 20 * math.sin(a),
                sun_c[0] + 28 * math.cos(a), sun_c[1] + 28 * math.sin(a)],
               fill=(250, 205, 80), width=3)
    # Mercury: a big cratered disc, lower right
    mx, my, mr = x + 214, y + 76, 44
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(168, 160, 150))
    for (cx, cy, cr, tone) in ((196, 62, 11, (146, 137, 126)),
                               (232, 92, 15, (150, 141, 130)),
                               (208, 104, 8, (142, 133, 122)),
                               (244, 56, 7, (152, 143, 132)),
                               (188, 88, 6, (148, 139, 128))):
        d.ellipse([x + cx - cr, y + cy - cr, x + cx + cr, y + cy + cr],
                  fill=tone, outline=(120, 112, 102), width=2)
    # dashed trajectory from the orbiter toward Mercury
    for t_i in range(14):
        t = t_i / 13
        px = x + 84 + (mx - mr - x - 78) * t
        py = y + 66 + (my - 16 - y - 66) * t + 14 * (t - t * t) * 4 / 4
        if t_i % 2 == 0:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(240, 240, 250))
    # the orbiter: bus, dish and two blue panel wings
    ox, oy = x + 66, y + 58
    d.rectangle([ox - 26, oy - 7, ox - 8, oy + 7], fill=(64, 110, 205))
    d.rectangle([ox + 8, oy - 7, ox + 26, oy + 7], fill=(64, 110, 205))
    d.rectangle([ox - 8, oy - 9, ox + 8, oy + 9], fill=(226, 228, 232))
    d.polygon([(ox, oy - 9), (ox - 10, oy - 20), (ox + 4, oy - 16)],
              fill=(240, 240, 244))
    d.line([ox, oy + 9, ox, oy + 18], fill=(200, 204, 210), width=2)


# ---------------------------------------------------------------- content

STATS = [
    "3 Houthi missiles downed over Riyadh",
    "41 killed in 24 h, Houthis say",
    "2 Danes charged",
    "8 yrs BepiColombo's voyage",
    "235 months for Gupta",
    "1st dual-orbit Mercury mission",
]

HEROES = [
    {
        "card": NAVY_CARD,
        "scene": scene_port,
        "headline": "COALITION BOMBS HODEIDAH PORT; MISSILES DOWNED OVER RIYADH",
        "summary": "Saudi-led jets struck Yemen's Red Sea port as defences "
                   "downed three Houthi ballistic missiles over Riyadh. "
                   "The Houthis say 41 people were killed in 24 hours.",
    },
    {
        "card": TEAL_CARD,
        "scene": scene_denmark,
        "headline": "DENMARK CHARGES TWO IN RUSSIAN PLOT TO KILL RAPPER",
        "summary": "Two Danes are accused of being recruited by Russia to "
                   "assassinate a US-Ukrainian rapper. Copenhagen has also "
                   "expelled Russia's defence attaché.",
    },
    {
        "card": DARK_CARD,
        "scene": scene_mercury,
        "headline": "BEPICOLOMBO REACHES MERCURY AFTER EIGHT-YEAR VOYAGE",
        "summary": "ESA's MPO and JAXA's Mio slip into orbit around Mercury "
                   "today, eight years after launch — the first mission to "
                   "fly two orbiters around the planet.",
    },
]

STORIES = [
    (4, icon_quote, RED,
     "Zelenskyy: Putin 'an enemy and a killer'",
     "Rebuking Trump for calling Putin 'a friend of mine' at Shenzhen."),
    (5, icon_atom, (150, 96, 20),
     "Iran holds red line, open to US deal",
     "Enriched-uranium line held; Araqchi seeks talks, Trump says no."),
    (6, icon_globe_clock, (12, 90, 90),
     "COP31 deadlocked into overtime in Antalya",
     "Fossil-fuel text still stuck past the Friday deadline."),
    (7, icon_bars, NAVY,
     "Gupta: 235 months for Pannun plot",
     "US sentence for the plot to kill Sikh separatist Pannun."),
    (8, icon_capsule, (170, 40, 90),
     "Cancer pill halts pancreatic tumours",
     "Daraxonrasib stopped tumours growing in nearly all patients; "
     "gone in 1 in 12."),
    (9, icon_gamepad, (90, 60, 140),
     "GTA VI: police say keep it in the game",
     "US departments issue warnings on the launch weekend."),
    (10, icon_wheat, (146, 110, 20),
     "Ukraine to send food aid to nine countries",
     "Kyiv pledges grain shipments to nine nations in need."),
    (11, icon_pumpjack, (100, 70, 40),
     "Pipeline CEO arrested over oil smuggling",
     "Iraq's petroleum chief held over a network at Jurf al-Sakhar."),
    (12, icon_gavel, (120, 50, 50),
     "Bali daycare head jailed for abuse",
     "Sentenced to five years for child abuse at the daycare."),
    (13, icon_bridge, (40, 100, 130),
     "Kyiv reopens bridge hit Friday",
     "The bridge damaged in Friday's attack is back in use."),
]

ALSO_LEFT = [
    "UN warns Hudaydah strikes threaten Yemen's aid lifeline",
    "Russia denies the Copenhagen plot",
    "US declassifies more UFO footage from the Middle East",
    "Birds die in a blaze at a large US foie gras farm",
    "Guinea bans a Burkina Faso broadcaster",
    "Dutch Warden interceptor missile costs ~€30,000",
    "Saudi civil defence warns of storms over Jazan and Najran",
    "Italian court orders a Ukrainian child returned in a custody ruling",
    "Kyiv says Russia lost 1,410 troops in a day",
]

ALSO_RIGHT = [
    "Russia says it downed Ukrainian drones overnight",
    "Nepal's new PM Balendra Shah faces his first India test",
    "Wellington Test day 3: India resume their reply to 368",
    "A second US judge blocks Trump's planned arch as a rushed job",
    "Cost-of-living protests sweep European cities",
    "Trump threatens to bar US firms from building AI data centres overseas",
    "Turkey banks hosting agreements as COP31 stalls",
    "BepiColombo's two orbiters separate 9–10 December",
]

REGION_LINE = ("Europe 10 · Asia 4 · Middle East 5 · Africa 1 · "
               "Americas 7 · Oceania 1 · Space 2 — 30 stories in all")

DATE_CHECK = ("Not Saturday: the Kyiv bridge barrage (Fri) · Cyclone "
              "Akvan's Odisha landfall (Fri) · the Wall Street AI "
              "correction (Fri) · Mongolia's president resigning (Thu) · "
              "the Riemann-hypothesis claim (Fri)")

FOOTER = ("The World in One Day — Saturday 21 November 2026 · Every story "
          "verified against at least two sources dated Saturday "
          "21 November 2026.")


# ---------------------------------------------------------------- build

def build_page():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(page)
    cx = PAGE_W // 2

    # masthead
    draw_tracked(d, cx, 14, "THE WORLD IN ONE DAY",
                 font(SANS_BOLD, 40), RED, 7)
    draw_tracked(d, cx, 63, "GLOBAL NEWS BRIEF",
                 font(SANS, 19), FAINT, 9)
    d.line([MARGIN, 93, CONTENT_R, 93], fill=INK, width=3)
    d.line([MARGIN, 98, CONTENT_R, 98], fill=INK, width=1)
    draw_centered(d, cx, 107, "SATURDAY 21 NOVEMBER 2026",
                  font(SERIF_BOLD, 44), INK)

    # stats strip: six figures in gold on navy
    strip_y, strip_h = 163, 50
    d.rectangle([MARGIN, strip_y, CONTENT_R, strip_y + strip_h], fill=NAVY)
    col_w = (CONTENT_R - MARGIN) / 6
    stat_font = font(SANS_BOLD, 13)
    for i, stat in enumerate(STATS):
        col_cx = MARGIN + col_w * (i + 0.5)
        lines = wrap(d, stat, stat_font, col_w - 16)
        ty = strip_y + (strip_h - len(lines) * 16) / 2
        for line in lines:
            draw_centered(d, col_cx, ty, line, stat_font, GOLD)
            ty += 16
        if i:
            sx = MARGIN + col_w * i
            d.line([sx, strip_y + 8, sx, strip_y + strip_h - 8],
                   fill=(74, 90, 128), width=1)

    # hero cards
    hero_y, hero_h, hero_w = 221, 276, 314
    head_font = font(SANS_BOLD, 16)
    sum_font = font(SANS, 13)
    for i, hero in enumerate(HEROES):
        hx = MARGIN + i * (hero_w + 13)
        d.rectangle([hx, hero_y, hx + hero_w, hero_y + hero_h],
                    fill=hero["card"])
        hero["scene"](page, hx + 10, hero_y + 10, hero_w - 20, 120)
        d = ImageDraw.Draw(page)
        ty = hero_y + 140
        for line in wrap(d, hero["headline"], head_font, hero_w - 24):
            d.text((hx + 12, ty), line, font=head_font, fill=WHITE)
            ty += 20
        ty += 5
        for line in wrap(d, hero["summary"], sum_font, hero_w - 24):
            d.text((hx + 12, ty), line, font=sum_font, fill=(228, 232, 240))
            ty += 16

    # numbered story cards, two rows of five
    card_w, card_h = 184, 132
    card_head = font(SANS_BOLD, 13)
    card_body = font(SANS, 11)
    num_font = font(SANS_BOLD, 15)
    for idx, (num, icon, colour, headline, body) in enumerate(STORIES):
        row, col = divmod(idx, 5)
        x = MARGIN + col * (card_w + 12)
        y = 505 + row * (card_h + 8)
        d.rounded_rectangle([x, y, x + card_w, y + card_h], radius=6,
                            fill=CARD_BG, outline=CARD_LINE, width=1)
        icon(page, x + 32, y + 30, colour)
        d = ImageDraw.Draw(page)
        label = str(num)
        d.text((x + card_w - 12 - text_w(d, label, num_font), y + 8),
               label, font=num_font, fill=RED)
        ty = y + 57
        for line in wrap(d, headline, card_head, card_w - 20):
            d.text((x + 10, ty), line, font=card_head, fill=INK)
            ty += 15.5
        ty += 3
        for line in wrap(d, body, card_body, card_w - 20):
            d.text((x + 10, ty), line, font=card_body, fill=(70, 63, 52))
            ty += 12.5

    return page


def finish_page(page):
    d = ImageDraw.Draw(page)

    # region tally on a beige band
    band_y = 785
    d.rectangle([MARGIN, band_y, CONTENT_R, band_y + 26], fill=BEIGE)
    draw_centered(d, PAGE_W // 2, band_y + 5, REGION_LINE,
                  font(SANS_BOLD, 13), INK)

    # also on Saturday: two columns of one-liners
    also_head = font(SANS_BOLD, 15)
    d.text((MARGIN, 819), "ALSO ON SATURDAY", font=also_head, fill=RED)
    head_w = text_w(d, "ALSO ON SATURDAY", also_head)
    d.line([MARGIN + head_w + 12, 827, CONTENT_R, 827], fill=CARD_LINE,
           width=1)
    item_font = font(SANS, 11)
    for col_x, items in ((MARGIN, ALSO_LEFT), (526, ALSO_RIGHT)):
        ty = 843
        for item in items:
            d.text((col_x, ty), "·  " + item, font=item_font, fill=INK)
            ty += 13

    # date check: the wrong-day stories this page deliberately leaves out
    dc_y = 964
    d.rectangle([MARGIN, dc_y, CONTENT_R, dc_y + 30], fill=DATE_BG,
                outline=RED, width=2)
    d.text((MARGIN + 12, dc_y + 8), "DATE CHECK", font=font(SANS_BOLD, 12),
           fill=RED)
    dc_font = font(SANS, 11)
    ty = dc_y + 3
    for line in wrap(d, DATE_CHECK, dc_font, CONTENT_R - MARGIN - 140):
        d.text((MARGIN + 128, ty), line, font=dc_font, fill=INK)
        ty += 13

    # footer
    draw_centered(d, PAGE_W // 2, 1000, FOOTER, font(SERIF_ITALIC, 13),
                  FAINT)
    return page


def main():
    import os

    page = finish_page(build_page())
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    page.save(out, format="PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
