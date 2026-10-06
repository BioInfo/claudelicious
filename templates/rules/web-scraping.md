# Web Scraping Strategy (example rule file)

<!-- An example rules/*.md showing a tiered fallback ladder. Scrub the
     self-hosted gateway/host details to your own. See docs/01. -->

Follow the ladder in order; stop at the first tier that works. Don't reach for a
heavy renderer when a plain fetch would do, and don't give up after one failure.

## The ladder

1. **Web search** for finding URLs (a scraper can't search).
2. **Plain fetch** for content extraction — fast, no infrastructure dependency.
3. **Paywall/anti-bot bypass** when the fetch hits a login wall or empty body.
4. **Headless-browser scrape** (JS rendering) when the bypass also fails, or for
   JS-heavy single-page apps.

## Routing shortcuts

- Known paywalled outlets (major newspapers, paid newsletters): go straight to
  the bypass tier; the plain fetch will return a "subscribe" stub.
- JS-heavy SPAs and social sites: go straight to the headless scraper; both the
  plain fetch and the bypass return empty or a login wall.

## After a failure

- Do NOT retry the same tier. Escalate to the next one.
- Do NOT tell the user "I can't access that page" before trying the bypass and
  headless tiers.

## If the whole ladder fails

Check that any self-hosted scraping infrastructure is actually reachable before
concluding the page is unreachable. Then tell the user and suggest an
alternative (a browser tool, a manual copy), rather than silently failing.
