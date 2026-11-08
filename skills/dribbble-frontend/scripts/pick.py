#!/usr/bin/env python3
"""Pick Dribbble reference shots for a frontend build (Nick's private library).

Usage:
  pick.py categories                       list categories with shot counts
  pick.py filter KEYWORD [KEYWORD ...]     list every shot whose search term, title or category name has all keywords
  pick.py pick "QUERY" [-n 4] [--seed S] [--kind web|mobile|any] [--grids] [--log SLUG] [--allow-reuse]
                                           N random fitting references (seeded, reproducible)
  pick.py sheet (--log SLUG [--pick K] | FILE ...) [--add SHOT ...] [--cols C] [-o OUT.jpg]
                                           contact sheet (ffmpeg) of a pick plus your build screenshots, for QA
  pick.py check --slug SLUG [--font F ...] [--palette "#hex,#hex"] [--archetype "words"] [--log]
                                           warn when planned fonts / colours / archetype clash with BRANDS.md
                                           or other projects' picks logs (exit 1 on a clash)
  pick.py lint SLUG                        list unfilled takes fields and a missing QA record in picks/SLUG.md
  pick.py write-categories                 regenerate references/categories.md from the indexes

Library: web-shots/ (individual 1800x1350 web shots), mobile-shots/ (individual 1800x1350 mobile shots) and
mobile/ (older search-page grid captures, used only with --grids or when no full-res mobile shot fits).

Matching: each query word is matched against a shot's categories (and their aliases), its Dribbble
search term and its shot title. Shots matching the most query words form the pool (widened one step
if the pool is small), then a seeded random sample is drawn: the first pick from the best-matching tier,
the rest from the whole pool, one shot per search first so the picks are varied. With --log SLUG the pick
is appended to design-references/picks/SLUG.md, and shots already logged for OTHER projects are excluded
unless --allow-reuse (keeps products distinct).

Library images are other designers' work: internal reference only. Never copy them into a repo.
"""
import argparse, datetime, math, os, random, re, shutil, subprocess, sys

LIB = os.environ.get('DRIBBBLE_LIB', '/Volumes/Extreme SSD/Projects/grokbot/design-references')
BRANDS = os.environ.get('DRIBBBLE_BRANDS') or os.environ.get('BRANDS_FILE') or os.path.join(os.path.dirname(LIB), 'BRANDS.md')
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.path.join(os.environ.get('TMPDIR') or '/Volumes/Extreme SSD/tmp-render', 'dribbble-sheets')

