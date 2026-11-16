From the supplied JSON records and source metadata, identify which records represent the same underlying FDA letter. Produce a unique-letter mapping and calculate category counts by letter and application family without double-counting duplicate representations.

Use the supplied verified category annotations as fixed inputs. Do not infer categories from headings, routine safety updates, deferred labeling comments, or redactions. The category ledger covers only the explicitly identified, visible findings; unobservable redacted findings are outside this benchmark. A letter may have no categories in this five-category taxonomy. It still counts in the denominator.

Different review-cycle letters remain distinct even when wording, application number, PDF package, or a package-level Reference ID matches. A reference to a separate letter does not create another supplied record. Application family means the base NDA/BLA number; Original subnumbers belong to the same family but can identify separate actions.

Return JSON with:

- `record_to_letter`: one mapping entry for every supplied record, with arbitrary stable letter IDs. Equal IDs mean the same letter.
- `decisions`: one entry for every unordered pair of supplied record IDs: `records`, `same_letter` (boolean), `evidence` (list of record/PDF metadata locators), and `reason`. Explain both merges and separations using source or metadata; similarity alone is insufficient. Equivalent evidence and wording are accepted.
- `counts`: `unique_letters`, `application_families`, `by_letter` and `by_application_family` (each a category-to-integer-count object containing all five categories), and `letter_percentages` and `family_percentages` (category-to-percentage objects).

Count each category once per unique letter. For a family count, take the union across that family's letters and count the family once per category. Category overlaps are allowed. Divide by all unique letters or all families, including those with no in-scope annotation. Report percentages to at least one decimal place.

The benchmark provides annotations, not the identity partition. Use only the candidate workspace; hidden gold and judge logs are not candidate inputs.
