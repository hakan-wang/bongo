# Design Partners & LOIs (traction)

Running list of people who've committed interest. Show this to judges as traction.
Keep it honest: "LOI / verbal commit," not "revenue."

## 1. Julio Anthony Leonard  (data migration — verbal LOI)
- **Status:** Verbal LOI. Interested specifically IF agents don't fail silently or fake success during data migration.
- **Concrete use case (his words):** migration from **on-prem to BigQuery**.
  - BigQuery column names are **case-INsensitive** at creation: you can't have both `Column_A` and `column_a` — it errors.
  - On-prem column names are **case-sensitive**: both can exist at once.
  - So on migration, something must decide per-column: if `Column_A` and `column_a` are **semantically the same** -> combine them; otherwise rename / alias / other.
  - Today this needs **manual intervention and data-level checks** every time.
- **Why this is the ideal use case (and a real beachhead):** correctness is **deterministically checkable** — compare migrated data vs source (row counts, value-level equality, schema/column mapping). No AI judging AI. A cheap model does the migration; Bongo verifies each column mapping against the actual data and catches the wrong calls (e.g. merging two columns that are NOT the same, which silently loses data). This is exactly the "fails silently / fakes success" risk he flagged.
- **One-line pitch for him:** "Run the migration on a cheaper model. Bongo checks every column mapping against the real data and catches the silent mistakes — like wrongly merging `Column_A` and `column_a` — so you trust the migration without hand-checking it."
- **Next steps:** capture company/email, book a 15-min call, scope on-prem->BQ, consider building a migration-verify demo on THIS case (checkable = bulletproof).

## 2. Arjun (ponnagantiarjun644@gmail.com)  (earlier LOI)
- **Status:** Offered to sign an LOI as an early design partner. LOI PDF drafted (`Agent-Reality-Check-LOI`), pending send/sign.
- **Use case:** general early design partner for agent reliability.
- **Next steps:** send the LOI (or the updated Bongo version), book a call.

---
_Update this as more LOIs / design partners come in. Pair each with a concrete, checkable use case where possible._
