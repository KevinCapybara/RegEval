"""At-a-glance comparisons using the same scoring rules as the detail tables."""
from .history import aggregate, score

AGENTS = {"gpt-6-luna": "Luna", "gpt-5-nano": "Nano"}


def summary_data(tasks):
    shared = [task for task in tasks if all(aggregate(task, m)[0] is not None for m in AGENTS)]
    means = {m: sum(aggregate(t, m)[0] for t in shared) / len(shared) if shared else None for m in AGENTS}
    bars, cells = [], []
    for task in tasks:
        for model, label in AGENTS.items():
            mean, count = aggregate(task, model)
            bars.append(dict(Task=f"Task {task['number']}", Agent=label, Score=mean,
                             Coverage=f"{count}/5", Description=task['title']))
            for dataset in range(1, 6):
                row = task['results'].get((dataset, model), {})
                value = score(row)
                cells.append(dict(Task=f"Task {task['number']}", Agent=label,
                                  Row=f"T{task['number']} · {label}", Dataset=f"D{dataset}",
                                  Score=value, Label="—" if value is None else f"{value:.0%}",
                                  Status=row.get('status', 'Not evaluated').replace('_', ' ')))
    return shared, means, bars, cells


def render_summary(tasks):
    import altair as alt
    import pandas as pd
    import streamlit as st

    shared, means, bars, cells = summary_data(tasks)
    st.markdown("### Agent performance at a glance")
    st.caption("LUNA / NANO · Shared-task averages · Higher is better")
    columns = st.columns([1, 1, 0.85])
    for column, (model, label), tone in zip(columns, AGENTS.items(), ['luna', 'nano']):
        value = means[model]
        display = "—" if value is None else f"{value:.1%}"
        with column:
            st.html(f'<div class="re-score-card {tone}"><div class="re-eyebrow">{label.upper()}</div>'
                    f'<div class="re-score-value">{display}</div><div class="re-score-label">Overall score</div>'
                    f'<div class="re-score-foot">{len(shared)} shared tasks · {len(shared) * 5} datasets per agent</div></div>')
    with columns[2]:
        gap = means['gpt-6-luna'] - means['gpt-5-nano'] if shared else None
        leader = "Awaiting comparable tasks" if gap is None else "Agents are tied" if abs(gap) < 1e-10 else f"{'Luna' if gap > 0 else 'Nano'} leads"
        display = "—" if gap is None else f"{abs(gap) * 100:.1f}<small> pp</small>"
        st.html(f'<div class="re-score-card gap"><div class="re-eyebrow">PERFORMANCE GAP</div>'
                f'<div class="re-score-value">{display}</div><div class="re-score-label">{leader}</div>'
                '<div class="re-score-foot">Same tasks · Same weighting</div></div>')
    basis = ', '.join(f"T{t['number']}" for t in shared) or 'none yet'
    st.caption(f"Comparison basis: {basis}. Each task needs five scored datasets and no failed calibration for both agents. "
               "Missing, review-pending, and incomplete task results are excluded. Task 1 is provisional when included; individual Task 5 datasets are visible below.")

    colors = alt.Scale(domain=['Luna', 'Nano'], range=['#a89bff', '#53d9cd'])

    def style(chart):
        return (chart.configure_view(strokeOpacity=0).configure_axis(
            labelColor='#c7cbd3', titleColor='#c7cbd3', gridColor='#303238',
            domainOpacity=0, tickSize=0, labelPadding=10, titlePadding=12)
            .configure_legend(labelColor='#e5e5e4', title=None, orient='top'))

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("#### Task-by-task comparison")
        st.caption("Five-dataset task averages · Hover for score and coverage")
        base = alt.Chart(pd.DataFrame(bars)).encode(
            x=alt.X('Task:N', sort=[f"Task {t['number']}" for t in tasks], title=None),
            xOffset=alt.XOffset('Agent:N', sort=['Luna', 'Nano']),
            y=alt.Y('Score:Q', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='.0%'), title=None),
            color=alt.Color('Agent:N', scale=colors),
            tooltip=['Agent:N', 'Description:N', alt.Tooltip('Score:Q', format='.1%'), 'Coverage:N'])
        chart = base.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=24)
        labels = base.mark_text(dy=-12, color='#faf9fa', fontSize=12).encode(
            text=alt.Text('Score:Q', format='.0%'), color=alt.value('#faf9fa'))
        st.altair_chart(style((chart + labels).properties(height=310)), width="stretch")
        st.caption("Absent bars indicate unavailable task averages, not 0% scores.")
    with right:
        st.markdown("#### Dataset score map")
        st.caption("Every dataset · Includes partial tasks")
        base = alt.Chart(pd.DataFrame(cells)).encode(
            x=alt.X('Dataset:N', title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Row:N', title=None, sort=[f"T{t['number']} · {a}" for t in tasks for a in AGENTS.values()]),
            tooltip=['Task:N', 'Agent:N', 'Dataset:N', 'Label:N', 'Status:N'])
        tiles = base.mark_rect(cornerRadius=5, stroke='#0f1012', strokeWidth=4).encode(
            color=alt.condition('isValid(datum.Score)', alt.Color('Score:Q',
                scale=alt.Scale(domain=[0, 1], range=['#30354b', '#b6aaff']), legend=None), alt.value('#202328')))
        labels = base.mark_text(fontSize=12).encode(text='Label:N', color=alt.condition(
            'isValid(datum.Score) && datum.Score >= 0.5', alt.value('#101117'), alt.value('#e5e5e4')))
        st.altair_chart(style((tiles + labels).properties(height=310)), width="stretch")
        st.caption("Light = higher score · Dark = lower score · — = unscored or missing")
    st.divider()
