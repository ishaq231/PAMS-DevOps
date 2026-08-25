# PAMS - Paragon Apartment Management System

A desktop application built to manage multi-location apartment operations. Developed as a group project for the **Advanced Software Development** module (UFCF8S-30-2).

## Features

Role-based panels for **Admin**, **Manager**, **Front Desk**, **Finance**, **Maintenance**, and **Tenant** users, covering tenant & lease management, maintenance tickets, finance reporting, and multi-location apartment operations.

## Project Structure

```
src/
├── gui/        # PyQt6 windows and role-based panels
└── database/   # SQLAlchemy models, connection, and seed data
tests/          # pytest / pytest-qt test suite
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI | PyQt6 |
| Database | MySQL 8.0 (via SQLAlchemy + PyMySQL) |
| Authentication | bcrypt |
| PDF Reports | ReportLab |
| Charts | Matplotlib |
| Testing | pytest, pytest-qt |
| CI/CD | GitHub Actions |

## Requirements

- **Python** 3.10 or higher
- **MySQL Server** 8.0 or higher (running locally or remotely)
- **pip** (Python package manager)
- Dependencies listed in `requirements.txt`

## Instructions for Running:

- Install dependencies from `requirements.txt` using one of the following options:

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

- Create a `.env` file with the following structure:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your password for your server 
DB_NAME=asd_project
DB_PORT=3306
```

- Set up the database. You can either import the provided SQL dump (quickest) or seed from scratch:

Option A (Import the dump):

```bash
mysql -u root -p asd_project < Database_dump/asd_projects_dump.sql
```

Option B (Run the seed script):

```bash
python src/database/seed_data.py
```

- Run the application:

```bash
python src/gui/login_window.py
```

- Use the credentials from `LOGINS.md` to log in as different user roles and explore the features.

## Demo Credentials

The `LOGINS.md` file contains pre-seeded login credentials for testing the application. It includes:

- **Staff accounts** for each role: Administrator, Manager, Front Desk, Finance, and Maintenance
- **Tenant accounts** across different locations and apartments
- **Staff signup codes** for registering new staff accounts through the Sign Up page

---

# Testing

The project uses `pytest` with `pytest-qt` for automated GUI and unit testing.
To run all tests:

```bash
pytest tests/
```

Alternatively, run specific test modules:

```bash
pytest tests/gui/test_login_window.py
pytest tests/gui/test_maintenance_panel.py
pytest tests/gui/test_admin_panel.py
```

The tests are also run automatically on each commit via GitHub Actions CI pipeline, ensuring code quality and preventing regressions.

---

## Authors

Developed as a group project by:

- Hasaan Ahmad
- Ishaq Modassir Mushtaq
- Rayyan Tahir
- Royden Dias

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
