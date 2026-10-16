"""Generate a DAW plugin-rack SVG showing the tech stack."""
import sys

W = 880
BG, PANEL, GRID, MUTED, TEXT = "#0b0f14", "#11161d", "#1f262e", "#6e7681", "#e6edf3"

CHAINS = [
    ("languages", "#bc8cff", [("Python", "scripting"), ("Shell", "automation"),
                              ("PowerShell", "windows"), ("C", "low-level"),
                              ("C++", "systems")]),
    ("offensive", "#ff5f56", [("Burp Suite", "web proxy"), ("Metasploit", "exploitation"),
                              ("Wireshark", "packets")]),
    ("infra", "#9fef00", [("Linux", "daily driver"), ("Docker", "containers"), ("Git", "versioning"),
                          ("WireGuard", "tunnels")]),
    ("hardware", "#ffbd2e", [("Raspberry Pi", "single-board"), ("Arduino", "microcontrollers")]),
    ("defense", "#1793d1", [("Wazuh", "SIEM / XDR"), ("Sentinel", "cloud SIEM"),
                            ("Trend Vision One", "XDR platform")]),
]

TOP = 36
ROW_H = 70
CHAIN_X = 12
DEV_X0 = 160
DEV_W, DEV_H, GAP = 128, 54, 12
H = TOP + 14 + len(CHAINS) * ROW_H + 14


def knob(cx, cy, color, seed):
    swing = 40 + (seed * 17) % 50
    base = -40 + (seed * 29) % 80
    dur = 2.4 + (seed % 4) * 0.5
    return (f'<circle cx="{cx}" cy="{cy}" r="11" fill="{BG}" stroke="{GRID}" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="{PANEL}"/>'
            f'<g><line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - 9}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'values="{base} {cx} {cy};{base + swing} {cx} {cy};{base} {cx} {cy}" '
            f'dur="{dur:.1f}s" repeatCount="indefinite"/></g>')


def meter(x, y, color, seed):
    out = []
    for k in range(5):
        delay = ((seed + k) * 0.13) % 0.9
        out.append(f'<rect x="{x + k * 5}" y="{y}" width="3" height="10" rx="1" fill="{color}" opacity="0.2">'
                   f'<animate attributeName="opacity" values="0.2;1;0.2" dur="0.9s" begin="{delay:.2f}s" '
                   f'repeatCount="indefinite"/></rect>')
    return "".join(out)


def device(x, y, name, role, color, seed):
    return "".join([
        f'<rect x="{x}" y="{y}" width="{DEV_W}" height="{DEV_H}" rx="5" fill="{PANEL}" stroke="{GRID}"/>',
        f'<path d="M{x} {y + 15} V{y + 5} a5 5 0 0 1 5 -5 H{x + DEV_W - 5} a5 5 0 0 1 5 5 V{y + 15} Z" '
        f'fill="{color}" fill-opacity="0.22"/>',
        # power LED
        f'<circle cx="{x + 9}" cy="{y + 7.5}" r="2.5" fill="{color}">'
        f'<animate attributeName="opacity" values="1;0.5;1" dur="{1.6 + (seed % 3) * 0.3:.1f}s" repeatCount="indefinite"/></circle>',
        f'<text x="{x + 17}" y="{y + 11}" class="mono" font-size="9" font-weight="700" fill="{TEXT}">{name.upper()}</text>',
        f'<text x="{x + 8}" y="{y + 31}" class="mono" font-size="8" fill="{MUTED}">{role}</text>',
        meter(x + 8, y + 38, color, seed),
        knob(x + DEV_W - 20, y + 35, color, seed),
    ])


def build():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         "<defs><style>",
         "text { font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }",
         ".mono { font-family: ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; }",
         "</style></defs>",
         f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
         f'<rect x="0" y="0" width="{W}" height="{TOP}" rx="10" fill="{PANEL}"/>',
         f'<rect x="0" y="{TOP - 10}" width="{W}" height="10" fill="{PANEL}"/>',
         f'<line x1="0" y1="{TOP}" x2="{W}" y2="{TOP}" stroke="{GRID}"/>',
         f'<text x="18" y="23" class="mono" font-size="11" fill="{TEXT}">device rack<tspan dx="7" fill="{MUTED}">· tech stack</tspan></text>',
         f'<text x="{W - 18}" y="23" text-anchor="end" class="mono" font-size="11" fill="{MUTED}">'
         f'{sum(len(c[2]) for c in CHAINS)} devices loaded</text>']

    seed = 0
    for i, (chain, color, devices) in enumerate(CHAINS):
        y = TOP + 14 + i * ROW_H
        dy = y + (ROW_H - DEV_H) / 2 - 4
        # chain header
        o.append(f'<rect x="{CHAIN_X}" y="{dy}" width="{DEV_X0 - CHAIN_X - 18}" height="{DEV_H}" rx="5" fill="{PANEL}"/>')
        o.append(f'<rect x="{CHAIN_X}" y="{dy}" width="3" height="{DEV_H}" rx="1.5" fill="{color}"/>')
        o.append(f'<text x="{CHAIN_X + 12}" y="{dy + 22}" class="mono" font-size="10" fill="{TEXT}">{chain}</text>')
        o.append(f'<text x="{CHAIN_X + 12}" y="{dy + 36}" class="mono" font-size="8" fill="{MUTED}">{len(devices)} inserts</text>')

        # signal cable from the chain header through every device
        cable_y = dy + DEV_H / 2
        end_x = DEV_X0 + len(devices) * (DEV_W + GAP) - GAP
        o.append(f'<line x1="{DEV_X0 - 18}" y1="{cable_y}" x2="{end_x}" y2="{cable_y}" stroke="{GRID}" stroke-width="2"/>')
        dur = 0.9 * len(devices) + 0.6
        o.append(f'<circle cx="{DEV_X0 - 18}" cy="{cable_y}" r="3" fill="{color}">'
                 f'<animate attributeName="cx" values="{DEV_X0 - 18};{end_x}" dur="{dur:.1f}s" begin="{i * 0.4:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.9;1" dur="{dur:.1f}s" begin="{i * 0.4:.1f}s" repeatCount="indefinite"/>'
                 f'</circle>')

        for k, (name, role) in enumerate(devices):
            o.append(device(DEV_X0 + k * (DEV_W + GAP), dy, name, role, color, seed))
            seed += 1

    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    with open(sys.argv[1], "w") as f:
        f.write(build() + "\n")