# category -> (description, aliases)
CATS = {
    'landing':      ('Marketing sites and landing pages: hero, proof, features, CTA', ['landing', 'homepage', 'marketing', 'website', 'site', 'hero', 'launch', 'startup']),
    'dashboard':    ('Data-dense app shells: sidebars, KPI rows, tables, charts', ['dashboard', 'admin', 'panel', 'console', 'analytics', 'backoffice']),
    'devtool':      ('Developer tools, docs, API, changelog, status, devops', ['dev', 'developer', 'devtool', 'api', 'docs', 'documentation', 'sdk', 'cli', 'changelog', 'status', 'devops', 'infra', 'technical']),
    'fintech':      ('Payments, banking, trading, pricing, checkout, money UI', ['fintech', 'finance', 'payment', 'payments', 'bank', 'banking', 'money', 'trading', 'invoice', 'checkout', 'pricing', 'payroll']),
    'crypto':       ('Web3, DeFi, wallets, NFTs, explorers, swaps', ['crypto', 'web3', 'defi', 'wallet', 'blockchain', 'nft', 'token', 'swap', 'explorer', 'zcash', 'near', 'onchain', 'dex', 'exchange']),
    'trading':      ('Trading terminals, perps, order books, DEX swaps, social trading', ['trading', 'trade', 'trader', 'terminal', 'perps', 'perp', 'perpetual', 'futures', 'orderbook', 'leverage', 'candlestick', 'swap', 'dex', 'exchange', 'copytrading']),
    'launchpad':    ('Token launchpads, memecoins, prediction markets: speculative boards', ['launchpad', 'launch', 'memecoin', 'meme', 'pump', 'presale', 'ido', 'bonding', 'prediction', 'polymarket', 'bet', 'betting', 'odds', 'market']),
    'stocks':       ('Stock trading and portfolio: tickers, watchlists, holdings', ['stock', 'stocks', 'equity', 'equities', 'broker', 'brokerage', 'portfolio', 'watchlist', 'invest', 'investing', 'investment', 'holdings', 'ticker']),
    'payments-consumer': ('Consumer payments: P2P, QR, tipping, donations, payment links', ['p2p', 'peer', 'send', 'tip', 'tipping', 'qr', 'scan', 'donation', 'donate', 'split', 'request', 'paylink', 'gateway', 'payment', 'payments']),
    'privacy':      ('Privacy, security, auth, vaults, keys', ['privacy', 'private', 'security', 'secure', 'cyber', 'cybersecurity', 'vault', 'password', 'auth', 'login', 'signin', 'key', 'keys', 'recovery', 'shielded', 'zk', 'quantum', 'pq']),
    'ai':           ('AI agents, assistants and chat surfaces', ['ai', 'agent', 'agents', 'assistant', 'llm', 'chat', 'copilot', 'mcp', 'bot']),
    'marketplace':  ('Marketplaces and commerce: auctions, listings, product pages, checkout', ['marketplace', 'auction', 'bid', 'bidding', 'ecommerce', 'shop', 'store', 'product', 'listing', 'checkout', 'commerce', 'realestate', 'property', 'travel', 'booking']),
    'creator':      ('Creator platforms: profiles, memberships, tips, fan pages', ['creator', 'creators', 'influencer', 'patreon', 'fan', 'fans', 'membership', 'subscription', 'profile', 'tip', 'tipping']),
    'games':        ('Game UI: HUDs, card games, leaderboards, game sites and mobile games', ['game', 'games', 'gaming', 'gamer', 'hud', 'leaderboard', 'arcade', 'esports', 'quest', 'level', 'cardgame', 'play', 'gamification']),
    'comics':       ('Comics, manga and webtoon readers and sites', ['comic', 'comics', 'manga', 'webtoon', 'reader', 'reading', 'anime', 'panel', 'issue']),
    'editorial':    ('Editorial, typographic, minimal, brutalist, retro, portfolio and agency sites', ['editorial', 'typography', 'type', 'minimal', 'brutalist', 'brutalism', 'neubrutalism', 'neobrutalism', 'brutal', 'retro', 'portfolio', 'agency', 'magazine', 'blog', 'serif', 'personal']),
    'illustration': ('Illustration-led pages: characters, mascots, hand-drawn art', ['illustration', 'illustrated', 'illustrative', 'character', 'mascot', 'playful', 'drawn', 'sticker']),
    'neon':         ('Neon, arcade, cyber and retro-futurist looks', ['neon', 'arcade', 'cyber', 'cyberpunk', 'synthwave', 'glow', 'pixel', 'futuristic']),
    'design-system':('Design systems, component sheets and micro-interactions', ['system', 'component', 'components', 'library', 'tokens', 'kit', 'uikit', 'micro', 'interaction', 'interactions', 'microinteraction', 'toggle', 'states']),
    'productivity': ('Work apps: kanban, calendar, files, email, CRM, HR, settings, onboarding', ['productivity', 'kanban', 'calendar', 'files', 'file', 'email', 'mail', 'crm', 'hr', 'settings', 'onboarding', 'project', 'tasks', 'workspace', 'saas', 'tool', 'b2b']),
    'social-media': ('Chat, feeds, video, music, gaming, streaming', ['social', 'feed', 'chat', 'messaging', 'video', 'music', 'player', 'gaming', 'game', 'streaming', 'community', 'podcast', 'media']),
    'data-viz':     ('Chart-led pages: analytics, maps, health metrics, explorers', ['data', 'chart', 'charts', 'viz', 'visualization', 'analytics', 'map', 'metrics', 'monitoring', 'health', 'stats', 'threat']),
    'flows':        ('Single-task screens: login, onboarding, checkout, settings, pricing, empty states', ['flow', 'flows', 'form', 'login', 'signup', 'onboarding', 'checkout', 'settings', 'pricing', 'empty', 'state', 'wizard', 'modal']),
    'onboarding-mobile': ('Phone onboarding and sign-in: welcome, wallet creation, email / passkey login', ['onboarding', 'welcome', 'signup', 'signin', 'login', 'passkey', 'passwordless', 'otp', 'email', 'backup', 'splash', 'intro']),
    '3d-motion':    ('3D heroes, motion, glass and expressive visuals', ['3d', 'motion', 'animation', 'animated', 'glass', 'glassmorphism', 'webgl', 'immersive', 'gaming']),
    'dark':         ('Dark-themed references', ['dark', 'night', 'black']),
    'consumer':     ('Consumer verticals: health, education, travel, real estate, music, reading', ['consumer', 'health', 'education', 'learning', 'course', 'travel', 'property', 'fitness', 'lifestyle']),
    'bento':        ('Bento grids and modular card layouts', ['bento', 'grid', 'cards', 'modular']),
    'sports':       ('Sports, betting and fantasy: scores, odds, picks, leagues', ['sports', 'sport', 'betting', 'bet', 'fantasy', 'league', 'odds', 'picks', 'scores', 'football', 'soccer', 'cricket', 'nba']),
    'personal-finance': ('Personal finance: budgets, spending, subscriptions, bills, receipts, tax', ['budget', 'budgeting', 'spending', 'expense', 'expenses', 'subscription', 'subscriptions', 'bill', 'bills', 'receipt', 'receipts', 'tax', 'insurance', 'savings', 'splitting']),
    'governance':   ('DAO governance, voting, staking and bridges: on-chain coordination screens', ['dao', 'governance', 'vote', 'voting', 'proposal', 'staking', 'stake', 'validator', 'bridge', 'crosschain']),
    'spatial':      ('VR, spatial and immersive UI: headsets, 3D panels, visionOS-like windows', ['vr', 'xr', 'ar', 'spatial', 'visionos', 'headset', 'immersive', 'metaverse']),
    'workflow':     ('Builders and power tools: node editors, workflow canvases, terminals, command palettes', ['node', 'nodes', 'workflow', 'builder', 'canvas', 'automation', 'terminal', 'command', 'palette', 'shortcut', 'graph']),
    'memory-companion': ('AI memory and companion surfaces: journals, recall, personal assistants, habits', ['memory', 'remember', 'recall', 'companion', 'journal', 'habit', 'habits', 'voice', 'personal']),
    'culture-style': ('Strong national or luxury styles: Japanese, Swiss, luxury, fashion, events', ['japanese', 'japan', 'swiss', 'luxury', 'premium', 'fashion', 'event', 'ticket', 'ticketing', 'hackathon', 'conference']),
    'mobile':       ('Phone-first references: full-res mobile shots (plus older grid captures)', ['mobile', 'ios', 'android', 'phone', 'app']),
}

