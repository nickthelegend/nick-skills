---
name: dribbble-frontend
description: Nick's private Dribbble reference workflow for frontend work. Use it whenever you design, build, restyle or polish a web or app UI, including landing pages, marketing sites, dashboards, admin panels, trading terminals, launchpads, games, comic or creator sites, dev-tool or docs sites, wallets, payment apps, mobile screens, onboarding flows or any frontend component. Before you write UI code, pick fitting Dribbble shots from the local reference library at random (seeded), study the full-res images, write down concrete takes from each, check the planned fonts, palette and archetype against other products, then build and QA side by side with the references. Keep every product visually distinct and show only real data.
---

# Dribbble frontend

A private library of full-res Dribbble shots (440 web and 230 mobile, all 1800x1350, in 29 categories) sets the visual
bar before you write UI code. Every image is another designer's work: internal reference only (see Rules).

- Library root: `$DRIBBBLE_LIB` (default `/Volumes/Extreme SSD/Projects/grokbot/design-references/`). The images are
  **not** in this skill's repo; see "Build your own library" below.
  - `web-shots/` and `mobile-shots/`: individual shots; each `INDEX.md` gives file, search, title, author and Dribbble link.
  - `mobile/` and `web/`: older search-page grid captures (many shots per image; the mobile file labels are shifted, so
    read the search bar). The picker uses grids only with `--grids` or when no full-res shot fits.
  - `picks/<project>.md`: what each project picked, its takes, plan and QA record.
- Category map: [references/categories.md](references/categories.md). Picker: `python3 ~/.claude/skills/dribbble-frontend/scripts/pick.py` (below: `pick.py`).

| Command | What it does |
|---|---|
| `pick.py categories` | categories with shot counts |
| `pick.py filter WORD ...` | every shot whose search, title or category literally has all words |
| `pick.py pick "words" -n 4 --log SLUG [--kind web\|mobile] [--seed S]` | seeded random references, logged with a takes template |
| `pick.py check --slug SLUG --font F --font M --palette "#..,#.." --archetype "words" --log` | flags fonts, colours or archetype already used in `BRANDS.md` or other picks logs (exit 1 on a clash) |
| `pick.py sheet --log SLUG --add shot-1440.png shot-375.png` | ffmpeg contact sheet of the latest pick plus your build screenshots; prints the tile legend |
| `pick.py lint SLUG` | lists unfilled `__` takes fields and a missing QA record |
| `pick.py write-categories` | regenerates the category map after the library grows |

## Workflow

### 1. Name the category
Run `pick.py categories` and skim the category map. Name the product in plain words, for example "perps trading
terminal", "memecoin launchpad", "comic reader", "p2p payment app", "dev tool docs" or "auction marketplace".

### 2. Pick at random among fitting references
```bash
python3 ~/.claude/skills/dribbble-frontend/scripts/pick.py pick "<product category words>" -n 4 --log <project-slug>
```
- Shots are scored by how many of your words match their categories, search term and title; the best-matching pool
  (widened one step if small) is sampled with a printed seed (`--seed` reproduces it). Slot 1 comes from the best tier,
  the rest take one shot per search first.
- `--log` appends the pick to `picks/<slug>.md` and excludes shots other projects already logged. `--allow-reuse` only
  if the pool runs dry.
- `--kind mobile` draws from the full-res `mobile-shots/`; `--kind web` from `web-shots/`.
- Take 3 to 5: one for layout, one for density and components, one for mood and type, plus a mobile shot
  (`--kind mobile`, logged under the same slug) when the product is used on phones. If nothing fits, take the nearest
  category; never fall back to a generic template look.

### 3. Study the full-res images
Open every chosen file with the Read tool (absolute path) and look properly, not at a thumbnail.

### 4. Write concrete takes
`--log` writes this block under each shot. Replace every `__` with a number or a short phrase you measured from the shot
(estimate px against its 1800px width), or `n/a`:
```
- grid: __ columns, max width __px, gutter __px, side margin __px (375: __px); hero = __% of the fold
- type: display __px / weight __ / tracking __em / line-height __; h2 __px; body __px/__; label __px caps?; mono __
- spacing scale: __ (e.g. 4 8 12 16 24 32 48 64 96); section padding __px; card padding __px
- shape: radius cards __px, buttons __px, inputs __px; borders __px __colour; shadow __ (none / hard __px offset / y__ blur__ __%)
- motion: what moves __; duration __ms; easing __; reduced-motion fallback __
- palette: bg __, surface __, ink __, accent(s) __; light/dark __; contrast of body text __:1
- components: nav __; cards __; table/list __; buttons __; inputs __; empty/error state __
- this product does differently: __
```
Turn the agreed numbers into the product's tokens (CSS variables). `pick.py lint <slug>` lists anything left blank.
Keep this log in the library (it is private), never in a project repo.

