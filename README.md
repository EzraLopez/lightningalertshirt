# lightningalertshirt.com — waitlist site

Clone of the lightning-alert-tees interest page, for the domain
**lightningalertshirt.com** (Porkbun, account katlaio, expires 2027-10-14).

## Layout
- `site/index.html` — the whole site (single static page, no build step).
  The crew photo is currently hotlinked from the original site; drop a
  local `crew-hotel-selfie.jpg` next to `index.html` and change the
  `<img src>` before launch if hotlinking is a concern.
- `tools/parse_waitlist.py` — turns a form-export CSV into print-run
  numbers (shirts per size) + a deduplicated email list.

## Hosting + data capture (recommended: Netlify)
The form is wired for **Netlify Forms** (`data-netlify="true"`,
honeypot field `website` — same trap name as the original):

1. Create a free Netlify site from this repo's `site/` folder
   (or drag-and-drop deploy). Netlify auto-detects the form.
2. Point the domain at it: Netlify > Domain management > add
   `lightningalertshirt.com`, then set the DNS records it shows you
   at Porkbun (apex A / www CNAME). HTTPS is automatic.
3. Every submission is stored as a structured row:
   `created_at, name, email, size, quantity`.
   View/filter in Netlify > Forms > `waitlist`; enable email
   notifications there if wanted.

GitHub Pages alone will NOT work for data capture (static only) —
it can host the page, but the form needs Netlify (or an equivalent
form backend) behind it.

## Our own signup database
`data/signups.csv` is the canonical list of waitlist signups, kept by us
(not by Netlify/FormSubmit). It is **local only and gitignored** — it
contains real email addresses and this repo is public.
- **Update it:** `python3 tools/sync_signups.py` — scans the
  foku.assistant@gmail.com inbox for signup notification emails (both the
  Netlify Forms era and the current FormSubmit era, same subject line),
  parses name/email/size/quantity, skips test submissions, dedupes by
  message ID, and prints the size tally. Safe to re-run any time.
- Columns: received_at_utc, name, email, size, quantity, source, message_id.

## Using the data
- **How many of each size?** Export CSV from Netlify, then:
  `python3 tools/parse_waitlist.py export.csv --out-dir out`
  → prints shirts-per-size and writes `out/summary.csv`.
- **Send everyone the Shopify link later:** the same run writes
  `out/emails.txt` (unique emails, one per line) — import/paste that
  into Shopify Email (Customers > email subscription list) or any
  mail tool when the product page is live. The signup fine print
  already tells visitors their email will be used for updates about
  this shirt, including a purchase link.

## Launch status — LIVE 2026-10-14
- Netlify project "lightningalertshirt" (team ezralopez, free plan),
  imported from this repo, publish directory `site`.
  Fallback URL: https://lightningalertshirt.netlify.app
- Porkbun DNS: A @ → 75.2.60.5, CNAME www → lightningalertshirt.netlify.app
  (TTL 600). HTTPS on (Let's Encrypt, auto-renews ~Jan 12, 2027).
- Forms: form detection enabled; "waitlist" form is collecting.
  Verified end-to-end with one test submission
  (Foku Test / foku.assistant@gmail.com / M / 1) — ignore that row
  in real counts, or delete it in the Netlify dashboard.

## Still TODO before launch
- [x] About Us filled in (2026-10-14): Ezra (@ezraxlopez),
      Bradley (@bfisch1), Noah (@noah_reis_), Shub (@exploreshub),
      Pavan (@pavan.brahmbhatt), Niraj (@nazz9).
- [ ] Confirm final copy tweaks (story paragraph is a close
      paraphrase of the original).
