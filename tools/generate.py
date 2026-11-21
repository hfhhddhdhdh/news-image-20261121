#!/usr/bin/env python3
"""Render entry.png for the news-image-20261121 bounty.

A one-page newspaper infographic summing up the world news of Saturday
21 November 2026, drawn with Pillow from the day's reporting. This is a
local build tool only: it runs on this machine to produce the image the
entry ships. The entry program (main.py, standard library only) copies the
finished image to /output/entry.png in the grader.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1024, 1024

PAPER = (250, 246, 238)      # warm paper
NAVY = (18, 30, 54)          # masthead + ink
CRIMSON = (176, 32, 22)      # lead accent
STEEL = (28, 84, 150)        # diplomacy blue
OCHRE = (150, 108, 8)        # markets gold-brown
PLUM = (96, 48, 120)         # science purple
LEAF = (26, 118, 70)         # good-news green
CARD_BG = (255, 255, 255)
EDGE = (214, 208, 194)
GREY = (88, 94, 108)
FAINT = (150, 145, 130)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap_text(draw, text, fnt, width):
    """Greedy word wrap of `text` to lines no wider than `width`."""
    out = []
    current = ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=fnt) <= width:
            current = candidate
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def draw_paragraph(draw, x, y, text, fnt, fill, width, leading):
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap_text(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def section_label(draw, x, y, text, color):
    draw.text((x, y), text, font=load_font(SANS_BOLD, 18), fill=color)
    return y + 25


def panel(draw, x, y, w, h, accent):
    """White card with a thin border and a coloured spine on the left."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10,
                           fill=CARD_BG, outline=EDGE, width=1)
    draw.rounded_rectangle([x, y, x + 8, y + h], radius=4, fill=accent)


