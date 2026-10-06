# Design Systems Reference

Loaded on demand by `designing-frontend-uis` Section 4. When a brief reads as an enterprise/system surface, install the **official** package and use it honestly. One system per project. Do not hand-roll a system's CSS or import its tokens then override 90% of them.

## Install commands

```bash
# Material Web (Material 3)
npm install @material/web
# Fluent UI React (v9) — Microsoft / enterprise
npm install @fluentui/react-components
# Fluent UI Web Components (framework-free)
npm install @fluentui/web-components @fluentui/tokens
# IBM Carbon — data-dense analytics
npm install @carbon/react @carbon/styles
# Radix Themes — modern accessible React foundation
npm install @radix-ui/themes
# shadcn/ui — own-the-code SaaS (NEVER ship default state)
npx shadcn@latest init
npx shadcn@latest add button card badge separator input
# Primer CSS — GitHub product/devtool UI
npm install --save @primer/css
# Primer Brand — GitHub marketing UI
npm install @primer/react-brand
# GOV.UK Frontend — UK public sector
npm install govuk-frontend
# USWDS — US public sector / trust-first
npm install uswds
# Atlassian (Atlaskit)
yarn add @atlaskit/css-reset @atlaskit/tokens @atlaskit/button @atlaskit/badge @atlaskit/section-message @atlaskit/card
# Bootstrap 5.3 — fast local-business / agency MVP
npm install bootstrap
# Shopify Polaris Web Components (Shopify app surfaces only) — add to app HTML head:
#   <meta name="shopify-api-key" content="%SHOPIFY_API_KEY%" />
#   <script src="https://cdn.shopify.com/shopifycloud/polaris.js"></script>
```

## Canonical sources (read before reinventing)

- **Material Web** — https://material-web.dev/theming/material-theming/ · https://m3.material.io/develop/web
- **Fluent UI** — https://fluent2.microsoft.design/components/web/react/ · https://github.com/microsoft/fluentui · https://learn.microsoft.com/en-us/fluent-ui/web-components/
- **Carbon** — https://carbondesignsystem.com/ · https://carbondesignsystem.com/developing/react-tutorial/overview/
- **Shopify Polaris** — https://shopify.dev/docs/api/app-home/web-components · https://polaris-react.shopify.com/components
- **Atlassian** — https://atlassian.design/get-started/develop · https://atlassian.design/tokens/design-tokens
- **Primer** — https://primer.style/ · https://github.com/primer/css · https://github.com/primer/brand
- **GOV.UK** — https://design-system.service.gov.uk/components/button/ · https://github.com/alphagov/govuk-frontend
- **USWDS** — https://designsystem.digital.gov/components/button/ · https://github.com/uswds/uswds
- **Bootstrap** — https://getbootstrap.com/docs/5.3/layout/grid/
- **Tailwind** — https://tailwindcss.com/docs/dark-mode · https://tailwindcss.com/blog/tailwindcss-v4
- **Radix** — https://www.radix-ui.com/themes/docs/components/theme
- **shadcn/ui** — https://ui.shadcn.com/docs
- **Native CSS / W3C** — backdrop-filter, prefers-color-scheme, prefers-reduced-motion, CSS Grid, scroll-driven animations (MDN) · https://drafts.csswg.org/scroll-animations-1/
- **Apple Liquid Glass** (Apple platforms ONLY — no official web `liquid-glass.css`; web is an approximation) — https://developer.apple.com/design/human-interface-guidelines/materials

## Aesthetic-only directions (no official package — build native + Tailwind, label honestly)

Glassmorphism (`backdrop-filter` + 1px inner border + inner shadow, solid-fill fallback for `prefers-reduced-transparency`) · Bento (CSS Grid, mixed cell sizes) · Brutalism (native CSS, mono, raw borders) · Editorial (serif, asymmetric grid, whitespace) · Dark-tech (mono + one neon accent) · Aurora/mesh (layered radial gradients) · Kinetic type (CSS + scroll-driven animations, GSAP for hijacks).