### 5. Plan a distinct look and check it
Each product gets its own layout archetype, palette, sans + mono pairing and component shape language; a font appears
in exactly one product (`/Volumes/Extreme SSD/Projects/grokbot/BRANDS.md`). Before building, run
```bash
python3 ~/.claude/skills/dribbble-frontend/scripts/pick.py check --slug <slug> --font "<Sans>" --font "<Mono>" \
  --palette "#bg,#ink,#accent" --archetype "<metaphor in a few words>" --log
```
Resolve every `CLASH` (choose another font, colour or metaphor); `near` lines are colours within deltaE 10, so make sure
they read differently in context. Restyling an existing brand: pass `--brand <Name>` so its own row is ignored.
Nick prefers Polaris-grade UI that is different for each product; never Inter Tight, no glassmorphism by default.

### 6. Build to that bar
- Match the references' structure, spacing discipline, hierarchy and finish, at the same level of polish.
- Never copy their artwork, illustrations, 3D renders, photos, logos, brand names or text. Make your own (CSS, SVG,
  generated shapes, real product screenshots) and write your own copy for the actual product.
- Never embed, hotlink or ship the library images, and never copy them into any repository.

### 7. Show only real data
No mock numbers, fake users, invented testimonials, placeholder charts or "$1.2M volume" filler. Show live data from the
product, or an honest empty, loading, error or "Setup required" state. Label units.

### 8. QA side by side, then record it
Screenshot every route at 1440px and 375px, then
`pick.py sheet --log <slug> --add <shot-1440.png> <shot-375.png>` and open the sheet with Read. Fix gaps until the build
holds up next to the references, then tick the checklist:
- [ ] **Polaris-grade:** grid, type scale, density, contrast and finish match the takes; nothing looks like a default template.
- [ ] **Live data only:** every number, address and txid is real or labelled Empty / Loading / Setup required; units labelled.
- [ ] **375px:** no horizontal overflow on any route (`document.documentElement.scrollWidth <= innerWidth`), no clipped text, nav usable.
- [ ] **Tap targets** of 44x44px or more; spacing between adjacent targets.
- [ ] **Focus:** visible `:focus-visible` on every control; keyboard order makes sense.
- [ ] **Reduced motion:** `prefers-reduced-motion: reduce` turns animation off or static.
- [ ] **States:** designed empty, loading and error states on every data surface; errors are readable and fail loudly.
- [ ] **Contrast:** body text 4.5:1 or more; **distinct:** `pick.py check` has no unresolved CLASH.

Record the result under `### QA (<date>)` in `picks/<slug>.md` (pass, or what was fixed, round by round), then
`pick.py lint <slug>` should print `ok`.

## Rules
- The images belong to their designers. Internal reference only: don't publish them, put them in a project repo, ship
  them in a product or upload them anywhere. The only copy outside this Mac is the PRIVATE GitHub backup of the whole
  library (`design-references/`); never make that repo public.
- Point at the library by absolute path. Never copy images into a project. Contact sheets go to `$TMPDIR/dribbble-sheets/`
  (outside every repo).
- To fetch more shots use `design-references/tools/fetch-shots.mjs` from the private library (web or mobile, de-duplicated, exact 1800x1350 only;
  never bypass a bot check, login wall or CAPTCHA), add the new search terms to `TERM_CATS` in `pick.py`, then run
  `pick.py write-categories`.

## Build your own library (new machine or new user)
This public repo ships the picker, the category rules (`CATS` and `TERM_CATS` in `pick.py`) and the workflow, but no
images and no scraper. Nick's library and its fetcher (`tools/fetch-shots.mjs`) live in his **private** backup repo.

To start your own library:
- Save shots you have the right to use as reference, as 1800x1350 JPEGs, into `$DRIBBBLE_LIB/web-shots/` and
  `$DRIBBBLE_LIB/mobile-shots/`.
- Give each folder an `INDEX.md` table: `| File | Search | Shot | Author |`, with the shot's link and its author.
- Map each search term to categories in `TERM_CATS`, then run `python3 scripts/pick.py write-categories`.

Keep the library on your own disk, or in a private repo, never a public one. The images belong to their designers.

Settings: `DRIBBBLE_LIB` (library root) and `DRIBBBLE_BRANDS` or `BRANDS_FILE` (the brands table that `pick.py check`
compares against).
