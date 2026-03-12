# 🎯 Exam Ace Analytics

A personal exam performance tracker built with **Streamlit**. Designed for competitive exam aspirants who want to track mock test scores, analyze subject-wise performance, and monitor their journey toward a target rank.

> Built originally for **NIMCET** preparation, but fully configurable for any exam — GATE, CAT, UPSC, JEE, and more.

---

## ✨ Features

- **Setup Wizard** — first-run configuration for your exam, target rank, institution, subjects, and exam date
- **Dashboard** — percentile trend charts, rolling average, study streak, and predicted AIR at a glance
- **Add Test** — log mock test scores with rank, participants, accuracy; auto-calculates percentile and predicted rank
- **Add Subject** — break down each test by subject-wise scores and accuracy
- **Mock Analysis** — question-by-question breakdown with topic, difficulty, status, and time tracking; includes weak topic detection and speed vs. accuracy scatter plots
- **Analytics Hub** — deeper cross-test analysis across subjects and performance trends
- **Profile** — edit your exam config anytime without losing test data
- **Delete Test** — remove tests and all associated data with cascade delete

---

## 🗂️ Project Structure

```
exam-ace/
├── app.py                  # Main entry point
├── database.py             # SQLAlchemy engine & session management
├── models.py               # ORM models: Test, Subject, Question
├── config_manager.py       # Config read/write helpers
├── styles.py               # Global CSS styles
├── config.json             # Auto-generated on first run (gitignored)
├── exam_tracker.db         # SQLite database (auto-created, gitignored)
├── requirements.txt
└── pages/
    ├── __init__.py         # Required (can be empty)
    ├── setup_wizard.py
    ├── dashboard.py
    ├── add_test.py
    ├── add_subject.py
    ├── mock_analysis.py
    ├── analytics_hub.py
    ├── delete_test.py
    └── profile.py
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

- Python **3.9+**

### 2. Clone the repository

```bash
git clone https://github.com/your-username/exam-ace.git
cd exam-ace
```

### 3. (Recommended) Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create the pages `__init__.py`

```bash
# Windows
type nul > pages\__init__.py

# macOS / Linux
touch pages/__init__.py
```

### 6. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🚀 First Run

On first launch, you'll see the **Setup Wizard**. Fill in:

| Field | Example |
|---|---|
| Exam Name | NIMCET |
| Target Rank | 40 |
| Target Institution | NIT Tiruchirapalli |
| Exam Date | 2026-06-06 |
| Total Candidates | 50000 |
| Total Marks | 1000 |
| Subjects | Mathematics, LR & Quant, Computer, English |

This creates a `config.json` file and the SQLite database. You can edit all of this later from the **Profile** page.

---

## 📊 How to Use

1. **Add Test** — after every mock test, log your score, rank, and participants
2. **Add Subject** — optionally break down the test by subject scores
3. **Mock Analysis → Add Questions** — for deep dives, log individual questions with topic, difficulty, and time taken
4. **Dashboard** — monitor your percentile trend and predicted AIR over time
5. **Analytics Hub** — cross-test subject performance comparisons
6. **Mock Analysis → Analysis** — identify weak topics and time management issues

---

## 🔒 Notes

- `config.json` and `exam_tracker.db` are gitignored — your data stays local
- Resetting config (from Profile → Danger Zone) only removes `config.json`; your test data in the database is preserved
- The database is SQLite — no server setup needed

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| [Streamlit](https://streamlit.io/) | UI framework |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM & database management |
| [Plotly](https://plotly.com/python/) | Interactive charts |
| [Pandas](https://pandas.pydata.org/) | Data manipulation |
| SQLite | Local database (via SQLAlchemy) |

---

## 📄 License

MIT License — free to use and modify for personal use.
