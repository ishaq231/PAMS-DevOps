# PAMS DevOps Pipeline

This repo builds on **PAMS (Paragon Apartment Management System)**, a desktop application originally developed as a group project for the **Advanced Software Development** module (UFCF8S-30-2) at UWE Bristol.

This specific repo is an individual project layered on top of that group work: adding a REST API, containerisation, and an automated deployment pipeline around the existing backend, as a hands-on DevOps and cloud deployment showcase.

**What's original group work vs individual work:**

- The PyQt6 GUI (`src/gui/`) and the underlying database/backend architecture (`src/database/`) are from the original group project. Ishaq Modassir Mushtaq was sole architect of the database schema and the Python backend model classes within that team.
- The FastAPI layer (`api/`), Docker setup, and CI/CD deployment pipeline in this repo are individual work, built afterward by Ishaq as a standalone project.

## What This Adds

The original PAMS backend was only ever reachable through the PyQt6 desktop GUI. This project gives that same backend a second entry point: a small REST API built with **FastAPI**, so the exact same model classes (`User`, `Tenant`, etc) can be called over HTTP instead of only from button clicks in the desktop app. That API is then containerised with **Docker** and deployed automatically via a **CI/CD pipeline**, giving it a live, publicly reachable URL that redeploys on every push.

The desktop GUI is untouched and still works exactly as it did before.

```
PyQt6 GUI ─┐
            ├─→ shared model classes (src/database/) → MySQL
FastAPI  ──┘
```

## Project Structure

```
api/            # FastAPI layer exposing the backend over HTTP (individual project work)
src/
├── gui/        # PyQt6 windows and role-based panels (group project)
└── database/   # Model classes, connection handling, and seed data (group project)
tests/          # pytest / pytest-qt test suite (group project)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI | PyQt6 |
| API | FastAPI, uvicorn |
| Database | MySQL 8.0, via `mysql-connector-python` |
| Authentication | bcrypt |
| Containerisation | Docker |
| CI/CD | GitHub Actions |
| Testing | pytest, pytest-qt |

## Status

- [x] Group project: PyQt6 desktop app, 16-table MySQL schema, 272-test pytest suite, CI running on every push
- [x] Public individual repo set up, separated from the original group repo
- [ ] FastAPI layer, in progress: `/login` endpoint built, remaining models to follow
- [ ] Docker containerisation
- [ ] CI/CD deployment pipeline to a live public URL

## Requirements

- **Python** 3.10 or higher
- **MySQL Server** 8.0 or higher (running locally or remotely)
- **pip** (Python package manager)
- Dependencies listed in `requirements.txt`

## Running the Desktop App

Install dependencies from `requirements.txt` using one of the following options:

Option 1 (local/system Python install):

```bash
pip install -r requirements.txt
```

Option 2 (recommended, isolated `.venv`):

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with the following structure:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=asd_project
DB_PORT=3306
```

Set up the database. You can either import the provided SQL dump (quickest) or seed from scratch:

Option A (import the dump):

```bash
mysql -u root -p asd_project < Database_dump/asd_projects_dump.sql
```

Option B (run the seed script):

```bash
python src/database/seed_data.py
```

Run the application:

```bash
python src/gui/login_window.py
```

Use the credentials from `LOGINS.md` to log in as different user roles and explore the features.

## Running the API

With the same `.env` file and database set up as above:

```bash
uvicorn api.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive API documentation, where each endpoint can be tried directly in the browser.

## Testing

The project uses `pytest` with `pytest-qt` for automated GUI and unit testing.

Run all tests:

```bash
pytest tests/
```

Run specific test modules:

```bash
pytest tests/gui/test_login_window.py
pytest tests/gui/test_maintenance_panel.py
pytest tests/gui/test_admin_panel.py
```

Tests also run automatically on every push via GitHub Actions.

## Original Group Project Authors

The base PAMS application (GUI, database design, and backend) was developed as a group project by:

- Hasaan Ahmad
- Ishaq Modassir Mushtaq
- Rayyan Tahir
- Royden Dias

The API, Docker, and CI/CD work in this repo is an individual continuation of that project by Ishaq Modassir Mushtaq.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
