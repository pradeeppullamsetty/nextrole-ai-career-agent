import json
import time
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from app_testable import build_task_summary, task_completion_rate

st.set_page_config(page_title="NeuralDesk · Focus OS", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

DEFAULT_TASKS = [
    {"id": 1, "title": "Finish UI polish", "project": "NeuralDesk", "priority": "High", "done": False, "due": "Today"},
    {"id": 2, "title": "Review Python fundamentals", "project": "Learning", "priority": "Medium", "done": False, "due": "Today"},
    {"id": 3, "title": "Update project README", "project": "Portfolio", "priority": "Low", "done": True, "due": "Today"},
]
if "tasks" not in st.session_state:
    st.session_state.tasks = DEFAULT_TASKS.copy()
if "focus_seconds" not in st.session_state:
    st.session_state.focus_seconds = 25 * 60
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_last" not in st.session_state:
    st.session_state.timer_last = time.time()
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 4
if "focus_intention_saved" not in st.session_state:
    st.session_state.focus_intention_saved = ""
if "focus_deadline" not in st.session_state:
    st.session_state.focus_deadline = None

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--text:#f4f5fc;--muted:#9da5bd;--line:rgba(255,255,255,.105)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{color:var(--text);background:#080a12;background-image:radial-gradient(ellipse at 10% 0%,rgba(111,88,255,.21),transparent 35%),radial-gradient(ellipse at 95% 12%,rgba(64,195,255,.14),transparent 31%),radial-gradient(ellipse at 55% 105%,rgba(197,86,255,.09),transparent 45%);background-attachment:fixed}
[data-testid="stHeader"]{background:rgba(8,10,18,.42)}
.block-container{max-width:1450px;padding:1.25rem 2rem 3rem}
h1,h2,h3{font-family:'Manrope',sans-serif!important;letter-spacing:-.04em}
h1{font-weight:800!important;letter-spacing:-.07em}
p,li{color:#d8dced}
.small{color:var(--muted);font-size:.88rem}
.eyebrow{display:inline-flex;padding:7px 12px;border-radius:999px;background:rgba(255,255,255,.055);border:1px solid var(--line);color:#c8c5ff;text-transform:uppercase;letter-spacing:.14em;font-size:.72rem}
.hero{padding:1.5rem 0 1rem}
.hero h1{font-size:clamp(2.6rem,5vw,4.9rem);line-height:1.0;margin:.8rem 0}
.grad{background:linear-gradient(95deg,#fff 0%,#c7bfff 45%,#9ce7ff 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.glass{border:1px solid var(--line);border-radius:24px;padding:22px;background:linear-gradient(145deg,rgba(255,255,255,.08),rgba(255,255,255,.025));box-shadow:0 25px 80px rgba(0,0,0,.19);backdrop-filter:blur(24px);transition:transform .28s ease,border-color .28s ease,box-shadow .28s ease}
.glass:hover{transform:translateY(-3px);border-color:rgba(182,180,255,.28);box-shadow:0 30px 100px rgba(0,0,0,.27)}
.glass-lite{border:1px solid var(--line);border-radius:18px;padding:16px;background:rgba(255,255,255,.035)}
.kicker{font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;color:#9fa8c5}
.pill{display:inline-flex;padding:5px 9px;border-radius:999px;font-size:.72rem;border:1px solid rgba(169,166,255,.25);background:rgba(140,130,255,.12);color:#d8d5ff}
.stButton>button,.stDownloadButton>button{border-radius:999px;border:1px solid rgba(255,255,255,.16);background:linear-gradient(110deg,#dfddff,#9ce4ff);color:#101321;font-weight:700;transition:transform .2s,box-shadow .2s;padding:.6rem 1rem}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);box-shadow:0 10px 35px rgba(132,130,255,.28);border-color:#fff}
div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea{border-radius:14px;background:rgba(255,255,255,.045);color:#f4f5fc;border-color:var(--line)}
div[data-testid="stMetric"]{background:rgba(255,255,255,.04);border:1px solid var(--line);padding:17px 18px;border-radius:19px}
[data-testid="stMetricValue"]{font-family:'Manrope',sans-serif;letter-spacing:-.06em}
hr{border-color:var(--line)}
.orb{height:178px;width:178px;border-radius:48% 52% 62% 38% / 47% 41% 59% 53%;margin:auto;background:radial-gradient(circle at 31% 25%,rgba(255,255,255,.95),rgba(183,175,255,.68) 9%,rgba(105,95,255,.65) 27%,rgba(56,173,255,.28) 53%,rgba(157,91,255,.08) 70%);box-shadow:inset -15px -18px 36px rgba(5,8,20,.55),inset 12px 10px 35px rgba(255,255,255,.22),0 0 55px rgba(120,113,255,.18);animation:floaty 7s ease-in-out infinite,hue 18s linear infinite}
@keyframes floaty{0%,100%{transform:translateY(0) rotate(-7deg)}50%{transform:translateY(-12px) rotate(5deg)}}
@keyframes hue{to{filter:hue-rotate(25deg)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
@media(max-width:780px){.block-container{padding:1rem .8rem 2rem}.glass{padding:17px}.hero h1{font-size:2.8rem}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def priority_color(priority):
    return {"High": "#ffb2c1", "Medium": "#d7c6ff", "Low": "#a6e8dc"}.get(priority, "#cbd1e7")

def render_task(task):
    mark = "✓" if task["done"] else "○"
    faded = "opacity:.5;text-decoration:line-through;" if task["done"] else ""
    st.markdown(
        f'<div class="glass-lite" style="margin-bottom:9px;{faded}">'
        f'<div style="display:flex;align-items:center;gap:10px">'
        f'<span style="font-size:1.2rem;color:{priority_color(task["priority"])}">{mark}</span>'
        f'<div style="flex:1"><b>{task["title"]}</b><div class="small">{task["project"]} · Due {task["due"]}</div></div>'
        f'<span class="pill">{task["priority"]}</span></div></div>',
        unsafe_allow_html=True,
    )

nav_cols = st.columns([1.5, 4.4, 1.1])
with nav_cols[0]:
    st.markdown('<div style="font-family:Manrope;font-weight:800;font-size:1.25rem;letter-spacing:-.06em">✦ neural<span class="grad">desk</span></div><div class="small">FOCUS OPERATING SYSTEM</div>', unsafe_allow_html=True)
with nav_cols[1]:
    active_view = st.radio("Navigation", ["Overview", "Tasks", "Focus", "Insights"], horizontal=True, label_visibility="collapsed", key="nav")
with nav_cols[2]:
    st.markdown('<div style="text-align:right;padding-top:5px"><span class="pill">● LOCAL MODE</span></div>', unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(175,174,255,.3),transparent);margin:15px 0 20px"></div>', unsafe_allow_html=True)

tasks = st.session_state.tasks
summary = build_task_summary(tasks)
done, total = summary["completed"], summary["total"]
today = date.today().strftime("%A, %d %B")

if active_view == "Overview":
    a, b = st.columns([1.7, 1], gap="large")
    with a:
        st.markdown(f'<div class="hero"><div class="eyebrow">✦ YOUR SPACE, REIMAGINED</div><h1>Make room for<br><span class="grad">deep work.</span></h1><p style="color:#a9b1c8;max-width:600px;line-height:1.8">One calm place for your tasks, focus sessions, and momentum. Keep the signal. Leave the noise.</p><div class="small">{today} &nbsp;·&nbsp; A fresh page, ready when you are.</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="glass" style="text-align:center;height:260px;display:flex;flex-direction:column;justify-content:center"><div class="orb"></div><div style="font-size:.8rem;color:#bac3df;margin-top:14px;letter-spacing:.08em">YOUR MIND, IN FLOW</div></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Tasks captured", total, "Keep it clear")
    cols[1].metric("Completed", done, f"{task_completion_rate(tasks)}% of your list")
    cols[2].metric("Open priorities", summary["open_high"], "High priority")
    cols[3].metric("Focus mode", "25 min", "Pomodoro default")
    left, right = st.columns([1.25, .75], gap="large")
    with left:
        st.markdown('<div class="glass"><div class="kicker">TODAY · MOMENTUM</div><h3 style="margin:.3rem 0 1rem">Your action board</h3></div>', unsafe_allow_html=True)
        open_tasks = [t for t in tasks if not t["done"]]
        if not open_tasks:
            st.success("All clear — you've completed every task in your list.")
        for task in open_tasks[:5]:
            render_task(task)
        if st.button("Open task manager →", key="overview_tasks", use_container_width=True):
            st.session_state.nav = "Tasks"
            st.rerun()
    with right:
        st.markdown('<div class="glass"><div class="kicker">A LITTLE STRUCTURE</div><h3 style="margin:.3rem 0 .6rem">Daily progress</h3><div class="small">Small wins create durable momentum.</div></div>', unsafe_allow_html=True)
        st.progress(task_completion_rate(tasks) / 100)
        st.markdown(f'<div style="display:flex;justify-content:space-between"><span class="small">Completed</span><b>{done}/{total}</b></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-lite" style="margin-top:16px"><div class="kicker">TODAY\'S RESET</div><p style="line-height:1.75">Pick one important task. Mute the distractions. Give it 25 honest minutes.</p></div>', unsafe_allow_html=True)

elif active_view == "Tasks":
    st.markdown('<div class="hero"><div class="eyebrow">TASK MANAGER</div><h1>Your ideas,<br><span class="grad">in motion.</span></h1><p class="small">Capture the next step, set its priority, and move it forward.</p></div>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("new_task_form", clear_on_submit=True):
            title = st.text_input("Task title", placeholder="What would you like to move forward?")
            c1, c2, c3 = st.columns(3)
            project = c1.text_input("Project", value="Personal")
            priority = c2.selectbox("Priority", ["High", "Medium", "Low"], index=1)
            due = c3.selectbox("Due", ["Today", "Tomorrow", "This week", "Someday"])
            submitted = st.form_submit_button("＋ Add task")
            if submitted:
                if title.strip():
                    st.session_state.tasks.insert(0, {"id": st.session_state.task_counter, "title": title.strip(), "project": project.strip() or "Personal", "priority": priority, "done": False, "due": due})
                    st.session_state.task_counter += 1
                    st.success("Task added.")
                    st.rerun()
                else:
                    st.warning("Enter a task title first.")
    st.markdown("### Your list")
    filter_by = st.selectbox("Show tasks", ["All tasks", "Open only", "Completed only"])
    visible = [t for t in st.session_state.tasks if filter_by == "All tasks" or (filter_by == "Open only" and not t["done"]) or (filter_by == "Completed only" and t["done"])]
    if not visible:
        st.info("Nothing here yet. Add a task above to get started.")
    for task in visible:
        c1, c2, c3 = st.columns([.08, .72, .2], vertical_alignment="center")
        with c1:
            new_done = st.checkbox("Done", value=task["done"], key=f"done_{task['id']}", label_visibility="collapsed")
            if new_done != task["done"]:
                for item in st.session_state.tasks:
                    if item["id"] == task["id"]:
                        item["done"] = new_done
                st.rerun()
        with c2:
            st.markdown(f'**{task["title"]}**  <span class="small">· {task["project"]} · {task["due"]}</span>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<span class="pill">{task["priority"]}</span>', unsafe_allow_html=True)
    if st.session_state.tasks:
        with st.expander("Maintenance"):
            if st.button("Clear completed tasks"):
                st.session_state.tasks = [t for t in st.session_state.tasks if not t["done"]]
                st.rerun()
            st.download_button("Export task list (JSON)", json.dumps(st.session_state.tasks, indent=2), file_name="neuraldesk-tasks.json", mime="application/json")

elif active_view == "Focus":
    st.markdown('<div class="hero"><div class="eyebrow">FOCUS MODE</div><h1>Enter your<br><span class="grad">flow state.</span></h1><p class="small">One session. One intention. Fewer interruptions.</p></div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="large")
    with left:
        if st.session_state.timer_running and st.session_state.focus_deadline is not None:
            st.session_state.focus_seconds = max(0, int(st.session_state.focus_deadline - time.time()))
            if st.session_state.focus_seconds <= 0:
                st.session_state.timer_running = False
                st.session_state.focus_deadline = None
                st.success("Focus session complete. Take a mindful break.")
        mins, secs = divmod(max(0, int(st.session_state.focus_seconds)), 60)
        st.markdown('<div class="glass" style="text-align:center"><div class="kicker">POMODORO SESSION</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass" style="text-align:center;margin-top:12px"><div style="font-family:Manrope;font-size:clamp(3.5rem,8vw,5.5rem);font-weight:800;letter-spacing:-.08em">{mins:02d}:{secs:02d}</div><div class="small">{"Session running" if st.session_state.timer_running else "Ready when you are"}</div></div>', unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        if p1.button("▶ Start / resume", use_container_width=True):
            st.session_state.timer_running = True
            st.session_state.focus_deadline = time.time() + st.session_state.focus_seconds
            st.rerun()
        if p2.button("Ⅱ Pause", use_container_width=True):
            if st.session_state.focus_deadline is not None:
                st.session_state.focus_seconds = max(0, int(st.session_state.focus_deadline - time.time()))
            st.session_state.timer_running = False
            st.session_state.focus_deadline = None
        if p3.button("↺ Reset", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.focus_seconds = 25 * 60
            st.session_state.focus_deadline = None
            st.rerun()
        length = st.select_slider("Session length", options=[15, 20, 25, 30, 45, 60], value=25, format_func=lambda x: f"{x} min")
        if st.button("Set session length"):
            st.session_state.focus_seconds = int(length * 60)
            st.session_state.timer_running = False
            st.session_state.focus_deadline = None
            st.rerun()
    with right:
        st.markdown('<div class="glass"><div class="kicker">YOUR INTENTION</div><h3>Before you begin</h3><p style="color:#aab2c9;line-height:1.8">Write one clear outcome for this focus block. A smaller finish line is easier to start and easier to cross.</p></div>', unsafe_allow_html=True)
        intention = st.text_area("What will you work on?", placeholder="For the next 25 minutes, I will…", height=120, key="focus_intention")
        if st.button("Save intention"):
            st.session_state.focus_intention_saved = intention.strip()
            st.success("Intention saved for this session.")
        if st.session_state.focus_intention_saved:
            st.markdown(f'<div class="glass-lite"><div class="kicker">CURRENT INTENTION</div><p>{st.session_state.focus_intention_saved}</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-lite" style="margin-top:14px"><b>Focus ritual</b><p class="small" style="line-height:1.8">1. Close one distraction. 2. Keep one tab open. 3. Start before you feel ready. 4. Stop when the timer ends.</p></div>', unsafe_allow_html=True)
    if st.session_state.timer_running and st.session_state.focus_deadline is not None:
        deadline_ms = int(st.session_state.focus_deadline * 1000)
        components.html(f"""<script>
          const deadline = {deadline_ms};
          const tick = () => {{
            const left = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
            const displays = Array.from(window.parent.document.querySelectorAll("div"))
              .filter(el => /^\\d{{2}}:\\d{{2}}$/.test((el.textContent || "").trim()));
            if (displays.length) displays[displays[displays.length - 1].textContent =
              String(Math.floor(left / 60)).padStart(2, "0") + ":" + String(left % 60).padStart(2, "0");
            if (left <= 0) window.parent.location.reload();
          }};
          tick(); setInterval(tick, 1000);
        </script>""", height=0, scrolling=False)

elif active_view == "Insights":
    st.markdown('<div class="hero"><div class="eyebrow">INSIGHTS</div><h1>Progress you<br><span class="grad">can see.</span></h1><p class="small">A live view of the tasks you have captured in this session.</p></div>', unsafe_allow_html=True)
    if not st.session_state.tasks:
        st.info("Add a few tasks to see insights.")
    else:
        df = pd.DataFrame(st.session_state.tasks)
        s1, s2, s3 = st.columns(3)
        s1.metric("Completion rate", f"{task_completion_rate(tasks)}%")
        s2.metric("High priority open", summary["open_high"])
        s3.metric("Projects", int(df.project.nunique()))
        pcol, qcol = st.columns(2, gap="large")
        with pcol:
            by_status = df.assign(Status=df.done.map({True: "Completed", False: "Open"})).groupby("Status").size().reset_index(name="Tasks")
            fig = px.pie(by_status, values="Tasks", names="Status", hole=.72, title="Your task balance", color_discrete_sequence=["#9b91ff", "#66d5ef"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eef0ff", title_font_color="#f4f5fc", legend_title_text="", margin=dict(l=10,r=10,t=52,b=10))
            fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="#11131d", width=3)))
            st.plotly_chart(fig, use_container_width=True)
        with qcol:
            by_project = df.groupby("project").size().reset_index(name="Tasks").sort_values("Tasks", ascending=True)
            fig2 = px.bar(by_project, x="Tasks", y="project", orientation="h", title="Tasks by project", color="Tasks", color_continuous_scale=["#60d9ee", "#9285ff"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eef0ff", title_font_color="#f4f5fc", coloraxis_showscale=False, margin=dict(l=10,r=15,t=52,b=10), yaxis_title="", xaxis_title="")
            fig2.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,.08)")
            fig2.update_yaxes(showgrid=False)
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### Next best move")
        open_high = [t for t in st.session_state.tasks if not t["done"] and t["priority"] == "High"]
        if open_high:
            st.markdown(f'<div class="glass"><div class="kicker">HIGH PRIORITY</div><h3>{open_high[0]["title"]}</h3><p class="small">Start here, then reassess your list after a focus block.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="glass"><h3>Protect your momentum</h3><p class="small">No high-priority open tasks. Pick the task that moves your main goal forward.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="footer">NEURALDESK · FOCUS OPERATING SYSTEM<br>Built with Streamlit, Plotly & a little calm. Data stays in the active session; export tasks to keep a copy.</div>', unsafe_allow_html=True)
