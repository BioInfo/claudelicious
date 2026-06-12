---
name: designing-frontend-uis
description: "Build or improve any frontend UI (component, page, app, dashboard, landing, marketing site) so it does not look like generic AI output. Enforces a brief-read, three dials, and a countable pre-flight gate instead of vague 'be distinctive' advice. Invoke when the user asks to build/create/redesign/improve a web UI, a React/Vue/Svelte component, a page, a dashboard, or an app, or says it 'looks generic / boring / AI-slop / templated'. Pulls a NAMED design style only when the user names one; otherwise reads the brief and picks a fitting direction. Does NOT auto-clone any template and does NOT default to any one font."
disable-model-invocation: true
model: opus
---

# Frontend design skill (anti-slop, mechanical)

Most AI UI is boring for one reason: the model jumps to a default aesthetic and follows vague "be creative" advice it can ignore under load. This skill replaces that with a **brief-read, three dials, and a countable pre-flight gate**. The rules below are contextual: read the brief first, then pull only what fits.

Scope is **all UI** (components, pages, apps, dashboards, landing, marketing), not landing pages only. Layout, typography, contrast, motion, and anti-tell rules apply equally to a dashboard and a marketing page.

> Provenance: the mechanical layer (dials, layout hard rules, AI-tell bans, pre-flight) is adapted from `leonxlnx/taste-skill` (public repo), rewritten tight. The named-styles contract is the local addition.

<!-- protected:start reason="forcing contract: the exact failure this skill exists to prevent" -->
## STOP. This skill only works if you actually run it.

The way this skill fails is specific. The model **free-hands the default dark dashboard, then writes a Design Read that just describes that default** ("dark zinc, one emerald accent, mono") and ships it. Reskinning the default dashboard with a different accent hue is not a design. A Design Read that names a palette is not a design.

Three non-negotiables, each a pre-flight FAIL if missing:

