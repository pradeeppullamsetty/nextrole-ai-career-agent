# ✦ NeuralDesk — Focus Operating System

An intermediate-level productivity workspace built with Streamlit and Plotly. It pairs an Apple-inspired visual language with real task-management and focus workflows: glass-like panels, soft aurora lighting, a softly animated 3D-feeling orb, carefully tuned hover states, and responsive layouts.

## Experience

- **Overview:** today's task snapshot, completion progress, open priorities, and a focused action board.
- **Task manager:** create, prioritize, filter, complete, clear, and export tasks as JSON.
- **Focus mode:** set a 15–60 minute Pomodoro-style session and save the intention for your current session.
- **Insights:** interactive Plotly charts for task completion and projects.
- **No API key required.** Current features work locally inside the Streamlit app session.
- **Accessibility-minded motion:** prefers-reduced-motion support and responsive spacing.

## ECC-inspired engineering

Workflow principles were informed by [ECC](https://github.com/affaan-m/ECC) and its [frontend-design-direction skill](https://github.com/affaan-m/ECC/tree/main/skills/frontend-design-direction). This repository is a distinct implementation and does not copy or package ECC code or skills.

## Run locally

Python 3.10 or newer is recommended.

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

On a system where `py` is unavailable, use `python -m pip install -r requirements.txt` and `python -m streamlit run app.py`.

## Run helper tests

```bash
py -m pip install pytest
py -m pytest -q
```

## Deploy to Streamlit Community Cloud

1. Go to https://share.streamlit.io/ and sign in with GitHub.
2. Select this repository.
3. Set the main file to `app.py`.
4. Click **Deploy**. No secrets are required.

## Data notes

Tasks and settings are held in the active Streamlit session, not a durable database. Export your task list as JSON for a backup. The focus timer is a lightweight session timer and is not a background service; a refresh may be needed to update the visible time.

## License

MIT
