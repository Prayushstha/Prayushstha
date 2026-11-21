"""Generates minimal transparent SVGs for Prayushstha's GitHub profile:
  assets/profile-card.svg  animated avatar card
  assets/contrib-bars.svg  weekly contribution BAR graph (last year)
  assets/skills.svg        minimal skill list
  assets/currently-building.svg  active development projects
  assets/repo-<name>.svg   one transparent card per featured repo
"""
import argparse, os, json, base64, textwrap, urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "Prayushstha")
TOKEN = os.environ.get("GH_TOKEN")
REPOS = ["NoNotion", "Inventory-Manager", "Chulo"]
HEADINGS = ["About Me", "Skills", "Latest Projects", "Connect"]
SKILLS = ["HTML", "CSS", "JavaScript", "TypeScript", "React",
          "Vite", "Node.js", "Electron", "SQLite", "Git"]

# Active work is independent of the featured repository cards and GitHub API.
CURRENTLY_BUILDING = [
    {
        "name": "NoNotion",
        "description": "A desktop productivity and habit-tracking application.",
        "tech": ["React", "TypeScript", "Electron", "SQLite"],
        "status": "In Development",
        "repository": "https://github.com/Prayushstha/NoNotion",
    },
    {
        "name": "Collaborative 2D Game",
        "description": "A story-driven 2D game being developed with a team.",
        "tech": ["Godot", "GDScript"],
        "status": "In Development",
        "repository": None,
    },
]

def gql(query, variables):
    if not TOKEN:
        raise RuntimeError("Set GH_TOKEN to refresh GitHub profile graphics.")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": "prayushstha-readme"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]

USER_Q = """query($login:String!){user(login:$login){
  name login bio avatarUrl followers{totalCount}
  repositories(ownerAffiliations:OWNER){totalCount}
  contributionsCollection{contributionCalendar{totalContributions
    weeks{contributionDays{date contributionCount}}}}}}"""

def repos_q():
    parts = "".join(
        f'r{i}:repository(owner:$login,name:"{n}"){{name description stargazerCount forkCount primaryLanguage{{name color}}}}'
        for i, n in enumerate(REPOS))
    return f"query($login:String!){{{parts}}}"

def avatar_b64(url):
    url += ("&" if "?" in url else "?") + "s=260"
    req = urllib.request.Request(url, headers={"User-Agent": "prayushstha-readme"})
    with urllib.request.urlopen(req) as r:
        return f"data:{r.headers.get_content_type()};base64," + base64.b64encode(r.read()).decode()

DEFS = """
<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">
  <feDropShadow dx="0" dy="1" stdDeviation="1.2" flood-color="#000000" flood-opacity=".12"/>
</filter>
<style>
  svg{color:#FFF3B0;--primary:#FFF3B0;--secondary:#E3D3A0;--muted:#CDB46A;--accent:#FFD700;--gold:#FFD700;--highlight:#FFF3B0;--border:#B8860B}
  .primary{fill:var(--primary)}
  .secondary{fill:var(--secondary)}
  .muted{fill:var(--muted)}
  .accent{fill:var(--accent)}
  .gold{fill:var(--gold)}
  .border{stroke:var(--border)}
  .frame{stroke:var(--gold)}
  .r1{stroke:var(--highlight)}
  .bar{fill:var(--accent)}
  .peak{fill:var(--gold)}
  .inactive{fill:var(--border)}
  @media (prefers-color-scheme:light){
    svg{color:#2B2208;--primary:#2B2208;--secondary:#66521C;--muted:#7C6324;--accent:#8A6508;--gold:#8A6508;--highlight:#B8860B;--border:#B8860B}
  }
  text,image,circle,path,.b{filter:url(#shadow)}
</style>
"""
# Dark palette targets GitHub's #0D1117 interface without painting a background.
# Light-mode overrides retain warm gold accents with stronger contrast.
FONT = "font-family:'Segoe UI',Helvetica,Arial,sans-serif;"

def card_bg(w, h, r=22):
    return ""