1. **Run the process, do not retrofit it.** If you are reaching for zinc-950 + one bright accent + uppercase-mono labels + bordered cards + an admin table because that is what comes to mind, you have NOT used this skill. That gestalt is the current LLM-default dashboard. Stop and do the Design Read for real before writing code.
2. **Name a CONCEPT, not a palette.** The Design Read must state an idea that could only describe THIS product (a metaphor, a point of view, the domain's own visual language). Test: if your read would be equally true of a generic invoices dashboard, it is not a design read. Redo it.
3. **Ship a SIGNATURE element + visible DOMAIN identity.** Name, before building, the one memorable thing someone would screenshot, and make it specific to what the product *is* (a voice lab shows waveforms; a finance app shows money; a calendar shows time). Generic CRUD chrome that could front any dataset fails.
<!-- protected:end -->

---

## The loop (every build)

1. **Design Read**: one line naming a CONCEPT, before any code. Not a palette.
2. **Named style?** If the user named one, pull it exactly and skip dial-guessing for visual identity. Otherwise set dials from the brief, and do not park them all at the safe middle.
3. **Name the signature element**: the one domain-specific, memorable thing this build is remembered for. Decide it before writing components.
4. **Build** using the bias-correction directives and design-system honesty. Replace default components, do not ship them untouched.
5. **Pre-flight**: run the checklist before outputting. Any box fails, fix it, do not ship.

---

## 1. Design Read (mandatory gate)

Before touching code, state in one line:

> **Reading this as: `<page/app kind>` for `<audience>`; the CONCEPT is `<a metaphor / point of view / the domain's own visual language>`; signature element = `<the one memorable, domain-specific thing>`; dials `<V/M/D + why>`.**

The concept is the load-bearing field. "Dark zinc with an emerald accent, mono-forward" is NOT a concept, it is a palette describing the default dashboard. A concept is "a studio listening console", "liner-notes for a record review", "a trading terminal", "a field notebook". Name the idea that could only describe THIS product.

Read these signals: page/app kind, the vibe words the user used, reference URLs or products named, audience (B2B buyer vs design-conscious consumer vs internal operator), brand assets that already exist, and quiet constraints (accessibility, regulated, trust-first) that **override** aesthetic preference.

If the brief is genuinely ambiguous, ask **exactly one** question, never a multi-question dump. If you can infer confidently, declare the read and proceed.

**Anti-default discipline.** Do not reach for: AI-purple/violet gradients, a centered hero over a dark mesh, three equal feature cards, glassmorphism on everything, infinite micro-animations, Inter + slate-900. And the dashboard-specific default, the #1 tell for tools: **near-black (zinc-950) + one saturated accent (emerald/cyan/violet) + uppercase-tracked mono labels + rounded bordered cards + a bordered admin table.** Changing only the accent hue does not escape it. Move past the whole gestalt deliberately, based on the concept.

---

## 2. Named styles registry (pull ONLY when named)

There is **no default house style.** A named style is applied **only when the user names it.** For net-new UI with no named style, run the Design Read and dials and pick a direction that fits the brief. Never auto-clone a template, never default to one font.

The pattern: keep a registry of your own brands or product styles, each one a fixed spec the model reproduces *exactly* when named. The point of naming them is that "named" is the only switch that turns off the dial-guessing; an unnamed build never silently inherits one. A registry entry is a small, exact block:

```
### `<style-name>` (what it is)
- Theme: dark or light, the exact background and body token.
- Neutrals: the named scale, lightest to darkest.
- Accent: the exact accent token(s), and the rule (one accent, locked page-wide).
- Fonts: the exact families for display / body / mono. If it specifies a "default" font like Inter, that is deliberate inside a named system, not a violation of the avoid-Inter default.
- Surfaces, motion, and any signature element (an eyebrow style, a hairline, a stripe).
```

Recognized-but-never-auto-applied is a valid state too: a brand the model should pull only when named and never migrate another build toward. The discipline is the same: named means named, nothing inherits a style it was not given.

---

## 3. The three dials

After the read, set three dials (1 to 10). Every layout/motion/density call below is gated by them.

- **`DESIGN_VARIANCE`**: 1 perfect symmetry, 10 artsy chaos.
- **`MOTION_INTENSITY`**: 1 static, 10 cinematic/physics.
- **`VISUAL_DENSITY`**: 1 art-gallery airy, 10 cockpit/packed.

State the values and a one-line reason. Presets:

| Use case | VAR | MOT | DEN |
|---|---|---|---|
| SaaS landing (mainstream) | 7 | 6 | 4 |
| Agency / creative landing | 9 | 8 | 3 |
| Premium consumer | 7 | 6 | 3 |
| Developer portfolio | 6 | 5 | 4 |
| Editorial / blog | 6 | 4 | 3 |
| **App / dashboard / operator UI** | 4 | 3 | 6 |
| Trust-first / regulated / a11y-critical | 3 | 2 | 5 |
| Redesign, preserve | match | match+1 | match |
| Redesign, overhaul | +2 | +2 | match |

**Do not park all three dials at the safe middle (4 to 6) by default.** Middle dials with no stated reason are how "restraint" becomes blandness. Justify each value from the brief. For a personal or internal tool you own, bias `DESIGN_VARIANCE` HIGH (7 to 10): there is no committee to please, so timidity is the only failure. A dashboard at low variance still needs a concept and a signature element.

---

## 3.5 Signature element + kill the defaults (mandatory)

A build passes only if it has a **named signature element** and **visible domain identity**, and only if it does **not** ship default components untouched.

**Signature element.** Before writing components, name the one memorable, domain-specific thing. It comes from what the product *is*, not from generic chrome. A voice/TTS lab: stacked waveforms aligned to the same script, scrubbed together. A finance app: a cashflow ribbon. A calendar: a real time-grid. "A nice card grid" is not a signature element.

**Categorical color as structure, not decoration.** When the domain has named categories (method classes, genome tracks, taxa, pipeline stages, ledger accounts), one saturated hue per category IS a strong anti-default signature, and explicitly NOT the one-bright-accent default. But it works only when the color SYSTEM *dominates the surface as structure*: full color plates, thick spines, colored tabs, a verdict block flooding in the category's hue. Rendered as thin swatches beside a single dominant accent, it collapses straight back to the dark-default gestalt. Drive one hue per element through a single CSS var so verdict, spine, tab, and link stay consistent.

**Default-component ban (replace or customize, never ship as-is):** native `<audio controls>` / `<video controls>` (build a real player with a waveform); unstyled native `<select>` and default file inputs; shadcn/ui in default state (customize radii, color, type, density); the plain bordered admin table with uppercase-mono headers as the only way to show rows; "near-black + one bright accent" as the entire visual identity; a single rounded bordered card as the only container shape on the page.

---

## 4. Design-system honesty

If the brief reads as an enterprise/system surface, install and use the **official** package, do not hand-roll its CSS or import its tokens then override 90% of them. **One system per project.** (Full install table and canonical sources in `references/design-systems.md`.) Quick map: Microsoft/enterprise → Fluent UI; Google-flavored → Material 3; IBM analytics → Carbon; Shopify → Polaris; Atlassian → Atlaskit; GitHub-style → Primer; UK gov → GOV.UK Frontend; US gov → USWDS; modern accessible React → Radix Themes; own-the-code SaaS → shadcn/ui (never default state); Tailwind SaaS → Tailwind utilities.

If the brief is an **aesthetic** (glassmorphism, bento, brutalism, editorial, dark-tech, kinetic type), there is no official package: build with native CSS + Tailwind and label borrowed inspiration honestly in comments.

---

## 5. Bias-correction directives

**Typography.** Display default `text-4xl md:text-6xl tracking-tighter leading-none`; body `text-base leading-relaxed max-w-[65ch]`. **Avoid Inter as a default** (allowed inside a named system that specifies it). Serif for editorial/luxury/publication, not for dashboards, and vary the serif across projects. Italic display words with descenders (`y g j p q`) need `leading-[1.1]` min + `pb-1` reserve or they clip.

**Color.** **Max 1 accent**, saturation under 80% by default, over a neutral base. No default AI-purple/blue glow. One accent used identically across every section (no blue CTA in section 7 of a warm-grey site). For premium consumer (cookware/wellness/artisan/luxury), avoid the AI-default beige+brass+oxblood+espresso family.

**Layout hard rules (failing any is shipping broken work).** Hero fits the initial viewport: headline 2 lines max, subtext 20 words and 4 lines max, CTA visible without scroll. Hero top padding capped at `pt-24`. Hero stack max 4 text elements; no tagline-below-CTAs, trust strip, pricing teaser, feature bullets, or avatar row in the hero. **Eyebrow restraint** (the #1 violated rule): an eyebrow is a small uppercase wide-tracking label above a headline; max 1 per 3 sections; count the `uppercase tracking` micro-labels and fail if over `ceil(sectionCount / 3)`. No "big left headline + small right explainer" as a section header by default. Max 2 consecutive image+text-split sections. A layout family appears at most once (8 sections, 4+ different families). Bento needs exact cell count (N items, N cells) plus mixed sizes and background diversity. Logo wall lives under the hero with real SVG logos, never text wordmarks. Nav on one line at desktop, height 80px max. Use `grid` over flex-math. `min-h-[100dvh]`, never `h-screen`. Declare the mobile collapse per section.

**Images.** Priority: an image-gen tool if available (generate section-specific assets at the right aspect ratio), then real photography via a seeded placeholder service, then a clearly-labeled TODO slot. Even minimalist sites need 2 or 3 real images; a pure-text page is incomplete, not minimal. Banned: div-based fake screenshots (the #1 tell), hand-rolled decorative SVGs, hand-rolled icon paths (use one icon family at a standard stroke width).

**Content density.** Per section: headline 8 words max + sub-paragraph 25 words max + one visual OR one CTA. Lists over 5 items use a real component, not a default `<ul>` with `divide-y`. No `border-t`+`border-b` on every row of a long table. A two-dimensional catalog (scheme/brand × type/format) collapses one axis to a picker: one card per type plus a single scheme selector that recolors every poster, never a card per combination.

**Motion (must be motivated).** Every animation justifies itself in one sentence: hierarchy, storytelling, feedback, or state. If `MOTION_INTENSITY > 4`, the page actually animates; if you cannot ship working motion, drop the dial to 3 and ship clean static. One marquee per page max, reduced-motion wrapped. Never read `window.scrollY` into React state; use a scroll-driven primitive.

---

## 6. AI tells (banned unless the brief explicitly asks)

**Visual:** no neon/outer glows, no pure `#000000` (use zinc-950), no oversaturated accents, no custom cursors, no gradient-text on large headers. **The "Jane Doe" effect:** no generic names, no egg/default-user avatars, no fake-perfect numbers (`99.99%`; use `47.2%`), no startup-slop brand names (Acme/Nexus/SmartFlow), no filler verbs (Elevate/Seamless/Unleash/Next-Gen). **Layout:** no three-equal feature cards; no version labels in a hero unless it is a launch; no section-number eyebrows (`00 / INDEX`). **Decoration tells:** no decorative status dots by default, no locale/time/weather strips, no scroll cues, no hero-bottom text strips, no pills overlaid on images, no fake photo-credit captions, no rotated vertical text, no crosshair grid lines as decoration. The middle-dot (`·`) is rationed to 1 per metadata line.

<!-- protected:start reason="em-dash ban, non-negotiable" -->
### 6.G EM-DASH BAN (non-negotiable)
The em-dash and the en-dash-as-separator are **completely banned** everywhere visible: headlines, eyebrows, pills, body, quotes, attribution, captions, button text, alt text. No "sparingly" allowance. Restructure with a period, comma, colon, or parentheses. Ranges use a hyphen (`2018-2026`). A single one anywhere is a pre-flight fail, rewrite.
<!-- protected:end -->

---

## 7. Final pre-flight (run every box; any fail is not done)

**Distinctiveness gate (run first; if any fails, the build is generic, redo before the rest):**
- [ ] **Concept, not palette:** the Design Read names an idea that could only describe THIS product. Would it be false of a generic invoices dashboard? If it would still be true, FAIL.
- [ ] **Signature element** named and built, and domain-specific (not "a card grid")?
- [ ] **Domain identity visible:** a stranger can tell what the product is for at a glance?
- [ ] **No untouched default component** (native audio/video/select, shadcn default, plain admin table)?
- [ ] **Not the default-dashboard gestalt** (near-black + one bright accent + mono labels + bordered cards)?
- [ ] **The mirror test:** would this be indistinguishable from a generic LLM dashboard/landing? If yes, FAIL and redo.

**Mechanical gate:** Design Read declared? Named style applied exactly if named, and NOT auto-cloned if not? Dials explicit and reasoned? Design system chosen or aesthetic labeled honestly? ZERO em-dashes anywhere visible? One theme page-wide, one accent, one corner-radius system? Button contrast AA 4.5:1, no CTA label wraps, no duplicate CTA intent? Inputs/labels/focus-rings pass AA, label above input? Hero fits viewport, 4 text elements max, `pt-24` cap? Eyebrow count within ceiling, split-header avoided, zigzag 2 max? 4+ layout families across 8 sections, bento exact cell count? Logo wall under hero, real SVG logos? Real images, no div fake-screenshots, no pure-text minimalism? Icons from one library? Content density sane? Motion motivated and claimed-equals-shown and reduced-motion wrapped? Viewport stability, mobile collapse, empty/loading/error states? No AI tells from Section 6?

---

## When NOT to over-apply

Inside a named design system (Fluent/Carbon/etc.), the system's fonts and tokens win over the Section 5 defaults; that is intended. For a tiny one-component change, run the Design Read and the relevant pre-flight boxes, skip the full landing-page machinery. Low variance is fine when the brief earns it, but a low-variance build still needs a concept, a signature element, and domain identity.

## Worked anti-example (the failure that hardened this skill)

A TTS voice-grading lab once shipped as: zinc-950 + an emerald accent + all-mono type + a bordered admin table + native `<audio controls>` + rounded bordered cards. A voice lab with no waveform anywhere. Diagnosis: (1) the skill was never actually invoked, the UI was free-handed and a Design Read retrofitted to describe it; (2) the Design Read was a palette, not a concept; (3) dials parked at the safe middle; (4) no signature element, no domain identity; (5) default components shipped untouched. Every one of those is now a named pre-flight FAIL above. If a build you are about to ship matches this shape, it is wrong.

## Why this is a good example

It is the anti-slop discipline from [doc 12](../../docs/12-voice-and-antislop.md) applied to UI instead of prose. The lesson that generalizes past frontend: vague instructions ("be distinctive") get ignored under load, so the skill replaces them with a countable gate the model cannot pass while producing the default. A rule you can count beats a rule you can rationalize.
