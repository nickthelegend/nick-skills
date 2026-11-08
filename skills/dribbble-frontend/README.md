# dribbble-frontend

A Claude Code skill that makes the agent design from real references instead of templates. Before it writes any
UI code, it:
- picks fitting Dribbble shots from **your own** reference library, at random (seeded) so two products never get
  the same look;
- studies the full-resolution images and writes down concrete takes (layout, density, type scale, components,
  motion, palette);
- checks the planned fonts, palette and archetype against your other products;
- builds the UI, then QAs it side by side with the references at 375 px and 1440 px.

It is part of [nick-skills](https://github.com/nickthelegend/nick-skills), the loops behind a solo builder's weekly
hackathon entries. This repo is the same skill on its own.

## Install

```bash
git clone https://github.com/nickthelegend/dribbble-frontend ~/.claude/skills/dribbble-frontend
export DRIBBBLE_LIB=~/design-references        # your library (see below)
python3 ~/.claude/skills/dribbble-frontend/scripts/pick.py write-categories
```

Then, in Claude Code, ask for any UI ("build the landing page", "restyle the dashboard") or type `/dribbble-frontend`.

Needs Python 3, plus ffmpeg for contact sheets.

## Commands

| Command | What it does |
|---|---|
| `pick.py categories` | categories with shot counts |
| `pick.py filter WORD ...` | every shot whose search, title or category contains all the words |
| `pick.py pick "words" -n 4 --log SLUG [--kind web\|mobile] [--seed S]` | seeded random references, logged with a takes template |
| `pick.py check --slug SLUG --font F --palette "#..,#.." --archetype "words" --log` | flags fonts, colours or archetypes already used by another product |
| `pick.py sheet --log SLUG --add shot-1440.png shot-375.png` | a contact sheet of the picks next to your build screenshots |
| `pick.py lint SLUG` | unfilled takes and a missing QA record |
| `pick.py write-categories` | regenerates the category map after the library grows |

36 categories, including landing, dashboard, fintech, crypto, trading, launchpad, stocks, consumer payments,
privacy, AI, marketplace, games, comics, editorial, data-viz, flows, mobile onboarding, personal finance, governance,
spatial, workflow tools and AI memory. They are defined in `CATS` and `TERM_CATS` in
[scripts/pick.py](scripts/pick.py).

## The library is yours, and it stays private

The public copy of this skill (in [nick-skills](https://github.com/nickthelegend/nick-skills)) ships **no images**.
Shots on Dribbble belong to their designers, so keep your library on your own disk or in a private repo, and never
ship or publish it. Nick's own copy of this repo is private and carries his library in `library/`.

Settings:
- `DRIBBBLE_LIB`: the library root. It holds `web-shots/` and `mobile-shots/`, each with an
  `INDEX.md` table of `| File | Search | Shot | Author |`.
- `DRIBBBLE_BRANDS` or `BRANDS_FILE`: a table of the fonts and palettes your products already use.

See "Build your own library" in [SKILL.md](SKILL.md).

## License

MIT © 2026 Nivesh Gajengi
