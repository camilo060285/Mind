# 🛠 Development Workflow

Mind uses a modern, strict development pipeline.

---

## 🧪 Tests

Run all tests:

```bash
pytest -v

🧹 Linting
ruff check .

🎨 Formatting
black .

🔍 Type Checking
mypy .

🔄 Pre‑commit
Install: pre-commit install

Run manually:
pre-commit run --all-files

🚦 CI
GitHub Actions runs:
• pytest
• ruff
• black
• mypy
See .github/workflows/ci.yml.


---

# 🤝 `docs/contributing.md`

```markdown
# 🤝 Contributing to Mind

Thank you for contributing to Mind.

Mind is a modular, privacy‑first agentic meta‑system.  
Contributions should respect its principles:

- sovereignty  
- transparency  
- meaning  

---

## 🧪 Requirements

- Python 3.11+
- pytest
- ruff
- black
- mypy
- pre‑commit

---

## 🛠 Workflow

1. Fork the repo
2. Create a feature branch
3. Run tests + pre‑commit
4. Submit a PR

---

## 🧹 Code Style

Mind uses:

- black
- ruff
- mypy
- pre‑commit

All PRs must pass CI.

---

## 📘 Documentation

All new features must include documentation in `docs/`.

---

## 🔒 Philosophy

Mind is built to empower individuals, not institutions.  
Contributions should align with this ethos.