# Dribbble search term -> categories (web w01-w88+, mobile m01-m46+, plus spares the fetcher may use).
# A fetched term missing here falls back to 'landing' (web) or 'mobile' only, and write-categories warns.
TERM_CATS = {
    'crypto landing page': ['landing', 'crypto'], 'fintech landing page': ['landing', 'fintech'],
    'web3 website': ['landing', 'crypto'], 'defi dashboard': ['dashboard', 'crypto', 'fintech'],
    'developer tool landing page': ['landing', 'devtool'], 'saas landing page dark': ['landing', 'dark', 'productivity'],
    'ai agent website': ['landing', 'ai'], 'cybersecurity landing page': ['landing', 'privacy'],
    'data visualization dashboard': ['dashboard', 'data-viz'], 'analytics dashboard dark': ['dashboard', 'data-viz', 'dark'],
    'crypto wallet website': ['landing', 'crypto', 'fintech'], 'payment website': ['landing', 'fintech', 'payments-consumer'],
    'api documentation website': ['devtool', 'editorial'], 'website motion design': ['landing', '3d-motion'],
    '3d hero section': ['landing', '3d-motion'], 'editorial website': ['editorial'], 'minimal website': ['editorial', 'landing'],
    'brutalist website': ['editorial'], 'auction website': ['marketplace'], 'nft marketplace website': ['marketplace', 'crypto'],
    'blockchain explorer': ['crypto', 'data-viz', 'dashboard'], 'trading platform website': ['fintech', 'crypto', 'dashboard', 'trading'],
    'banking website': ['landing', 'fintech'], 'privacy website': ['landing', 'privacy'], 'admin dashboard': ['dashboard'],
    'bento grid website': ['landing', 'bento'], 'product launch website': ['landing'], 'startup landing page': ['landing'],
    'typography website': ['editorial'], 'dark landing page': ['landing', 'dark'],
    # w31-w62
    'ai chat interface': ['ai', 'social-media'], 'saas pricing page': ['flows', 'fintech', 'landing'],
    'onboarding flow web': ['flows', 'productivity'], 'settings page web': ['flows', 'productivity', 'dashboard'],
    'kanban board': ['productivity', 'dashboard'], 'calendar app web': ['productivity'], 'file manager dashboard': ['productivity', 'dashboard'],
    'ecommerce product page': ['marketplace'], 'checkout page': ['flows', 'marketplace', 'fintech'],
    'music player web': ['social-media', 'consumer'], 'map dashboard': ['dashboard', 'data-viz'], 'health dashboard': ['dashboard', 'data-viz', 'consumer'],
    'education platform': ['consumer', 'landing'], 'portfolio website': ['editorial'], 'agency website': ['editorial', 'landing'],
    'glassmorphism dashboard': ['dashboard', '3d-motion'], 'retro website': ['editorial'], 'gaming website': ['social-media', '3d-motion', 'landing', 'games'],
    'devops dashboard': ['devtool', 'dashboard', 'data-viz'], 'crm dashboard': ['dashboard', 'productivity'],
    'chat app web': ['social-media', 'ai'], 'email client web': ['productivity'], 'social feed web': ['social-media'],
    'video platform web': ['social-media'], 'changelog page': ['devtool', 'editorial'], 'status page': ['devtool', 'data-viz'],
    'login page': ['flows', 'privacy'], 'real estate website': ['marketplace', 'consumer', 'landing'], 'travel website': ['consumer', 'marketplace', 'landing'],
    'hr dashboard': ['dashboard', 'productivity'], 'project management dashboard': ['dashboard', 'productivity'],
    'invoice dashboard': ['dashboard', 'fintech'], 'logistics dashboard': ['dashboard', 'data-viz'], 'fitness website': ['consumer', 'landing'],
    'restaurant website': ['consumer', 'landing'], 'podcast website': ['social-media', 'landing'], 'nonprofit website': ['landing', 'editorial'],
    'search results page': ['flows', 'marketplace'], 'empty state web': ['flows'], 'knowledge base website': ['devtool', 'editorial'],
    'neubrutalism website': ['editorial', 'illustration', 'landing'], 'neo brutalism ui': ['editorial', 'illustration', 'design-system'],
    'neubrutalism dashboard': ['editorial', 'dashboard'], 'neubrutalism landing page': ['editorial', 'landing'],
    'neo brutalism website': ['editorial', 'landing'], 'neubrutalism app': ['editorial', 'mobile'],
    # w63+ (Oct 30): trading, launchpads, games, comics, creators, consumer payments, stocks, AI, systems
    'crypto trading terminal': ['trading', 'crypto', 'dashboard', 'data-viz'], 'perps trading dashboard': ['trading', 'crypto', 'dashboard'],
    'dex swap interface': ['trading', 'crypto', 'flows'], 'token launchpad': ['launchpad', 'crypto', 'marketplace'],
    'memecoin website': ['launchpad', 'crypto', 'landing', 'illustration'], 'prediction market website': ['launchpad', 'trading', 'crypto'],
    'prediction market': ['launchpad', 'trading', 'crypto'],
    'card game ui': ['games', 'illustration'], 'game hud': ['games', '3d-motion'], 'game leaderboard': ['games', 'data-viz'],
    'manga website': ['comics', 'editorial', 'consumer'], 'comic website': ['comics', 'editorial', 'illustration'],
    'webtoon website': ['comics', 'editorial', 'consumer'], 'creator platform': ['creator', 'social-media', 'landing'],
    'social trading platform': ['trading', 'social-media', 'fintech'], 'ai agent dashboard': ['ai', 'dashboard'],
    'ai marketplace': ['ai', 'marketplace'], 'design system components': ['design-system'], 'micro interactions': ['design-system', '3d-motion'],
    'illustration landing page': ['illustration', 'landing'], 'neon ui': ['neon', 'dark'], 'arcade website': ['neon', 'games', 'landing'],
    'stock trading dashboard': ['stocks', 'trading', 'dashboard', 'fintech'], 'stock portfolio dashboard': ['stocks', 'dashboard', 'fintech', 'data-viz'],
    'crypto onboarding': ['flows', 'crypto', 'onboarding-mobile'], 'wallet login': ['flows', 'crypto', 'privacy'],
    'donation page': ['payments-consumer', 'flows', 'fintech'], 'crypto payment gateway': ['payments-consumer', 'crypto', 'fintech', 'landing'],
    'order book ui': ['trading', 'crypto', 'dashboard'], 'nft launchpad': ['launchpad', 'crypto', 'marketplace'],
    'web3 game website': ['games', 'crypto', 'landing'], 'esports website': ['games', 'landing'], 'pixel art website': ['neon', 'games', 'illustration'],
    'trading bot dashboard': ['trading', 'ai', 'dashboard'], 'crypto exchange dashboard': ['trading', 'crypto', 'dashboard'],
    'gamification ui': ['games', 'design-system'], 'quest dashboard': ['games', 'dashboard', 'crypto'], 'ai agent platform': ['ai', 'landing'],
    'payment link page': ['payments-consumer', 'flows'], 'mascot website': ['illustration', 'landing'], 'cyberpunk ui': ['neon', 'dark'],
    'component library': ['design-system', 'devtool'], 'ui components': ['design-system'],
    # mobile m01-m30 (grid captures in mobile/, full-res shots in mobile-shots/)
    'crypto wallet app': ['crypto', 'fintech'], 'fintech app': ['fintech'], 'banking app': ['fintech'], 'payment app': ['fintech', 'payments-consumer'],
    'trading app': ['fintech', 'crypto', 'data-viz', 'trading'], 'defi mobile app': ['crypto', 'fintech'], 'web3 mobile app': ['crypto'],
    'security app': ['privacy'], 'password manager app': ['privacy'], 'ai assistant app': ['ai'], 'chat app': ['social-media', 'ai'],
    'onboarding mobile': ['flows', 'onboarding-mobile'], 'dashboard mobile app': ['dashboard', 'data-viz'], 'finance tracker app': ['fintech', 'data-viz'],
    'auction app': ['marketplace'], 'nft app': ['crypto', 'marketplace'], 'swap app': ['crypto', 'fintech', 'flows', 'trading'],
    'crypto exchange app': ['crypto', 'fintech', 'trading'], 'crypto portfolio app': ['crypto', 'fintech', 'data-viz'], 'mobile card ui': ['fintech', 'bento'],
    'transaction history app': ['fintech', 'data-viz'], 'settings screen app': ['flows', 'productivity'], 'empty state mobile': ['flows'],
    'dark mode app': ['dark'], 'ios app design': [], 'android app design': [], 'mobile app animation': ['3d-motion', 'design-system'],
    'splash screen app': ['flows', '3d-motion', 'onboarding-mobile'], 'ios widget': ['bento', 'data-viz'], 'wallet onboarding': ['crypto', 'flows', 'onboarding-mobile'],
    # mobile m31+ (Oct 30)
    'mobile game ui': ['games', 'illustration'], 'comic reader app': ['comics', 'consumer'], 'manga app': ['comics', 'consumer'],
    'webtoon app': ['comics', 'consumer'], 'prediction market app': ['launchpad', 'trading', 'crypto'],
    'tipping app': ['payments-consumer', 'creator', 'fintech'], 'p2p payment app': ['payments-consumer', 'fintech'],
    'qr payment app': ['payments-consumer', 'fintech', 'flows'], 'crypto onboarding app': ['onboarding-mobile', 'crypto', 'flows'],
    'passwordless login app': ['onboarding-mobile', 'privacy', 'flows'], 'wallet login app': ['onboarding-mobile', 'crypto', 'privacy'],
    'login screen app': ['onboarding-mobile', 'privacy', 'flows'],
    'stock trading app': ['stocks', 'trading', 'fintech'], 'stock portfolio app': ['stocks', 'fintech', 'data-viz'],
    'investment app': ['stocks', 'fintech'], 'social trading app': ['trading', 'social-media', 'fintech'],
    'card game app': ['games', 'illustration'], 'memecoin app': ['launchpad', 'crypto'], 'launchpad app': ['launchpad', 'crypto'],
    'perps trading app': ['trading', 'crypto'], 'dex app': ['trading', 'crypto'], 'ai agent app': ['ai'],
    'creator app': ['creator', 'social-media'], 'game leaderboard app': ['games', 'data-viz'],
    'split bill app': ['payments-consumer', 'fintech'], 'send money app': ['payments-consumer', 'fintech'],
    # Nov 8 2026 searches (w89+, m47+), including spares.
    'sports betting website': ['sports', 'launchpad', 'landing'], 'fantasy sports dashboard': ['sports', 'dashboard', 'games'],
    'personal finance dashboard': ['personal-finance', 'dashboard', 'fintech'], 'budget app web': ['personal-finance', 'fintech', 'dashboard'],
    'ai memory app': ['memory-companion', 'ai'], 'ai companion website': ['memory-companion', 'ai', 'landing'],
    'dao governance dashboard': ['governance', 'dashboard', 'crypto'], 'staking dashboard': ['governance', 'dashboard', 'crypto'],
    'crypto bridge interface': ['governance', 'crypto', 'flows'], 'node editor ui': ['workflow', 'devtool'],
    'workflow builder ui': ['workflow', 'productivity'], 'terminal ui': ['workflow', 'devtool', 'dark'],
    'command palette': ['workflow', 'design-system', 'flows'], 'japanese website': ['culture-style', 'editorial', 'landing'],
    'swiss design website': ['culture-style', 'editorial', 'landing'], 'luxury website': ['culture-style', 'landing', 'editorial'],
    'event ticketing website': ['culture-style', 'marketplace', 'landing'], 'hackathon website': ['culture-style', 'devtool', 'landing'],
    'vr website': ['spatial', '3d-motion', 'landing'], 'spatial ui': ['spatial', '3d-motion'],
    'insurance website': ['personal-finance', 'fintech', 'landing'], 'subscription management dashboard': ['personal-finance', 'dashboard', 'fintech'],
    'notification center ui': ['design-system', 'flows', 'productivity'], 'leaderboard dashboard': ['games', 'dashboard', 'data-viz'],
    'tax dashboard': ['personal-finance', 'dashboard', 'fintech'], 'receipt ui': ['personal-finance', 'flows', 'fintech'],
    'vault website': ['privacy', 'landing'], 'sports dashboard': ['sports', 'dashboard', 'data-viz'],
    'web3 game landing': ['games', 'crypto', 'landing'], 'fashion ecommerce': ['culture-style', 'marketplace'],
    'blog website': ['editorial', 'landing'], 'pricing table': ['flows', 'fintech', 'design-system'],
    'sports betting app': ['sports', 'launchpad'], 'fantasy sports app': ['sports', 'games'],
    'budget app': ['personal-finance', 'fintech'], 'habit tracker app': ['memory-companion', 'consumer', 'productivity'],
    'ai companion app': ['memory-companion', 'ai'], 'voice assistant app': ['memory-companion', 'ai'],
    'health app': ['consumer', 'data-viz'], 'travel app': ['consumer', 'marketplace'],
    'food delivery app': ['consumer', 'marketplace'], 'music app': ['social-media', 'consumer'],
    'staking app': ['governance', 'crypto'], 'crypto bridge app': ['governance', 'crypto', 'flows'],
    'dao voting app': ['governance', 'crypto'], 'notification design app': ['design-system', 'flows'],
    'receipt app': ['personal-finance', 'fintech'], 'bill splitting app': ['personal-finance', 'payments-consumer'],
    'social app': ['social-media'], 'camera app': ['consumer'], 'calendar app': ['productivity'],
    'subscription tracker app': ['personal-finance', 'fintech'], 'event ticket app': ['culture-style', 'marketplace'],
}


