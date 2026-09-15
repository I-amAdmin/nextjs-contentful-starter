# Vendored agent skills

Skills in this directory are copied ("vendored") from open-source projects. Each
directory is named after the `name:` field in its `SKILL.md`, which is the name
Claude Code uses to invoke the skill.

Three upstreams are vendored here. Two are MIT (`LICENSE-taste-skill`,
`LICENSE-emilkowalski-skills`); Impeccable is Apache 2.0 and keeps its license and
NOTICE inside its own skill directory.

---

## 1. emilkowalski/skill — design & animation

- Upstream: https://github.com/emilkowalski/skill
  (the project README refers to itself as `emilkowalski/skills`)
- License: MIT — Copyright (c) 2026 Emil Kowalski (`LICENSE-emilkowalski-skills`)
- Vendored from commit `85e8e2363b713506e1d5b6e07a0eb2da66be1bc3` (2026-09-15)
- Upstream install command: `npx skills@latest add emilkowalski/skills`

| Skill | What it does |
| --- | --- |
| `emil-design-eng` | The main skill: mostly animation, plus general design advice. |
| `animate` | Builds an animation from scratch — curve, duration, properties. |
| `animate-expo` | The same bar for React Native / Expo: gestures, sheets, haptics, off-thread motion. |
| `review-animations` | Strict review of existing animations against the author's rules. |
| `improve-animations` | Audits every animation in the codebase and emits prioritized, self-contained plans. |
| `find-animation-opportunities` | Finds UI that would genuinely benefit from motion — and what not to animate. |
| `animation-vocabulary` | The right words to ask an agent for the animation you actually want. |
| `apple-design` | Apple's interface and motion principles, distilled from WWDC design talks, for the web. |
| `mobile-native` | Makes a web app feel native on a phone: sticky hover, tap highlight, 100vh, input zoom, safe areas. |
| `pick-ui-library` | Picks a trusted library instead of hand-rolling or installing an abandoned package. |
| `prototype` | Builds several versions of a UI piece and lets you flip between them. |
| `ask-sonner` | Working with Sonner (the author's toast library): setup, styling, recipes, fixes. |
| `write-swift` | Modern Swift: value types, Swift 6 concurrency, generics, performance, Swift Testing. |

## 2. Leonxlnx/taste-skill — anti-slop frontend

- Upstream: https://github.com/Leonxlnx/taste-skill
- License: MIT — Copyright (c) 2026 Leonxlnx (`LICENSE-taste-skill`)
- Vendored from commit `ccbc15639c97057cbfcf32ecebc38ef716e4bb37` (2026-08-24)
- Upstream install command: `npx skills add https://github.com/Leonxlnx/taste-skill`

| Skill | Upstream folder | What it does |
| --- | --- | --- |
| `design-taste-frontend` | `skills/taste-skill` | Main skill, **v2 (upstream marks it experimental)**. Anti-slop frontend for landing pages, portfolios and redesigns. |
| `design-taste-frontend-v1` | `skills/taste-skill-v1` | The original v1, kept for backward compatibility. |
| `redesign-existing-projects` | `skills/redesign-skill` | Audits an existing site and upgrades it without breaking functionality. |
| `high-end-visual-design` | `skills/soft-skill` | Agency-grade type, spacing, shadows and motion defaults. |
| `minimalist-ui` | `skills/minimalist-skill` | Clean editorial style: warm monochrome, flat bento grids. |
| `industrial-brutalist-ui` | `skills/brutalist-skill` | Swiss print + military terminal aesthetic, rigid grids. |
| `gpt-taste` | `skills/gpt-tasteskill` | UX/UI plus GSAP motion engineering, AIDA page structure. |
| `stitch-design-taste` | `skills/stitch-skill` | Generates `DESIGN.md` design systems for Google Stitch. |
| `image-to-code` | `skills/image-to-code-skill` | Generate design images first, then implement code to match. |
| `imagegen-frontend-web` | `skills/imagegen-frontend-web` | Image generation only: one image per landing-page section. |
| `imagegen-frontend-mobile` | `skills/imagegen-frontend-mobile` | Image generation only: mobile app screen concepts. |
| `brandkit` | `skills/brandkit` | Image generation only: brand-guideline boards and logo systems. |
| `full-output-enforcement` | `skills/output-skill` | Blocks truncation and placeholder code in generated output. |

---

## 3. pbakaus/impeccable — design fluency (skill + agents)

- Upstream: https://github.com/pbakaus/impeccable · https://impeccable.style
- License: **Apache 2.0** — Paul Bakaus (kept as `impeccable/LICENSE` and `impeccable/NOTICE.md`)
- Vendored from commit `0a4e72a254f3b175c95b36b82e5f2e60fa63f116` (2026-09-15), plugin version 4.3.1
- Upstream install for Claude Code: `/plugin marketplace add pbakaus/impeccable`, then install it from `/plugin`

Unlike the two packs above, this is a single skill (`impeccable`) with 24 sub-commands,
plus four subagents in `../agents/`:

| Component | What it does |
| --- | --- |
| `impeccable` (skill) | Design direction, critique, audit, polish, harden, adapt, animate, typeset, colorize, live browser iteration. Invoke as `/impeccable <command> [target]`. |
| `impeccable-finish-reviewer` (agent) | Reviews a finished build against its direction contract and quality bar. |
| `impeccable-documenter` (agent) | Writes `DESIGN.md` from the shipped artifact. |
| `impeccable-asset-producer` (agent) | Produces reusable raster assets from approved mock references. |
| `impeccable-manual-edit-applier` (agent) | Applies live manual copy-edit batches back to source. |

### Hooks are deliberately NOT installed

Upstream ships `PostToolUse` (on `Edit`/`Write`) and `Stop` hooks that run
`skills/impeccable/scripts/impeccable hook`. That launcher executes an engine binary
which, if not already present, is downloaded on first run from
`https://github.com/pbakaus/impeccable/releases` into `~/.impeccable/bin/` and verified
against a `.sha256` sidecar before it runs.

Those hooks were **not** committed here, so nothing runs automatically and no binary is
fetched unless you invoke the skill yourself. To enable them later, add upstream's
`.claude/settings.json` from the same commit.

The skill's own `Setup` step also calls that launcher once per session. If the binary is
unavailable the skill says so and falls back to reading `PRODUCT.md` / `DESIGN.md`
directly, so it degrades rather than failing.

---

## Updating

Re-clone the upstream and re-copy each `skills/<folder>/` into the directory named
by its `SKILL.md` `name:` field, then bump the commit SHA recorded above:

```sh
git clone --depth 1 https://github.com/emilkowalski/skill /tmp/emil-skill
git clone --depth 1 https://github.com/Leonxlnx/taste-skill /tmp/taste-skill
git clone --depth 1 https://github.com/pbakaus/impeccable /tmp/impeccable
```

The upstream `npx skills add ...` commands install into `~/.claude/skills/` on a
single machine instead of into this repository.
