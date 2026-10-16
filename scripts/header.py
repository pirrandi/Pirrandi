"""Generate a DAW-style animated SVG header for the GitHub profile README."""
import math
import sys

W, H = 880, 300
BPM, BARS = 128, 8
DUR = BARS * 4 * 60 / BPM  # seconds for one full pass of the playhead
TL_X0, TL_X1 = 176, 864    # timeline extents
BAR_W = (TL_X1 - TL_X0) / BARS
RULER_Y = 118
TRACK_Y0, TRACK_H = 136, 34

BG, PANEL, GRID, MUTED, TEXT = "#0b0f14", "#11161d", "#1f262e", "#6e7681", "#e6edf3"

TRACKS = [
    {"name": "research", "sub": "security", "color": "#ff5f56", "clips": [
        (0, 1.9, "recon"), (2, 5, "CVE-2026-54053 · 9.6 CRIT"), (5.1, 8, "web · AD · CTF")]},
    {"name": "flowdit", "sub": "self-hosted", "color": "#9fef00", "clips": [
        (0, 1.9, "targets"), (2, 3.9, "findings"), (4, 5.9, "WSTG checklists"), (6, 8, "reports")]},
    {"name": "certs", "sub": "learning", "color": "#1793d1", "clips": [
        (0, 1.4, "eJPT"), (1.5, 2.9, "ICCA"), (3, 4.9, "eWPTX"), (5, 8, "BSCP", "rec")]},
    {"name": "samples", "sub": "sampling", "color": "#bc8cff", "clips": [
        (0, 3.9, "sample_01.wav", "wave"), (4, 8, "chop_02.wav", "wave")]},
]


def bx(bar):
    return TL_X0 + bar * BAR_W


def anim(attr, values, key_times):
    vals = ";".join(str(v) for v in values)
    keys = ";".join(f"{k:.4f}" for k in key_times)
    return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{keys}" '
            f'dur="{DUR}s" repeatCount="indefinite"/>')


def lit(x0, x1, low, high):
    """Brighten an element while the playhead is between x0 and x1."""
    span = TL_X1 - TL_X0
    t0, t1 = (x0 - TL_X0) / span, (x1 - TL_X0) / span
    e = 0.004
    if t0 <= 0:
        return anim("opacity", [high, high, low, low], [0, t1, min(t1 + e, 1), 1])
    if t1 + e >= 1:
        return anim("opacity", [low, low, high, high], [0, t0, t0 + e, 1])
    return anim("opacity", [low, low, high, high, low, low], [0, t0, t0 + e, t1, t1 + e, 1])


def waveform(x0, x1, cy, amp, seed):
    bars = []
    x = x0 + 4
    i = 0
    while x < x1 - 4:
        a = abs(math.sin(i * 0.37 + seed) * math.cos(i * 0.11 + seed * 2)) * 0.8
        a += 0.2 * abs(math.sin(i * 1.7 + seed))
        h = max(1.5, a * amp)
        bars.append(f'<rect x="{x:.1f}" y="{cy - h:.1f}" width="2" height="{2 * h:.1f}"/>')
        x += 3.5
        i += 1
    return "".join(bars)


