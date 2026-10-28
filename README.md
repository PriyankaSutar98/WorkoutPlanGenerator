# Workout Plan Generator

A Streamlit app that generates a personalized weekly workout plan using the Groq API.
Pick a goal, experience level, training days, available equipment and any injuries, and
get a plan with warm-ups, exercise tables, cool-downs and a 4-week progression.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Groq API key from https://console.groq.com

## Setup

1. Install dependencies:

   ```
   uv sync
   ```

   Or with pip:

   ```
   pip install groq python-dotenv streamlit
   ```

2. Create a `.env` file in this folder:

   ```
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=openai/gpt-oss-20b   # optional
   ```

   Never commit `.env` (it is in `.gitignore`).

## Run

```
uv run streamlit run workoutplangenerator.py
```

Or, without uv: `streamlit run workoutplangenerator.py`

## Troubleshooting

### `uv sync` fails with "groq was not found in the package registry"

`groq` is on PyPI, so this usually means your user-level uv or pip config points at a
private package index (for example a corporate AWS CodeArtifact repository) whose
login token has expired. The index returns `401`, and uv reports the package as not found.

Either bypass the user config for this project:

```
uv sync --no-config
uv run --no-config streamlit run workoutplangenerator.py
```

or refresh your private index credentials (for CodeArtifact, re-run
`aws codeartifact login ...` and update the index URL in
`%APPDATA%\uv\uv.toml` / your pip config).

### "GROQ_API_KEY is missing"

Check that `.env` is in the same folder as `workoutplangenerator.py` and that you restarted
the app after editing it.

## Disclaimer

Plans are AI-generated and not medical advice. Consult a professional if you have
injuries or health conditions.
