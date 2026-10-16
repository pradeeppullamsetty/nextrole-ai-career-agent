# ✦ NeuralDesk — Focus Operating System

An intermediate-level productivity workspace with an Apple-inspired 3D/glassmorphism interface, soft aurora gradients, floaty orb, hover lift, interactive task management, focus timer, and productivity insights.

ECC-inspired engineering approach: research-first, small explicit functions, controlled state, clear validation, and a practical verification checklist. This project references the workflow philosophy from [ECC](https://github.com/affaan-m/ECC); it does not copy ECC's source code or bundle its skills.

## What works

- **Overview:** overview metrics, action board, daily progress.
- **Tasks:** add tasks, set project and priority, mark complete, filter lists, clear completed items, export as JSON.
- **Focus:** configure a 15–60 minute Pomodoro-style session, start/pause/reset, save an intention.
- **Insights:** Plotly task-status and project charts.
- **No API keys required:** the current app is functional without paid external services.
- **Responsive premium UI:** midnight palette, glass panels, ambient gradients, animated orb, subtle hover and motion-reduction support.

## Run locally

Python 3.10+ recommended.

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If `py` is unavailable on your machine, install Python and use `python -m pip` and `python -m streamlit run app.py`.

## Deploy to Streamlit Community Cloud

1. Visit https://share.streamlit.io/ and sign in with GitHub.
2. Select this repository.
3. Set **Main file path** to `app.py`.
4. Deploy. No secrets are needed.

## Data and limitations

Streamlit session state keeps changes while that app session is active, but it is not a durable database. Export your tasks as JSON if you need a backup. The timer is a simple session timer, not a background service, and its countdown may require refreshing the page.

## Inspiration

- [ECC — agentic engineering workflows and reusable skills](https://github.com/affaan-m/ECC)
- Visual direction: Apple-inspired dark glass, depth, aurora gradients, and understated motion.

## License

MIT