def clip(track, y, spec, seed):
    start, end, label, *kind = spec
    kind = kind[0] if kind else ""
    x0, x1 = bx(start) + 1, bx(end) - 1
    w, h = x1 - x0, TRACK_H - 6
    c = track["color"]
    # in-progress clips stay dimmed: nothing to play back yet
    glow = "" if kind == "rec" else lit(x0, x1, 0.45, 1)
    out = [f'<g opacity="0.45">{glow}']
    dash = ' stroke-dasharray="4 3"' if kind == "rec" else ""
    out.append(f'<rect x="{x0:.1f}" y="{y + 3}" width="{w:.1f}" height="{h}" rx="3" '
               f'fill="{c}" fill-opacity="0.18" stroke="{c}"{dash}/>')
    out.append(f'<rect x="{x0:.1f}" y="{y + 3}" width="{w:.1f}" height="9" rx="3" fill="{c}" fill-opacity="0.35"/>')
    out.append(f'<text x="{x0 + 5:.1f}" y="{y + 10.5}" class="mono" font-size="8" fill="{TEXT}">{label}</text>')
    if kind == "wave":
        out.append(f'<g fill="{c}">{waveform(x0, x1, y + 23, 7, seed)}</g>')
    elif kind == "rec":
        out.append(f'<circle cx="{x1 - 9:.1f}" cy="{y + 7.5}" r="2.5" fill="#ff3e3e">'
                   f'<animate attributeName="opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite"/></circle>')
        out.append(f'<text x="{x0 + 5:.1f}" y="{y + 26}" class="mono" font-size="8" fill="{MUTED}">in progress</text>')
    else:
        # midi-ish note blocks to give the clip some body
        n = max(2, int(w // 22))
        for k in range(n):
            nx = x0 + 6 + k * (w - 12) / n
            ny = y + 15 + ((k * 7 + seed * 3) % 11)
            out.append(f'<rect x="{nx:.1f}" y="{ny}" width="{(w - 12) / n * 0.6:.1f}" height="3" rx="1" fill="{c}" fill-opacity="0.7"/>')
    out.append("</g>")
    return "".join(out)


def meter(x, y, seed):
    vals = [0.2 + 0.8 * abs(math.sin(seed + k * 1.3)) for k in range(6)]
    hs = ";".join(f"{v * 22:.1f}" for v in vals + vals[:1])
    ys = ";".join(f"{y + 22 - v * 22:.1f}" for v in vals + vals[:1])
    d = 0.7 + (seed % 3) * 0.1
    return (f'<rect x="{x}" y="{y}" width="4" height="22" fill="{GRID}"/>'
            f'<rect x="{x}" y="{y + 11}" width="4" height="11" fill="#9fef00">'
            f'<animate attributeName="height" values="{hs}" dur="{d:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{ys}" dur="{d:.2f}s" repeatCount="indefinite"/></rect>')


def build():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         "<defs><style>",
         "text { font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }",
         ".mono { font-family: ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; }",
         "</style></defs>",
         f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>']

    # transport bar
    o.append(f'<rect x="0" y="0" width="{W}" height="36" rx="10" fill="{PANEL}"/>')
    o.append(f'<rect x="0" y="26" width="{W}" height="10" fill="{PANEL}"/>')
    o.append(f'<line x1="0" y1="36" x2="{W}" y2="36" stroke="{GRID}"/>')
    o.append(f'<text x="18" y="23" class="mono" font-size="11" fill="{TEXT}">pirrandi<tspan fill="{MUTED}">.project</tspan></text>')
    cx = W / 2
    o.append(f'<rect x="{cx - 52}" y="10" width="104" height="17" rx="4" fill="{BG}" stroke="{GRID}"/>')
    o.append(f'<path d="M{cx - 38} 13 l9 5.5 l-9 5.5 z" fill="#9fef00"/>')
    o.append(f'<rect x="{cx - 14}" y="14" width="9" height="9" fill="{MUTED}"/>')
    o.append(f'<circle cx="{cx + 14}" cy="18.5" r="4.5" fill="#ff3e3e">'
             '<animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite"/></circle>')
    o.append(f'<text x="{cx + 28}" y="22" class="mono" font-size="8" fill="{MUTED}">REC</text>')
    o.append(f'<text x="{W - 18}" y="23" text-anchor="end" class="mono" font-size="11" fill="{TEXT}">{BPM}.00 <tspan fill="{MUTED}">BPM · 4/4 · arch</tspan></text>')

    # identity
    o.append(f'<text x="18" y="78" font-size="30" font-weight="600" fill="{TEXT}">Diego Valencia</text>')
    o.append(f'<text x="18" y="100" font-size="12" fill="#9fef00" letter-spacing="2.5">SECURITY RESEARCHER · PENTESTER</text>')
    o.append(f'<text x="{W - 18}" y="78" text-anchor="end" class="mono" font-size="10" fill="{MUTED}">eJPT · eWPTX · ICCA</text>')
    o.append(f'<text x="{W - 18}" y="96" text-anchor="end" class="mono" font-size="10" fill="{MUTED}">CVE-2026-54053 <tspan fill="#ff3e3e">9.6</tspan></text>')

    # ruler
    o.append(f'<rect x="{TL_X0}" y="{RULER_Y}" width="{TL_X1 - TL_X0}" height="16" fill="{PANEL}"/>')
    for b in range(BARS):
        x = bx(b)
        o.append(f'<line x1="{x:.1f}" y1="{RULER_Y}" x2="{x:.1f}" y2="{RULER_Y + 16}" stroke="{GRID}"/>')
        o.append(f'<text x="{x + 4:.1f}" y="{RULER_Y + 11}" class="mono" font-size="8" fill="{MUTED}">{b + 1}</text>')
        for q in range(1, 4):
            qx = x + q * BAR_W / 4
            o.append(f'<line x1="{qx:.1f}" y1="{RULER_Y + 11}" x2="{qx:.1f}" y2="{RULER_Y + 16}" stroke="{GRID}"/>')

    # tracks
    for i, t in enumerate(TRACKS):
        y = TRACK_Y0 + i * TRACK_H
        o.append(f'<rect x="12" y="{y + 1}" width="{TL_X0 - 18}" height="{TRACK_H - 2}" rx="4" fill="{PANEL}"/>')
        o.append(f'<rect x="12" y="{y + 1}" width="3" height="{TRACK_H - 2}" rx="1.5" fill="{t["color"]}"/>')
        o.append(f'<text x="24" y="{y + 15}" class="mono" font-size="10" fill="{TEXT}">{t["name"]}</text>')
        o.append(f'<text x="24" y="{y + 27}" class="mono" font-size="8" fill="{MUTED}">{t["sub"]}</text>')
        for j, lbl in enumerate("MS"):
            o.append(f'<rect x="{112 + j * 16}" y="{y + 10}" width="13" height="13" rx="2" fill="{BG}" stroke="{GRID}"/>'
                     f'<text x="{118.5 + j * 16}" y="{y + 19.5}" text-anchor="middle" class="mono" font-size="7" fill="{MUTED}">{lbl}</text>')
        o.append(meter(148, y + 6, i * 2 + 1))
        o.append(f'<line x1="{TL_X0}" y1="{y + TRACK_H}" x2="{TL_X1}" y2="{y + TRACK_H}" stroke="{GRID}" stroke-opacity="0.5"/>')
        for b in range(1, BARS):
            o.append(f'<line x1="{bx(b):.1f}" y1="{y}" x2="{bx(b):.1f}" y2="{y + TRACK_H}" stroke="{GRID}" stroke-opacity="0.4"/>')
        for k, spec in enumerate(t["clips"]):
            o.append(clip(t, y, spec, i * 5 + k))

    # playhead
    bottom = TRACK_Y0 + len(TRACKS) * TRACK_H
    o.append(f'<g transform="translate({TL_X0} 0)">'
             f'<line x1="0" y1="{RULER_Y}" x2="0" y2="{bottom}" stroke="#e6edf3" stroke-width="1.2"/>'
             f'<path d="M-5 {RULER_Y} h10 l-5 7 z" fill="#e6edf3"/>'
             f'<animateTransform attributeName="transform" type="translate" from="{TL_X0} 0" to="{TL_X1} 0" '
             f'dur="{DUR}s" repeatCount="indefinite"/></g>')

    # footer
    o.append(f'<text x="18" y="{H - 10}" class="mono" font-size="9" fill="{MUTED}">github.com/pirrandi</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    with open(sys.argv[1], "w") as f:
        f.write(build() + "\n")
