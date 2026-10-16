# ✦ NextRole — AI Career Assistant

An Apple-inspired, dark glassmorphism career studio built with Streamlit. Compare resume text with a job description, review matched skills and potential gaps, rehearse interview questions, and export a simple report.

Inspired by the career-assistant idea in [500 AI Agents Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects). This is a separate implementation; it does not copy that repository's source code.

## Features

- **Elegant interface:** deep midnight background, soft aurora gradients, glass panels, gentle hover motion, and responsive layout.
- **Resume input:** upload a text-based PDF, DOCX, or TXT file, or paste resume text.
- **Job-fit snapshot:** approximate keyword alignment score, matched skills, potential gaps, and detected resume skills.
- **Interview practice:** role-focused starter questions and STAR answer guidance.
- **Export:** download the results as a text report.
- **No API key:** local, transparent keyword matching; no paid AI service required.

## Run locally

Python 3.10 or newer is recommended.

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

On macOS/Linux, use `python3 -m pip` and `python3 -m streamlit run app.py` if needed.

## Deploy on Streamlit Community Cloud

1. Open https://share.streamlit.io/
2. Sign in with GitHub and choose this repository.
3. Set the main file path to `app.py`.
4. Click **Deploy**.

No secrets or API keys are required.

## How scoring works

The app detects a curated list of common technical and professional skills in the resume and job description. When job skills are detected, the match score is the percentage of detected job-description skills also detected in the resume. If no listed skills are detected in the job description, it falls back to a basic word-overlap estimate.

**Important:** this is a lightweight keyword heuristic, not a true LLM assessment, hiring recommendation, or prediction of interview success. Missing keywords do not necessarily mean missing skills. Always tailor your resume truthfully and review the results yourself.

## Privacy

Uploaded files and pasted text are processed by the running Streamlit app session. This app does not intentionally send resume text to an external AI API. For a public deployment, review the hosting provider's privacy and retention terms before using sensitive personal information.

## Credits

Concept inspiration: [ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects).

## License

MIT