def _rows(path, kind, folder):
    """Individual-shot index rows: | `file` | term | [title](link) | author |"""
    if not os.path.exists(path): return []
    out = []
    for m in re.finditer(r'^\| `(([wm]\d+)-\d+-[^`]+)` \| ([^|]+) \| \[(.*)\]\((https://dribbble\.com/shots/[^)]+)\) \| (.*) \|$', open(path, encoding='utf8').read(), re.M):
        f, sid, term, title, link, author = m.groups()
        out.append(dict(kind=kind, grid=False, id=sid, file=os.path.join(LIB, folder, f), term=term.strip(), title=title.strip(),
                        link=link, author=author.strip()))
    return out


def load():
    shots = _rows(os.path.join(LIB, 'web-shots', 'INDEX.md'), 'web', 'web-shots')
    shots += _rows(os.path.join(LIB, 'mobile-shots', 'INDEX.md'), 'mobile', 'mobile-shots')
    for m in re.finditer(r'^\| (m\d+) \| ([^|]+) \| \[[^\]]+\]\(([^)]+)\) \| (.+) \|$', open(os.path.join(LIB, 'mobile', 'INDEX.md'), encoding='utf8').read(), re.M):
        sid, term, link, files = m.groups()
        for f in re.findall(r'`([^`]+)`', files):
            shots.append(dict(kind='mobile', grid=True, id=sid, file=os.path.join(LIB, 'mobile', f), term=term.strip(),
                              title=f'search-page capture: {term.strip()}', link=link, author='(multiple)'))
    for s in shots:
        cats = list(TERM_CATS.get(s['term'], []))
        t = s['title'].lower()
        if 'dark' in t and 'dark' not in cats: cats.append('dark')
        if s['kind'] == 'mobile' and 'mobile' not in cats: cats.append('mobile')
        s['cats'] = cats or ['landing']
    return shots


