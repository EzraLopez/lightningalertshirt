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

## Still TODO before launch
- [x] About Us filled in (2026-10-14): Ezra (@ezraxlopez),
      Bradley (@bfisch1), Noah (@noah_reis_), Shub (@exploreshub),
      Pavan (@pavan.brahmbhatt), Niraj (@nazz9).
- [ ] Confirm final copy tweaks (story paragraph is a close
      paraphrase of the original).
