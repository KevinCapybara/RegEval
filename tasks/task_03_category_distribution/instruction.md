Using the supplied verified paragraph labels, calculate for each of the five categories: deficiency-paragraph count, number of affected letters, and number of affected application families. Report each percentage with its numerator and denominator.

This is aggregation, not classification. Labels are authoritative; do not infer or change them. The datasets are synthetic, source-free fixtures, not FDA corpus prevalence estimates.

Counting policy:
- The five categories are CMC, clinical, nonclinical, labeling, and facility inspection.
- A paragraph is identified by paragraph_id. Repeated export rows with the same ID are one paragraph; identical labels on DIFFERENT IDs are distinct paragraphs. Paragraph IDs are globally unique within a dataset. A paragraph belongs to exactly one letter.
- A letter is identified by letter_id and belongs to exactly one family_id. Each review cycle is a separate letter, even within the same family. A family is counted once per category across all its letters and cycles.
- A paragraph is a deficiency exactly when deficiency=true. Non-deficiencies have no labels. Only deficiency paragraphs contribute to category numerators.
- Paragraph denominator: ALL unique deficiency paragraphs across the dataset, including all categories, counted once each. Do not use total label assignments or non-deficiency paragraphs.
- Letter denominator: ALL letters in the supplied letter registry, including letters with no deficiency paragraphs. Family denominator: ALL families in the supplied family registry, including unaffected families. Registry entries with no paragraph rows still count in the appropriate denominator.
- For each category, count unique deficiency paragraphs bearing that label; unique letters containing at least one such paragraph; and unique families containing at least one such letter.
- Report each of the 15 percentages with its exact integer numerator and denominator. Use at least one decimal place (rounding tolerance 0.05 percentage points). Explain the three denominator populations, deduplication, review-cycle handling, and why categories overlap and percentages need not sum to 100% at EACH level.

Return JSON with a categories object keyed by the five exact category names. Each category has paragraphs, letters, and families objects with integer numerator, integer denominator, and numeric percent. Include an explanation string. No evidence citations are required; do not invent source claims.