def norm(w):
    w = w.lower().strip()
    return w[:-1] if len(w) > 3 and w.endswith('s') and not w.endswith('ss') else w


def words(text):
    return {norm(w) for w in re.findall(r'[a-z0-9]+', text.lower())}


def score(shot, q, aliases=True):
    vocab = words(shot['term']) | words(shot['title'])
    for c in shot['cats']:
        vocab |= {norm(c)} | words(c) | ({norm(a) for a in CATS[c][1]} if aliases else set())
    return sum(1 for w in q if w in vocab)


def picks_dir():
    return os.path.join(LIB, 'picks')


def used_by_others(slug):
    d = picks_dir(); used = set()
    if not os.path.isdir(d): return used
    for f in os.listdir(d):
        if f.endswith('.md') and f[:-3] != slug:
            used |= set(re.findall(r'(/Volumes/[^`\n]+\.jpg)', open(os.path.join(d, f), encoding='utf8').read()))
    return used


def pick(shots, query, n, seed, kind, slug, allow_reuse, grids):
    q = [w for w in words(query) if w not in {'a', 'an', 'the', 'for', 'and', 'with', 'page', 'ui', 'design'}]
    if not q: sys.exit('empty query')
    if kind != 'any': shots = [s for s in shots if s['kind'] == kind]
    if slug and not allow_reuse:
        used = used_by_others(slug); shots = [s for s in shots if s['file'] not in used]
    shots = [s for s in shots if os.path.exists(s['file'])]
    if not grids:   # prefer full-res mobile shots: grid captures only when no full-res shot fits
        full = [s for s in shots if not s['grid']]
        if sum(score(s, q) > 0 for s in full) >= n: shots = full
    scored = [(score(s, q), s) for s in shots]
    best = max((sc for sc, _ in scored), default=0)
    if best == 0: sys.exit(f'no reference matches "{query}"; try `pick.py categories`')
    floor = best
    pool = [s for sc, s in scored if sc >= floor]
    while len(pool) < n * 3 and floor > 1:
        floor -= 1; pool = [s for sc, s in scored if sc >= floor]
    rng = random.Random(seed)
    rng.shuffle(pool)
    top = [s for s in pool if score(s, q) == best]
    pool = [top[0]] + [s for s in pool if s is not top[0]]   # slot 1 always comes from the best-matching tier
    out, seen_terms = [], set()
    for s in pool:                       # first pass: one shot per search term
        if len(out) < n and (s['kind'], s['term']) not in seen_terms: out.append(s); seen_terms.add((s['kind'], s['term']))
    for s in pool:                       # fill if the pool has fewer distinct searches than n
        if len(out) < n and s not in out: out.append(s)
    return q, best, floor, len(pool), out


