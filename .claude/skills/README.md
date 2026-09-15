# Vendored skills: taste-skill

These skills are vendored (copied) from the open-source **taste-skill** project.

- Upstream: https://github.com/Leonxlnx/taste-skill
- License: MIT — Copyright (c) 2026 Leonxlnx (see `LICENSE-taste-skill`)
- Vendored from commit `ccbc15639c97057cbfcf32ecebc38ef716e4bb37` (2026-08-24)

Each directory below is named after the `name:` field in its `SKILL.md`, which is the
name Claude Code uses to invoke the skill.

| Directory (skill name) | Upstream folder | What it does |
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

## Updating

```sh
git clone --depth 1 https://github.com/Leonxlnx/taste-skill /tmp/taste-skill
# then re-copy each skills/<folder>/ into the directory named by its SKILL.md `name:` field
```

Upstream also supports `npx skills add https://github.com/Leonxlnx/taste-skill`, which
installs into `~/.claude/skills/` instead of into this repository.