def profile_card(u, total):
    W, H = 900, 280
    name = escape(u["name"] or u["login"])
    bio = escape((u["bio"] or "CSIT student from Nepal | Frontend developer")[:80])
    css = """
    text{%s}
    @keyframes spin{to{transform:rotate(360deg)}}
    .r1{transform-origin:150px 140px;animation:spin 14s linear infinite}
    .avatar-haze{filter:none}
    @keyframes rise{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
    .t{animation:rise .9s ease-out both}
    """ % FONT
    stats = [("Repos", u["repositories"]["totalCount"]), ("Followers", u["followers"]["totalCount"]),
             ("Contributions / yr", total)]
    stat_svg = ""
    for i, (k, v) in enumerate(stats):
        x = 330 + i * 190
        tone = "gold" if i == 2 else "accent"
        stat_svg += (f'<g class="t" style="animation-delay:{.6+i*.15}s">'
                     f'<rect class="border" x="{x}" y="190" width="170" height="62" rx="14" fill="none" stroke="#B8860B"/>'
                     f'<text class="{tone}" x="{x+85}" y="219" text-anchor="middle" font-size="22" font-weight="700" fill="currentColor">{v}</text>'
                     f'<text class="muted" x="{x+85}" y="240" text-anchor="middle" font-size="11" fill="currentColor" letter-spacing="1">{k.upper()}</text></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<clipPath id="c"><circle cx="150" cy="140" r="106"/></clipPath>
<radialGradient id="avatar-haze">
  <stop offset="0" stop-color="#FFD700" stop-opacity=".04"/>
  <stop offset=".74" stop-color="#FFD700" stop-opacity=".14"/>
  <stop offset="1" stop-color="#FFD700" stop-opacity="0"/>
</radialGradient><style>{css}</style></defs>
<circle class="avatar-haze" cx="150" cy="140" r="136" fill="url(#avatar-haze)"/>
<image href="{avatar_b64(u['avatarUrl'])}" x="44" y="34" width="212" height="212" clip-path="url(#c)" preserveAspectRatio="xMidYMid slice"/>
<circle class="frame" cx="150" cy="140" r="108" fill="none" stroke="#FFD700" stroke-width="1.5"/>
<circle class="r1" cx="150" cy="140" r="120" fill="none" stroke="#FFF3B0" stroke-width="1.5" stroke-dasharray="40 14 8 14" stroke-linecap="round"/>
<text class="t primary" x="330" y="95" font-size="44" font-weight="800" fill="currentColor">{name}</text>
<text class="t accent" style="animation-delay:.2s" x="332" y="125" font-size="17" fill="currentColor">@{escape(u['login'])}</text>
<text class="t secondary" style="animation-delay:.4s" x="332" y="160" font-size="15" fill="currentColor">{bio}</text>
{stat_svg}
</svg>"""

def contrib_bars(cal):
    weeks = cal["weeks"]
    counts = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    W, H, L, R, T, B = 900, 260, 8, 8, 80, 38
    ch = H - T - B
    n = len(counts); slot = (W - L - R) / n; bw = slot * 0.66
    mx = max(counts) or 1
    css = """
    text{%s}
    @keyframes grow{from{transform:scaleY(0);opacity:0}to{transform:scaleY(1);opacity:1}}
    @keyframes fade{from{opacity:0}to{opacity:1}}
    .b{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}
    .f{animation:fade 1.2s ease-out both}
    """ % FONT
    bars, labels, prev = "", "", None
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for i, (c, w) in enumerate(zip(counts, weeks)):
        h = max(4, c / mx * ch) if c else 4
        x = L + i * slot + (slot - bw) / 2
        y = T + ch - h
        # Keep bar geometry and totals unchanged; encode activity with intensity.
        op = .35 + .65 * c / mx if c else .25
        tone = "inactive" if not c else "peak" if c == mx else "bar"
        bars += (f'<rect class="b {tone}" style="animation-delay:{i*0.018:.3f}s" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                 f'height="{h:.1f}" rx="{min(3,bw/2):.1f}" fill="currentColor" opacity="{op}"><title>{c} contributions</title></rect>')
        month = w["contributionDays"][0]["date"][5:7]
        if month != prev:
            labels += f'<text class="muted" x="{x:.1f}" y="{H-12}" font-size="11" fill="currentColor">{months[int(month)-1]}</text>'
            prev = month
    grid = "".join(f'<line class="border" x1="{L}" x2="{W-R}" y1="{T+ch*k/4:.1f}" y2="{T+ch*k/4:.1f}" stroke="#B8860B" stroke-opacity=".4" stroke-dasharray="3 5"/>' for k in range(5))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
{card_bg(W,H)}
<text class="f accent" x="{L}" y="28" font-size="24" font-weight="700" fill="currentColor">Contribution Activity</text>
<text class="f secondary" x="{L}" y="50" font-size="12" fill="currentColor">Weekly commits, PRs, issues &amp; reviews over the last year</text>
<text class="f accent" x="{W-R}" y="28" text-anchor="end" font-size="26" font-weight="800" fill="currentColor">{cal['totalContributions']}</text>
<text class="f muted" x="{W-R}" y="50" text-anchor="end" font-size="11" fill="currentColor" letter-spacing="1">TOTAL · PEAK WEEK {max(counts)}</text>
{grid}{bars}{labels}
</svg>"""

def skills_svg():
    W, H = 900, 160
    css = "text{%s}" % FONT
    parts = ""
    for row in range(0, len(SKILLS), 5):
        chips = ""
        for i, s in enumerate(SKILLS[row:row+5]):
            if i:
                chips += '<tspan class="muted" dx="16" font-weight="300" fill="currentColor">||</tspan>'
            chips += f'<tspan dx="{16 if i else 0}">{escape(s)}</tspan>'
        parts += f'<text class="primary" x="{W/2}" y="{82 + (row//5)*42}" text-anchor="middle" font-size="22" font-weight="600" fill="currentColor">{chips}</text>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}
<style>{css}</style></defs>
{card_bg(W,H)}
<text class="accent" x="{W/2}" y="40" text-anchor="middle" font-size="12" font-weight="700" letter-spacing="3" fill="currentColor">LANGUAGES &amp; TECH</text>
{parts}
</svg>"""

def repo_card(r, idx):
    W, H = 290, 160
    name = escape(r["name"])
    name_size = min(22, int(240 / (len(r["name"]) * .62)))
    desc = r.get("description") or "No description yet."
    lines = textwrap.wrap(desc, 32)
    if len(lines) > 2:
        lines = lines[:2]; lines[1] = lines[1][:29].rstrip() + "…"
    lang = (r.get("primaryLanguage") or {}).get("name", "")
    css = "text{%s}" % FONT
    desc_svg = "".join(f'<text class="secondary" x="24" y="{82+i*20}" font-size="13" fill="currentColor">{escape(l)}</text>' for i, l in enumerate(lines))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{DEFS}<style>{css}</style></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="#FFD700" fill-opacity=".035"/>
<rect class="border" x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="none" stroke="#B8860B" stroke-opacity=".5" stroke-width="1"/>
<text class="accent" x="24" y="44" font-size="{name_size}" font-weight="800" fill="currentColor">{name}</text>
<line class="border" x1="24" y1="58" x2="266" y2="58" stroke="#B8860B" stroke-width="1.5" stroke-linecap="round"/>
{desc_svg}
<text class="muted" x="24" y="138" font-size="12" fill="currentColor">{escape(lang)}</text>
<text class="muted" x="266" y="138" text-anchor="end" font-size="12" fill="currentColor">★ {r['stargazerCount']}   ⑂ {r['forkCount']}</text>
</svg>"""

def currently_building_svg(stacked=False):
    # A separate mobile source avoids shrinking desktop text on small screens.
    width, padding, gap = (480 if stacked else 900), 6, 12
    card_width = width - padding * 2 if stacked else (width - padding * 2 - gap) / 2
    card_height = 178 if stacked else 146
    rows = len(CURRENTLY_BUILDING) if stacked else 1
    height = padding * 2 + rows * card_height + (rows - 1) * gap
    cards = []
    for i, project in enumerate(CURRENTLY_BUILDING):
        left = padding if stacked else padding + i * (card_width + gap)
        top = padding + i * (card_height + gap) if stacked else padding
        x = left + 18
        description = textwrap.wrap(project["description"], 44) if stacked else [project["description"]]
        description_size = 18 if stacked else 13
        description_svg = "".join(
            f'<text class="secondary" x="{x}" y="{top+60+j*24}" font-size="{description_size}">{escape(line)}</text>'
            for j, line in enumerate(description)
        )
        chip_y = top + (104 if stacked else 79)
        chip_x = x
        chips = []
        for tech in project["tech"]:
            chip_width = len(tech) * (9.4 if stacked else 7.2) + 18
            chip_height, chip_baseline, chip_font = (28, 20, 16) if stacked else (24, 16, 12)
            chips.append(f'''<rect class="border" x="{chip_x}" y="{chip_y}" width="{chip_width}" height="{chip_height}" rx="6" fill="none"/>
<text class="primary" x="{chip_x+9}" y="{chip_y+chip_baseline}" font-size="{chip_font}">{escape(tech)}</text>''')
            chip_x += chip_width + 7
        status_y = top + card_height - 20
        cards.append(f'''<g>
<rect class="border" x="{left}" y="{top}" width="{card_width}" height="{card_height}" rx="12" fill="none"/>
<text class="name" x="{x}" y="{top+30}" font-size="22" font-weight="600">{escape(project['name'])}</text>
{description_svg}
{''.join(chips)}
<circle class="status-dot" cx="{x+3}" cy="{status_y-4}" r="3"/>
<text class="secondary" x="{x+14}" y="{status_y}" font-size="{16 if stacked else 12}">{escape(project['status'])}</text>
</g>''')
    title = escape("Currently Building: " + " and ".join(p["name"] for p in CURRENTLY_BUILDING))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="building-title">
<title id="building-title">{title}</title>
<style>
  svg{{--accent:#E3B341;--highlight:#F2CC60;--primary:#E6EDF3;--secondary:#9DA7B3;--border:#30363D}}
  text{{{FONT}}}
  .name{{fill:var(--accent)}}
  .primary{{fill:var(--primary)}}
  .secondary{{fill:var(--secondary)}}
  .border{{stroke:var(--border);stroke-width:1}}
  .status-dot{{fill:var(--highlight);opacity:.65}}
  @media (prefers-color-scheme:light){{
    svg{{--accent:#9A6700;--highlight:#BF8700;--primary:#24292F;--secondary:#57606A;--border:#D0D7DE}}
  }}
</style>
{''.join(cards)}
</svg>'''


def section_heading(title):
    width = len(title) * 17
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="30" viewBox="0 0 {width} 30">
<defs>{DEFS}</defs>
<text class="accent" x="0" y="23" font-size="24" font-weight="600" style="{FONT}">{escape(title)}</text>
</svg>'''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--currently-building-only", action="store_true",
                        help="Generate only the active projects graphic; no GitHub token required.")
    args = parser.parse_args()
    os.makedirs("assets", exist_ok=True)
    def w(p, s): open(p, "w", encoding="utf-8").write(s)
    w("assets/currently-building.svg", currently_building_svg())
    w("assets/currently-building-mobile.svg", currently_building_svg(stacked=True))
    if args.currently_building_only:
        print("Generated desktop and mobile Currently Building graphics")
        return
    u = gql(USER_Q, {"login": USER})["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    rd = gql(repos_q(), {"login": USER})
    w("assets/profile-card.svg", profile_card(u, cal["totalContributions"]))
    w("assets/contrib-bars.svg", contrib_bars(cal))
    w("assets/skills.svg", skills_svg())
    for title in HEADINGS:
        w(f"assets/heading-{title.lower().replace(' ', '-')}.svg", section_heading(title))
    for i, n in enumerate(REPOS):
        r = rd.get(f"r{i}") or {"name": n, "description": None, "stargazerCount": 0, "forkCount": 0}
        w(f"assets/repo-{n.lower()}.svg", repo_card(r, i))
    print("done")


if __name__ == "__main__":
    main()