TAKES = '''  - takes (replace every __; write "n/a" where the shot shows nothing):
    - grid: __ columns, max width __px, gutter __px, side margin __px (375: __px); hero = __% of the fold
    - type: display __px / weight __ / tracking __em / line-height __; h2 __px; body __px/__; label __px caps?; mono __
    - spacing scale: __ (e.g. 4 8 12 16 24 32 48 64 96); section padding __px; card padding __px
    - shape: radius cards __px, buttons __px, inputs __px; borders __px __colour; shadow __ (none / hard __px offset / y__ blur__ __%)
    - motion: what moves __; duration __ms; easing __; reduced-motion fallback __
    - palette: bg __, surface __, ink __, accent(s) __; light/dark __; contrast of body text __:1
    - components: nav __; cards __; table/list __; buttons __; inputs __; empty/error state __
    - this product does differently: __
'''


def write_categories(shots):
    nweb = sum(s['kind'] == 'web' for s in shots); nmob = sum(s['kind'] == 'mobile' and not s['grid'] for s in shots)
    ngrid = sum(s['grid'] for s in shots)
    lines = ['# Reference categories', '',
             f'Generated by `scripts/pick.py write-categories` on {datetime.date.today()} from `{LIB}/web-shots/INDEX.md`, `mobile-shots/INDEX.md` and `mobile/INDEX.md`.',
             f'{nweb} web shots and {nmob} mobile shots (individual, 1800x1350), plus {ngrid} older mobile search-page grid captures',
             '(the picker uses grids only with `--grids` or when no full-res shot fits).',
             'A shot can sit in several categories. Paths are relative to the library root above.',
             'Other designers\' work: internal reference only.', '',
             '| Category | What it covers | Web | Mobile | Grids |', '|---|---|---|---|---|']
    for c, (desc, _) in CATS.items():
        cnt = lambda k, g: sum(s['kind'] == k and s['grid'] == g and c in s['cats'] for s in shots)
        lines.append(f'| [{c}](#{c}) | {desc} | {cnt("web", False)} | {cnt("mobile", False)} | {cnt("mobile", True)} |')
    for c, (desc, aliases) in CATS.items():
        members = [s for s in shots if c in s['cats']]
        lines += ['', f'## {c}', '', f'{desc}. Matched by: {", ".join(aliases)}.', '']
        by_term = {}
        for s in members: by_term.setdefault((s['id'], s['term'], s['kind'], s['grid']), []).append(s)
        for (sid, term, kind, grid), ss in by_term.items():
            files = ', '.join(f'`{os.path.relpath(s["file"], LIB)}`' for s in ss)
            lines.append(f'- **{sid} {term}** ({"mobile grid" if grid else kind}): {files}')
    path = os.path.join(SKILL, 'references', 'categories.md')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf8').write('\n'.join(lines) + '\n')
    print('wrote', path)
    missing = sorted({s['term'] for s in shots if s['term'] not in TERM_CATS})
    if missing: print('WARNING: search terms with no TERM_CATS entry (add them):', ', '.join(missing), file=sys.stderr)


# ---------- sheet ----------
def last_pick_files(slug, k):
    p = os.path.join(picks_dir(), f'{slug}.md')
    if not os.path.exists(p): sys.exit(f'no picks log {p}')
    blocks = re.split(r'^## ', open(p, encoding='utf8').read(), flags=re.M)
    blocks = [b for b in blocks if re.match(r'\S+ pick:', b)]
    if not blocks: sys.exit(f'no pick in {p}')
    b = blocks[k]
    return re.findall(r'`(/Volumes/[^`]+\.(?:jpg|png))`', b)


def dims(f):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', f],
                       capture_output=True, text=True).stdout.strip().split(',')
    return int(o[0]), int(o[1])


def sheet(files, cols, tile, out):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'): sys.exit('ffmpeg/ffprobe not found')
    files = [f for f in files if os.path.exists(f) or print(f'missing, skipped: {f}', file=sys.stderr)]
    if not files: sys.exit('no images')
    tw, th = tile; gap = 12
    cols = cols or min(4, math.ceil(math.sqrt(len(files))))
    rows = math.ceil(len(files) / cols)
    args, chains, layout = ['ffmpeg', '-v', 'error', '-y'], [], []
    for i, f in enumerate(files):
        w, h = dims(f)
        crop = ''
        if w >= 800 and h > w: crop = f'crop={w}:{int(w * 0.75)}:0:0,'           # desktop full-page: keep the first screen
        elif w < 800 and h > w * 2.3: crop = f'crop={w}:{int(w * 2.17)}:0:0,'    # phone full-page: keep the first screen
        args += ['-i', f]
        chains.append(f'[{i}:v]format=rgb24,{crop}scale={tw - gap}:{th - gap}:force_original_aspect_ratio=decrease,'
                      f'pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2:color=0x202124,setsar=1[t{i}]')
        layout.append(f'{(i % cols) * tw}_{(i // cols) * th}')
    if len(files) == 1:
        graph = chains[0].replace('[t0]', '')
    else:
        graph = ';'.join(chains) + ';' + ''.join(f'[t{i}]' for i in range(len(files))) + \
                f'xstack=inputs={len(files)}:layout={"|".join(layout)}:fill=0x202124'
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    r = subprocess.run(args + ['-filter_complex', graph, '-frames:v', '1', '-q:v', '3', out], capture_output=True, text=True)
    if r.returncode: sys.exit('ffmpeg failed: ' + r.stderr[-800:])
    legend = '\n'.join(f'{i + 1}. row {i // cols + 1} col {i % cols + 1}: {f}' for i, f in enumerate(files))
    open(os.path.splitext(out)[0] + '.txt', 'w', encoding='utf8').write(legend + '\n')
    print(f'wrote {out} ({cols}x{rows} tiles of {tw}x{th}); open it with the Read tool\n{legend}')


