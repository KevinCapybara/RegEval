"""Presentation helpers for the benchmark dashboard; no evaluation logic."""

from pathlib import Path

import streamlit as st


def apply_style():
    st.html(f"<style>{Path(__file__).with_name('ui.css').read_text(encoding='utf-8')}</style>")


def masthead():
    st.html('''
        <div class="re-masthead">
            <div class="re-brand"><span class="re-mark" aria-hidden="true">R<span>\u2197</span></span>RegEval</div>
            <div class="re-environment"><span aria-hidden="true"></span>LOCAL WORKSPACE</div>
        </div>
        <div class="re-intro">
            <div class="re-eyebrow">REGULATORY INTELLIGENCE / EVALUATION</div>
            <h1>Evidence first.<br><span>Evaluation, clarified.</span></h1>
            <p>Local benchmark for evidence-grounded FDA review</p>
        </div>
    ''')


def empty_benchmark():
    st.html('''
        <div class="re-empty">
            <div class="re-empty-icon" aria-hidden="true">\u2261</div>
            <div class="re-eyebrow">BENCHMARK STATUS</div>
            <h2>A clean slate for your next evaluation.</h2>
            <p>Benchmark reset. No test cases or golden datasets are installed.</p>
            <div class="re-empty-status"><span aria-hidden="true"></span>Awaiting test cases</div>
        </div>
        <div class="re-footer"><span>RegEval</span><span>Evidence-grounded FDA review</span></div>
    ''')


def section_heading(title, description):
    st.subheader(title)
    st.caption(description)


def evaluation_guide(tasks):
    st.markdown("""
- **System:** RegEval tests AI agents on five FDA Complete Response Letter tasks, from finding deficiencies to counting them correctly. A separate call to your selected judge model grades each answer.
- **Workspace and references:** Open **Benchmark setup** for each task's source inputs, instructions, rubric, reference answer, and supporting records. Agents see only instructions and inputs; the judge also sees the reference answer.
- **How to use:** Choose a task and test agent below, then confirm the document-use checkbox. All installed datasets run automatically; task averages require five scored datasets. Review scores in **Compare** and answers and judge findings in **Eval Results**.
- **One-command grader:** Click **Run evaluation** to generate answers, run the task-specific graders, and save results in one action\u2014no terminal command needed.
- **Scoring:** Each dataset has four pass/fail checks worth 25% each. The rubric requires 0% for empty or wholly wrong answers and 100% for complete, verified reference-equivalent answers; partially correct answers can pass individual checks. Review-pending results and execution errors remain unscored.
- **Verification status:** Reference answers and verification records are available in **Benchmark setup**. Task 1 gold and endpoint calibration remain provisional; Task 4 has an unresolved judgment; Task 5 includes a genuine-duplicate case and source-grounded false-merge controls as they become available. This interface does not establish complete verification or Harbor-format compliance.
""")
    rubrics = {
        1: (
            "Identify deficiencies, assign all supported categories (CMC, clinical, nonclinical, labeling, and facility inspection), and report their distribution. "
            "In other words, we check whether the AI can find the problems in a letter, say what kind of problems they are, and count each kind correctly.",
            (
                "**Deficiency detection:** Correctly identify every deficiency and non-deficiency.",
                "**Category assignment:** Assign every supported category, with no missing or extra labels.",
                "**Evidence and explanations:** Support every decision with accurate, source-grounded reasoning.",
                "**Distribution accuracy:** Report correct category counts, denominators, and percentages.",
            ),
            "Labeling a routine administrative request as a deficiency fails detection. Omitting a supported clinical label fails category assignment, even if another label is correct.",
        ),
        2: (
            "Find approval-blocking deficiency paragraphs while excluding routine requests and other non-deficiencies. "
            "In other words, we check whether the AI can pick out the parts that describe real problems needing a fix, without confusing them with ordinary requests.",
            (
                "**Recall:** Find every true deficiency paragraph without omissions.",
                "**Precision:** Select no non-deficiencies, unknown IDs, or duplicate IDs.",
                "**Evidence:** Support each selection with evidence explaining why it blocks approval.",
                "**Coverage and counts:** Review every paragraph exactly once and report correct deficiency totals and percentages.",
            ),
            "Skipping a true deficiency fails recall. Selecting a routine submission instruction fails precision. Selecting none of the true deficiencies earns zero overall.",
        ),
        3: (
            "Calculate category prevalence at three levels: paragraphs, distinct letters, and application families. "
            "In other words, we check whether the AI can count how often each kind of problem appears in text sections, whole letters, and groups of letters about the same case.",
            (
                "**Paragraph counts:** Correctly count deficiency paragraphs in each category.",
                "**Letter counts:** Correctly count distinct letters affected by each category.",
                "**Family counts:** Correctly count application families affected by each category.",
                "**Percentages and counting rules:** Report correct fractions and percentages; explain denominators, deduplication, and overlapping categories.",
            ),
            "Counting two review-cycle letters from the same application as two families fails family counts. Using letters as the denominator for paragraph prevalence fails percentages.",
        ),
        4: (
            "Assign every supported category to paragraphs that are already known deficiencies, including paragraphs spanning multiple categories. "
            "In other words, we check whether the AI can spot every kind of problem in the same piece of text, without missing one or making one up.",
            (
                "**No missing labels:** Include every supported category for every deficiency paragraph.",
                "**No extra labels:** Assign only categories supported by the paragraph.",
                "**Evidence:** Support each assigned label with an exact source quote and an accurate explanation.",
                "**Distribution accuracy:** Report category counts, denominators, and percentages matching the verified labels.",
            ),
            "Giving only CMC to a paragraph that also supports a facility-inspection deficiency fails the omission check. Adding an unsupported clinical label fails the addition check.",
        ),
        5: (
            "Recognize duplicate records without merging genuinely different letters, then count the deduplicated corpus. "
            "In other words, we check whether the AI can spot extra copies of the same letter and count it just once, while still counting different letters separately.",
            (
                "**Duplicate grouping:** Group all copies of the same letter and map every record exactly once.",
                "**Distinct-letter separation:** Keep different letters, including separate review cycles, apart with complete record coverage.",
                "**Identity evidence:** Support every pair's same-or-different decision with source evidence.",
                "**Deduplicated counts:** Report correct totals and category percentages, combining supported categories across duplicate copies.",
            ),
            "Treating two copies of one letter as separate fails duplicate grouping. Merging different review-cycle letters from the same application fails distinct separation.",
        ),
    }
    for task in tasks:
        description, checks, failure = rubrics[task['number']]
        with st.expander(f"Task {task['number']} \u00b7 {task['title']} \u2014 rubric"):
            st.write(description)
            st.markdown("**Four checks (25% each):**\n\n" + "\n".join(f"- {check}" for check in checks))
            st.markdown(f"**Failure example:** {failure}")