def glyph_rocket(draw, cx, cy, r, color):
    """A small rocket glyph centred at (cx, cy)."""
    draw.polygon([(cx, cy - r), (cx + r // 2, cy + r // 4),
                  (cx, cy + r // 2), (cx - r // 2, cy + r // 4)],
                 fill=color)
    draw.polygon([(cx - r // 2, cy + r // 4), (cx - r, cy + r),
                  (cx - r // 3, cy + r // 2)], fill=color)
    draw.polygon([(cx + r // 2, cy + r // 4), (cx + r, cy + r),
                  (cx + r // 3, cy + r // 2)], fill=color)
    draw.polygon([(cx - r // 4, cy + r // 2), (cx + r // 4, cy + r // 2),
                  (cx, cy + r)], fill=(230, 120, 40))


def glyph_rings(draw, cx, cy, r, color):
    for dx, dy in ((-r // 2, -r // 4), (r // 2, -r // 4), (0, r // 3)):
        draw.ellipse([cx + dx - r // 2, cy + dy - r // 2,
                       cx + dx + r // 2, cy + dy + r // 2],
                      outline=color, width=4)


def glyph_trend(draw, cx, cy, r, color):
    pts = [(cx - r, cy + r // 3), (cx - r // 2, cy - r // 3),
           (cx, cy + r // 5), (cx + r // 2, cy - r // 2),
           (cx + r, cy - r // 4)]
    draw.line(pts, fill=color, width=5, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=color)


def glyph_sigma(draw, cx, cy, r, color):
    fnt = load_font(SANS_BOLD, int(r * 2.1))
    draw.text((cx - r // 2, cy - r), "\u03a3", font=fnt, fill=color)


def glyph_flag(draw, cx, cy, r, color):
    draw.line([(cx, cy - r), (cx, cy + r)], fill=color, width=4)
    draw.polygon([(cx, cy - r), (cx + r, cy - r // 2), (cx, cy)],
                 fill=color)


def glyph_tick(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=5)
    draw.line([(cx - r // 2, cy), (cx - r // 6, cy + r // 2),
               (cx + r // 2, cy - r // 2)], fill=color, width=6,
              joint="curve")


def masthead(draw):
    draw.rectangle([0, 0, CANVAS_W, 112], fill=NAVY)
    tag = load_font(SANS_BOLD, 18)
    tagline = "T H E   W O R L D   I N   O N E   D A Y"
    tw = draw.textlength(tagline, font=tag)
    draw.text(((CANVAS_W - tw) / 2, 14), tagline, font=tag, fill=(201, 162, 39))
    title = load_font(SERIF_BOLD, 46)
    date = "Saturday, 21 November 2026"
    tw = draw.textlength(date, font=title)
    draw.text(((CANVAS_W - tw) / 2, 42), date, font=title, fill=(255, 255, 255))
    draw.rectangle([0, 112, CANVAS_W, 118], fill=(201, 162, 39))


def story_panel(draw, x, y, w, h, story):
    panel(draw, x, y, w, h, story["accent"])
    pad = 26
    inner = w - pad * 2
    yy = section_label(draw, x + pad, y + 14, story["kicker"], story["accent"])
    story["glyph"](draw, x + w - 52, y + 44, 20, story["accent"])
    yy = draw_paragraph(draw, x + pad, yy, story["headline"],
                        load_font(SANS_BOLD, story["head_size"]), NAVY,
                        inner - 96, story["head_size"] + 7)
    draw_paragraph(draw, x + pad, yy + 5, story["body"],
                   load_font(SANS_REG, 19), GREY, inner, 24)


def main():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)

    lead = {
        "kicker": "WAR  \u00b7  POLAND",
        "headline": "Russian missiles land in Poland; Tusk calls it a provocation",
        "body": ("Two cruise missiles and a jet-powered drone crash in "
                 "south-eastern Poland during Russia's largest strike on "
                 "Ukraine this month. NATO calls it a 'grave violation'."),
        "accent": CRIMSON,
        "glyph": glyph_rocket,
        "head_size": 36,
    }
    story_panel(d, 24, 134, 976, 192, lead)

    grid = [
        {
            "kicker": "DIPLOMACY  \u00b7  BERLIN",
            "headline": "Zelenskyy joins Berlin summit",
            "body": ("Kushner: Moscow is 'comfortable' with NATO-like "
                     "guarantees; Russia rejects the idea."),
            "accent": STEEL,
            "glyph": glyph_rings,
            "head_size": 28,
        },
        {
            "kicker": "MARKETS  \u00b7  NEW YORK",
            "headline": "Anthropic slides 8.5% in AI sell-off",
            "body": ("Shares close at $88.91 as the Nasdaq falls 4% and the "
                     "S&P enters correction."),
            "accent": OCHRE,
            "glyph": glyph_trend,
            "head_size": 28,
        },
        {
            "kicker": "SCIENCE  \u00b7  MATHEMATICS",
            "headline": "Claude helps prove Riemann Hypothesis",
            "body": ("Anthropic's Alp\u00f6ge publishes a Lean-checked proof; "
                     "independent checks compile it clean."),
            "accent": PLUM,
            "glyph": glyph_sigma,
            "head_size": 28,
        },
        {
            "kicker": "POLITICS  \u00b7  LONDON",
            "headline": "UK and EU agree closer ties",
            "body": ("Deal covers youth mobility, farming and carbon "
                     "markets; ministers hail a 'new chapter'."),
            "accent": NAVY,
            "glyph": glyph_flag,
            "head_size": 28,
        },
    ]
    positions = [(24, 342), (520, 342), (24, 544), (520, 544)]
    for story, (gx, gy) in zip(grid, positions):
        story_panel(d, gx, gy, 480, 186, story)

    # Good-news band.
    panel(d, 24, 746, 976, 106, LEAF)
    glyph_tick(d, 24 + 48, 746 + 53, 24, LEAF)
    yy = section_label(d, 116, 746 + 14, "HOPE  \u00b7  KUALA LUMPUR", LEAF)
    yy = draw_paragraph(d, 116, yy, "Malaysia to resettle 10,000 Rohingya in Turkey",
                        load_font(SANS_BOLD, 28), NAVY, 860, 34)
    draw_paragraph(d, 116, yy + 2,
                   "Days after the genocide ruling, a first resettlement "
                   "plan offers refugees a way out.",
                   load_font(SANS_REG, 19), GREY, 860, 24)

    # Ticker.
    d.rectangle([0, 868, CANVAS_W, 868 + 54], fill=NAVY)
    tick = ("Denmark: Russia plotted to kill a rapper  \u2022  "
            "Mamdani: close Rikers by 2032  \u2022  Trump: ban AI data "
            "centres abroad")
    size = 18
    tick_font = load_font(SANS_REG, size)
    while d.textlength(tick, font=tick_font) > 1000 and size > 12:
        size -= 1
        tick_font = load_font(SANS_REG, size)
    tw = d.textlength(tick, font=tick_font)
    d.text(((CANVAS_W - tw) / 2, 868 + (54 - size) // 2 - 2), tick,
           font=tick_font, fill=(255, 255, 255))

    # Footer.
    foot = load_font(SANS_REG, 16)
    line1 = ("Compiled from world reporting on 21 November 2026 \u2014 every "
             "story happened or was first reported that day.")
    tw = d.textlength(line1, font=foot)
    d.text(((CANVAS_W - tw) / 2, 940), line1, font=foot, fill=GREY)
    line2 = "THE WORLD IN ONE DAY  \u00b7  21 NOV 2026"
    line2_font = load_font(SANS_BOLD, 15)
    tw = d.textlength(line2, font=line2_font)
    d.text(((CANVAS_W - tw) / 2, 962), line2, font=line2_font, fill=FAINT)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