# ---------- distinctness check ----------
STOP = {'the', 'and', 'with', 'from', 'that', 'this', 'each', 'into', 'over', 'made', 'literal', 'page', 'site', 'landing',
        'light', 'dark', 'real', 'live', 'one', 'only', 'card', 'cards', 'panel', 'panels', 'hero', 'style', 'grid', 'look'}
BANNED_FONTS = {'inter tight': 'Polaris uses it (BRANDS.md: never Inter Tight)'}


def clean_font(f):
    return re.sub(r'\s*\(.*?\)', '', f).strip().strip('*').strip().lower()


def hex_rgb(h):
    h = h.lstrip('#'); h = ''.join(c * 2 for c in h) if len(h) == 3 else h
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lab(rgb):
    def lin(c):
        c /= 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(lin, rgb)
    x, y, z = (r * .4124 + g * .3576 + b * .1805) / .95047, r * .2126 + g * .7152 + b * .0722, (r * .0193 + g * .1192 + b * .9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(a, b):
    return math.dist(lab(hex_rgb(a)), lab(hex_rgb(b)))


def sig_words(t):
    return {norm(w) for w in re.findall(r'[a-z]{4,}', t.lower())} - STOP


def brand_rows():
    """(brand, fonts, hexes, archetype) from every table in BRANDS.md that has a font column."""
    if not os.path.exists(BRANDS): return []
    rows, header = [], None
    for line in open(BRANDS, encoding='utf8'):
        if not line.startswith('|'): header = None; continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if header is None: header = [c.lower() for c in cells]; continue
        if set(''.join(cells)) <= set('-: '): continue
        fcols = [i for i, h in enumerate(header) if re.search(r'\b(font|sans|mono|display)\b', h)]
        if not fcols: continue
        acol = next((i for i, h in enumerate(header) if 'archetype' in h), None)
        brand = re.sub(r'[*`]', '', cells[0]).split('(')[0].strip()
        fonts = {clean_font(cells[i]) for i in fcols if i < len(cells) and cells[i] and 'keep current' not in cells[i].lower()}
        hexes = set(h.lower() for h in re.findall(r'#[0-9a-fA-F]{6}\b', line))
        arch = cells[acol] if acol is not None and acol < len(cells) else ''
        rows.append((brand, fonts, hexes, arch))
    return rows


def strip_takes(text):
    """Drop takes blocks (notes about the references' own fonts and colours), keep plans and 'differently' notes."""
    keep, in_takes = [], False
    for l in text.splitlines():
        if l.lstrip().startswith('- takes'): in_takes = True; continue
        if in_takes and l.startswith('    '): continue
        in_takes = False; keep.append(l)
    return '\n'.join(keep)


def check(slug, fonts, palette, archetype, brand, log):
    fonts = [f for f in fonts if f.strip()]
    palette = [p.strip().lower() for p in re.split(r'[,\s]+', palette or '') if re.fullmatch(r'#[0-9a-fA-F]{6}', p.strip())]
    me = (brand or slug.split('-')[0]).lower()
    clashes, notes = [], []
    for f in fonts:
        if clean_font(f) in BANNED_FONTS: clashes.append(f'font "{f}": {BANNED_FONTS[clean_font(f)]}')
    for b, bfonts, bhex, barch in brand_rows():
        if b.lower() == me or b.lower().startswith(me + ' '): continue
        for f in fonts:
            if clean_font(f) in bfonts: clashes.append(f'font "{f}" is already {b}\'s (BRANDS.md: a font appears in exactly one product)')
        for p in palette:
            for h in bhex:
                d = delta_e(p, h)
                if d < 1: clashes.append(f'colour {p} is {b}\'s {h} exactly')
                elif d < 10: notes.append(f'colour {p} is close to {b}\'s {h} (deltaE {d:.1f})')
        if archetype and barch:
            head = re.split(r'[:.;]', barch)[0]
            shared = sig_words(archetype) & sig_words(head)
            if shared: clashes.append(f'archetype shares "{", ".join(sorted(shared))}" with {b}: "{head[:90]}"')
            else:
                shared = sig_words(archetype) & sig_words(barch)
                if len(shared) >= 3: notes.append(f'archetype overlaps {b} on {", ".join(sorted(shared))}')
    d = picks_dir()
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        other = fn[:-3]
        if not fn.endswith('.md') or other == slug or other.split('-')[0] == me: continue
        text = strip_takes(open(os.path.join(d, fn), encoding='utf8').read())
        for f in fonts:
            if re.search(r'(?<![\w-])' + re.escape(clean_font(f)) + r'(?![\w-])', text.lower()):
                clashes.append(f'font "{f}" is named in picks/{fn}')
        for p in palette:
            for h in set(x.lower() for x in re.findall(r'#[0-9a-fA-F]{6}\b', text)):
                dd = delta_e(p, h)
                if dd < 1: clashes.append(f'colour {p} is used in picks/{fn}')
                elif dd < 10: notes.append(f'colour {p} is close to {h} in picks/{fn} (deltaE {dd:.1f})')
        if archetype:
            for m in re.finditer(r'^- plan: .*archetype=(.*)$', text, re.M):
                shared = sig_words(archetype) & sig_words(m.group(1))
                if shared: clashes.append(f'archetype shares "{", ".join(sorted(shared))}" with the plan in picks/{fn}')
            shared = sig_words(archetype) & sig_words(text)
            if len(shared) >= 2: notes.append(f'archetype words {", ".join(sorted(shared))} also appear in picks/{fn}: read its plan')
    print(f'check for {slug}: fonts={fonts or "-"} palette={palette or "-"} archetype="{archetype or "-"}"')
    for c in dict.fromkeys(clashes): print('  CLASH ' + c)
    for n in dict.fromkeys(notes): print('  near  ' + n)
    if not clashes and not notes: print('  ok: nothing in BRANDS.md or other picks logs clashes')
    if log:
        with open(os.path.join(d, f'{slug}.md'), 'a', encoding='utf8') as fh:
            fh.write(f'\n### Plan ({datetime.date.today()})\n- plan: fonts={", ".join(fonts)}; palette={", ".join(palette)}; archetype={archetype or ""}\n'
                     f'- check: {"CLASH: " + "; ".join(dict.fromkeys(clashes)) if clashes else "no clash"}\n')
        print(f'logged the plan to {d}/{slug}.md')
    return 1 if clashes else 0


def lint(slug):
    p = os.path.join(picks_dir(), f'{slug}.md')
    if not os.path.exists(p): sys.exit(f'no picks log {p}')
    text = open(p, encoding='utf8').read(); bad = 0
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r'takes: TODO|(?<!_)__(?!_)', line): print(f'{p}:{i}: unfilled: {line.strip()[:100]}'); bad += 1
    if '### QA' not in text and '### qa' not in text.lower(): print(f'{p}: no "### QA" record yet (see SKILL.md step 8)'); bad += 1
    if '### Plan' not in text: print(f'{p}: no "### Plan" from `pick.py check --log` (optional but recommended)')
    print('ok' if not bad else f'{bad} item(s) to fill')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('categories'); sub.add_parser('write-categories')
    f = sub.add_parser('filter'); f.add_argument('keywords', nargs='+')
    p = sub.add_parser('pick'); p.add_argument('query'); p.add_argument('-n', type=int, default=4)
    p.add_argument('--seed'); p.add_argument('--kind', choices=['web', 'mobile', 'any'], default='any')
    p.add_argument('--grids', action='store_true', help='also draw from the old mobile search-page grid captures')
    p.add_argument('--log', metavar='SLUG'); p.add_argument('--allow-reuse', action='store_true')
    s = sub.add_parser('sheet'); s.add_argument('files', nargs='*'); s.add_argument('--log', metavar='SLUG')
    s.add_argument('--pick', type=int, default=-1, help='which pick in the log (0 = first, -1 = latest)')
    s.add_argument('--add', nargs='+', default=[], metavar='SHOT', help='build screenshots to place after the references')
    s.add_argument('--cols', type=int); s.add_argument('--tile', default='900x675'); s.add_argument('-o', '--out')
    c = sub.add_parser('check'); c.add_argument('--slug', required=True); c.add_argument('--font', action='append', default=[])
    c.add_argument('--palette'); c.add_argument('--archetype'); c.add_argument('--brand', help='brand name in BRANDS.md to ignore (default: first slug word)')
    c.add_argument('--log', action='store_true', help='append the plan and the result to picks/SLUG.md')
    l = sub.add_parser('lint'); l.add_argument('slug')
    a = ap.parse_args()
    if a.cmd == 'sheet':
        files = (last_pick_files(a.log, a.pick) if a.log else []) + a.files + a.add
        tw, th = (int(x) for x in a.tile.lower().split('x'))
        name = a.log or 'sheet'
        sheet(files, a.cols, (tw, th), a.out or os.path.join(SHEETS, f'{name}-{datetime.datetime.now():%Y%m%d-%H%M%S}.jpg'))
        return
    if a.cmd == 'check': sys.exit(check(a.slug, a.font, a.palette, a.archetype, a.brand, a.log))
    if a.cmd == 'lint': sys.exit(lint(a.slug))
    shots = load()
    nweb = sum(s['kind'] == 'web' for s in shots); nmob = sum(s['kind'] == 'mobile' and not s['grid'] for s in shots)
    ngrid = sum(s['grid'] for s in shots)
    if a.cmd == 'categories':
        print(f'{len(shots)} references ({nweb} web shots, {nmob} mobile shots, {ngrid} mobile grid captures)')
        for c, (desc, aliases) in CATS.items():
            print(f'  {c:17} {sum(c in s["cats"] and not s["grid"] for s in shots):4}  {desc}')
    elif a.cmd == 'write-categories':
        write_categories(shots)
    elif a.cmd == 'filter':
        q = {norm(k) for k in a.keywords}
        hits = [s for s in shots if score(s, q, aliases=False) == len(q)]  # literal: term, title or category name
        for s in hits: print(f'{s["file"]}\t{s["term"]}\t{s["title"]}\t{s["author"]}')
        print(f'{len(hits)} matches', file=sys.stderr)
    else:
        seed = a.seed or str(random.SystemRandom().randrange(10**6))
        q, best, floor, pool, out = pick(shots, a.query, a.n, seed, a.kind, a.log, a.allow_reuse, a.grids)
        print(f'query: "{a.query}"  words: {sorted(q)}  seed: {seed}  pool: {pool} shots (score {floor}-{best} of {len(q)})')
        print(f'reproduce: pick.py pick "{a.query}" -n {a.n} --seed {seed}' + (f' --kind {a.kind}' if a.kind != 'any' else '') + (' --grids' if a.grids else ''))
        for i, s in enumerate(out, 1):
            print(f'{i}. {s["file"]}\n   [{"mobile grid" if s["grid"] else s["kind"]}] {s["term"]} | {s["title"]} | {s["author"]} | {s["link"]} | cats: {", ".join(s["cats"])}')
        if a.log:
            d = picks_dir(); os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f'{a.log}.md'), 'a', encoding='utf8') as fh:
                fh.write(f'\n## {datetime.date.today()} pick: "{a.query}" (seed {seed})\n\n' +
                         ''.join(f'- `{s["file"]}` ({s["term"]}: {s["title"]}, {s["author"]})\n{TAKES}' for s in out))
            print(f'logged to {d}/{a.log}.md (fill in every __ in the "takes" blocks; `pick.py lint {a.log}` lists what is left)')


if __name__ == '__main__':
    main()
