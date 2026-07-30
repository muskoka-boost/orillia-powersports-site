# FM Recycling — Brand Spec

Derived from fmrecycling.ca (crawled 2026-07-30), their logo, and their own
photography. Positioning and copy are carried over from the existing site; the
hero leads harder on posted prices and same-day cash, which is what people are
actually searching for.

## Voice

Blunt, working, unpretentious. Their own line — *"Turn unwanted items into
cash!"* — is the whole pitch and stays as the hero. Other phrases worth keeping
verbatim because they're theirs: **"Fast, Fair and Friendly"**, **"honest
weights, competitive prices, and same-day payment"**, **"Open to the Public"**.

Never: "solutions", "sustainability journey", "eco-conscious partners". This is a
scrap yard. Say what you pay and when you're open.

## Palette

Sampled directly from the logo (`fm-logo.png`) — 47% black, 13% yellow.

| Token | Hex | Use |
|---|---|---|
| `--black` | `#0d0d0d` | Nav, footer, headings |
| `--yellow` | `#f0b01d` | **Brand.** Sampled mean of the logo's arrows. CTAs, prices, accents |
| `--yellow-dark` | `#c88f0a` | Yellow text on white — the raw brand yellow only hits 1.9:1 and is unreadable as text |
| `--steel-900` | `#1a1d21` | Dark section backgrounds |
| `--steel-100` | `#eceef1` | Tinted bands |
| `--ink` | `#15181c` | Body copy |
| `--rust` | `#b4531f` | Rare accent for "call for price" |

**The critical constraint:** `#f0b01d` on white is 1.9:1 — it fails badly as
text. Yellow is used as a *background* with black on top (13.2:1, which is where
it's strongest), never as small text on light. Where a yellow-toned word is
needed on white, `--yellow-dark` is used instead.

## Type

- **Barlow Condensed 700** — display headings, prices, table headers. Condensed
  and heavy, matching the logo's compressed grotesque wordmark. It also lets long
  material names ("CARS - NO CATS/NO MOTOR") sit on one line in a table.
- **Barlow 400/600/700** — body, labels, UI.
- Self-hosted, latin subset, ~86 KB total.

## Treatment

- **Industrial, high-contrast, no rounded softness.** 4px radii at most. Sharp
  edges, heavy rules, uppercase condensed labels.
- Yellow is used sparingly and always with intent: the price figures, the primary
  CTA, the "open now" indicator, and the section rules.
- Photography is theirs and it's honest — a real yard on a grey day, real scrap,
  a real branded bin. It's not pretty stock and shouldn't be treated as if it
  were: full-bleed, slightly desaturated, black scrims.
- Prices are the product. The pricing table is the most designed element on the
  site — sticky category nav, monospaced-feeling numerals, obvious "last updated"
  date.

## Imagery

All eight photographs are FM Recycling's own, pulled from their Wix site at full
resolution. **Three had unapplied EXIF rotation** (orientation 3 and 6) and were
being served sideways or upside-down; those are corrected here.

| File | Subject | Used on |
|---|---|---|
| `yard-hero.jpg` | The yard — two material handlers, scrap pile, trucks | Home hero |
| `bins.jpg` | FMR-branded green roll-off bin + orange roll-off truck | Services, bins |
| `flatbed.jpg` | Flatbed trailer | Services, trucking |
| `copper-brass.jpg` | Brass and copper fittings | Prices, copper table |
| `aluminium.jpg` | Aluminium tube and extrusion scrap | Prices, aluminium table |
| `stainless.jpg` | Stainless pipe | Prices, stainless table |
| `metal-shop.jpg` | The metal shop bench | About |
| `grapple.jpg` | Grapple close-up, desaturated | Section divider |

## Pricing — handle with care

The four price tables are transcribed from their site. Their own site renders
each table as **two independent Wix text blocks** (labels in one, prices in
another) positioned side by side — there is no row structure tying a name to a
number. Alignment had to be reconstructed from document order.

Copper/Brass (9) and Stainless (8) paired unambiguously. Ferrous (11) and
Aluminium (9) each contain paragraphs where two values share one `<p>`, so those
two were reconstructed from document order and **should be spot-checked by FM
before this goes live**.

Prices carry their own disclaimer (*"subject to change — call for updated
pricing"*) and the `UPDATED 2026/07/25` date, both preserved.

## Explicitly not included

- **No testimonials or ratings.** None are published anywhere I could reach.
  Nothing was invented.
- **No tonnage, years-in-business, or customer-count statistics.** The only
  verifiable date claim is "Since 2000" for bin services, which is their own.
