# Design Partners & LOIs (traction)

Running list of people who've committed interest. Show this to judges as traction.
Keep it honest: "LOI / verbal commit," not "revenue."

## 1. Data-tools migration prospect  (NEW — verbal LOI)
- **Status:** Gave an LOI by message ("consider this reply as my LOI"). Identify sender + capture name/company/email.
- **Use case (their words):** full migration between data-tools / cloud providers, with **data sameness as the ground truth**. Wants to see how we handle e.g. different column-naming rules between cloud providers.
- **Why it's a strong fit (and maybe a beachhead):** data migration correctness is **deterministically checkable** — compare migrated data vs source (row counts, value-level equality, schema/column mapping). No AI judging AI. A cheaper model does the migration; Bongo verifies every mapping against the source and catches the wrong ones (e.g. a column renamed/mapped incorrectly because providers name things differently).
- **One-line pitch for this customer:** "Run the migration on a cheaper model. Bongo checks every column mapping against the source data and catches the wrong ones, so you trust the migration without hand-checking it."
- **Next steps:** get name/company, book a 15-min call, scope the exact providers, consider building the demo on THIS use case (checkable = bulletproof).

## 2. Arjun (ponnagantiarjun644@gmail.com)  (earlier LOI)
- **Status:** Offered to sign an LOI as an early design partner. LOI PDF drafted (`Agent-Reality-Check-LOI`), pending send/sign.
- **Use case:** general early design partner for agent reliability.
- **Next steps:** send the LOI (or the updated Bongo version), book a call.

---
_Update this as more LOIs / design partners come in. Pair each with a concrete, checkable use case where possible._
