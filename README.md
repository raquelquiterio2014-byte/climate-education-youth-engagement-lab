# Climate Education & Youth Engagement Lab V1.0

**COP31 AI Solutions Lab — Day 6 (November 14, 2026)**

Independent educational Streamlit prototype for climate literacy and youth engagement. **All code, content and UI are in English.** The app is intended for general audiences and does not collect children's identities.

## Modules

1. **Overview:** learning pathway and indicators.
2. **Learning Hub:** four progressive lessons with theory, analogy, example, and source links.
3. **Climate Quiz:** eight questions, explanations, anonymous local quiz history.
4. **Youth Action Lab:** five hypothetical actions with *game points*, not estimated CO₂ reductions.
5. **AI & Human Review:** optional live Gemini 2.5 Flash explanation using supplied educational source excerpts; structured output, source ID validation and reviewer decision.
6. **Progress & Export:** CSV/JSON downloads, SQLite audit, methodology and limitations.

The original design called for five modules; the final interface separates Progress & Export into a sixth tab for clarity.

## Setup (Windows / PyCharm / Python 3.12)

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with your own Google Gemini API key. **Never commit `.env` to GitHub.** Without a key, the lessons, quiz, simulation and export still work.

```powershell
python -m pytest -q
python -m streamlit run app.py
```

If Streamlit is already using port 8501:

```powershell
python -m streamlit run app.py --server.port 8502
```

## Data and verification

- The educational content is in `data/content.json`. Reference URLs point to IPCC, NASA, UNESCO and UNFCCC.
- Only the short IPCC line is presented as an excerpt. Other reference summaries are **paraphrases, not verified quotations**. Check original sources before publication.
- AI source ID validation ensures IDs exist among provided material, **not** that conclusions are true or grounded in the complete original documents.
- AI outputs are marked unverified until human review. Reviewer decisions are stored locally in `local_data/learning.sqlite3`.
- No real-world emissions savings, learning effectiveness, child engagement outcomes or environmental impact have been measured.
- The application is not affiliated with or endorsed by COP31, UNFCCC, IPCC, NASA or UNESCO.
- The Gemini API requires internet access and may incur charges according to your Google account.

## Tests

`python -m pytest -q` covers content consistency, scoring, action points, validation, hashes, and SQLite persistence. The test suite does **not** call the live Gemini API.

## Privacy

No student names, ages, email addresses, or individual identifiers are requested. Quiz attempts are anonymous. The reviewer field accepts a role or pseudonym. Local records can be deleted by removing `local_data/learning.sqlite3` when the app is closed. The selected lesson and reference excerpts are transmitted to Google's Gemini API only when the user clicks the AI button.

**Evidence first. Engineering second. Measurable impact as the goal.**
