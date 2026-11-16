"""Streamlit presentation for saved evaluation results."""
from .results_summary import render_summary
from .llm import RESULT_MODELS as MODELS
from .history import aggregate, load_history, percent, score


def render_history(root, tasks=None):
    import pandas as pd
    import streamlit as st

    tasks = tasks if tasks is not None else load_history(root)
    tasks = [dict(task, results={key: row for key, row in task['results'].items() if key[1] in MODELS})
             for task in tasks]
    render_summary(tasks)
    st.subheader("Dataset evaluation details")
    for task in tasks:
        averages = " \u00b7 ".join(f"{label}: {percent(aggregate(task, model)[0])}" for model, label in MODELS.items())
        with st.expander(f"Task {task['number']} \u00b7 {task['title']} \u2014 {averages}"):
            if task["error"]:
                st.warning(task["error"])
            if not task["source"]:
                st.warning("Saved results are not installed in this workspace.")
            table = []
            for dataset in range(1, 6):
                for model, label in MODELS.items():
                    result = task["results"].get((dataset, model), {})
                    value = score(result)
                    row = {"Dataset": f"Dataset {dataset}",
                           "Model": label, "Score": percent(value),
                           "Status": result.get("status", "Not evaluated").replace("_", " ")}
                    criteria = result.get("criteria") or {}
                    for key, label in task["dimensions"].items():
                        verdict = criteria.get(key) if value is not None else None
                        row[label] = "Pass (1)" if verdict == 1 else "Fail (0)" if verdict == 0 else "\u2014"
                    table.append(row)
            st.dataframe(pd.DataFrame(table), hide_index=True, width="stretch")
            st.caption("Pass/fail applies to the entire dataset for each dimension. Expand a dataset for the saved evaluation details.")
            for dataset in range(1, 6):
                with st.expander(f"Dataset {dataset}" + (" \u00b7 pilot" if task["number"] == 5 and dataset == 1 else "")):
                    for column, (model, label) in zip(st.columns(len(MODELS)), MODELS.items()):
                        with column:
                            st.markdown(f"**{label}**")
                            result = task["results"].get((dataset, model))
                            if not result:
                                st.info("Not evaluated \u2014 no saved result.")
                                continue
                            st.metric("Dataset score", percent(score(result)))
                            st.caption(result.get("status", "Unknown").replace("_", " "))
                            reasons = result.get("criterion_reasons", result.get("reasons", {}))
                            for key, title in task["dimensions"].items():
                                if reasons.get(key):
                                    st.markdown(f"**{title}**")
                                    st.write(reasons[key])
                            if result.get("review_concern"):
                                st.warning(result["review_concern"].get("reason", "Needs review"))
                            st.json(result, expanded=False)
            if task["source"]:
                st.caption(f"Result source: {task['source']}")
