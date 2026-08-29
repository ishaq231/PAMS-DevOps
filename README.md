# PAMS DevOps Pipeline

This repo builds on **PAMS (Paragon Apartment Management System)**, a desktop application originally developed as a group project for the **Advanced Software Development** module (UFCF8S-30-2) at UWE Bristol.

This specific repo is an individual project layered on top of that group work: a REST API, a web frontend, containerisation, and a fully automated, test-gated deployment pipeline, built as a hands-on DevOps and cloud deployment showcase.

**Live:**

- Web app: https://pams-devops-1.onrender.com
- API docs: https://pams-devops.onrender.com/docs

Both run on Render's free tier, which spins down after 15 minutes of inactivity. The first request after a while may take 30–60 seconds to wake the service back up.

**What's original group work vs individual work:**

- The PyQt6 GUI (`src/gui/`) and the underlying database/backend architecture (`src/database/`) are from the original group project. Ishaq Modassir Mushtaq was sole architect of the database schema and the Python backend model classes within that team.
- Everything else in this repo, the FastAPI layer (`api/`), the React frontend (`frontend/`), Docker, and the CI/CD pipeline, is individual work, built afterward as a standalone project.

## What This Adds

The original PAMS backend was only ever reachable through the PyQt6 desktop GUI, a window that only runs on a local machine. This project gives that same backend two new ways in:

1. **A REST API** (`api/`), built with **FastAPI**, exposing every model in `src/database/` — auth, tenants, invoices, payments, complaints, enquiries, locations, apartments, leases, maintenance, users, and staff — over HTTP, secured with **JWT authentication** and **role-based access control**. The original model classes are called directly and never modified.
2. **A web frontend** (`frontend/`), built with **React, TypeScript, and Tailwind**, that talks to that API and visually replicates the desktop app's design system (colours, layout, the sidebar navigation) so it's recognisably the same product, just reachable from a browser instead of a local install.

Both are containerised with **Docker** and deployed via a **CI/CD pipeline**: GitHub Actions runs the backend test suite and a frontend type-check, lint, and build on every push, and Render only deploys a service once its checks pass.

The desktop GUI is untouched and still works exactly as it always did.

```
PyQt6 GUI ──────────────────────────┐
                                      ├──→ shared model classes (src/database/) → MySQL
React frontend ──(HTTPS + JWT)──→ FastAPI ┘
```

## Project Structure

```
api/            # FastAPI layer: auth, RBAC, and one route file per domain (individual work)
frontend/       # React + TypeScript + Tailwind web app (individual work)
src/
├── gui/        # PyQt6 windows and role-based panels (group project)
└── database/   # Model classes, connection handling, and seed data (group project)
tests/          # pytest / pytest-qt test suite (group project)
Dockerfile      # Builds the API image
frontend/Dockerfile   # Multi-stage build: Node compiles the app, nginx serves it
docker-compose.yml    # Runs both services together for local development
```

## API Surface

| Domain | Endpoints |
|---|---|
| Auth | `POST /login`, `GET /me` |
| Tenants | list, get, create |
| Invoices | list, list-for-tenant, create, update, mark paid |
| Payments | list, list-for-tenant, create, update |
| Complaints | list, get, list-for-tenant, stats, create, update status, delete |
| Enquiries | list, list-for-tenant, create |
| Locations | list, create |
| Apartments | list, count, update, update status, update rent |
| Leases | list, list-for-tenant, create, update, update status, terminate |
| Maintenance | list, get, stats, staff, staff availability, list-for-tenant, list-for-staff, create, update status/priority/schedule/cost, assign staff, work logs |
| Users | list, count, get, create, update, delete, change password |
| Staff | list, update |

Every endpoint requires a valid JWT except `POST /login`. Role checks are enforced server-side via FastAPI dependencies (`require_roles`, `require_staff_self`, `require_user_self_or_staff`), not just hidden in the frontend's navigation.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+, TypeScript |
| GUI | PyQt6 |
| API | FastAPI, uvicorn, PyJWT |
| Frontend | React, Vite, Tailwind CSS v4, React Router |
| Database | MySQL 8.0, via `mysql-connector-python` |
| Authentication | bcrypt (passwords), JWT (API sessions) |
| Containerisation | Docker, multi-stage builds, nginx (frontend) |
| CI/CD | GitHub Actions (test → build → deploy), Render |
| Testing | pytest, pytest-qt, tsc, eslint |

## Status

- [x] PyQt6 desktop app, 16-table MySQL schema, 272-test pytest suite
- [x] FastAPI layer covering every model, with JWT auth and role-based access control
- [x] React frontend replicating the desktop app's design system, covering every role
- [x] Docker for both services, `docker-compose.yml` for local development
- [x] CI/CD: tests and frontend checks gate every deploy; both services live on Render
- [ ] A handful of desktop-app screens with no backing data yet: Reports, Settings, Occupancy, Expand Business, Late Payments, Financial Reports, Notifications. These render a "coming soon" state in the frontend rather than fabricated data.

## Requirements

- **Python** 3.10 or higher
- **Node.js** 22 or higher (for the frontend)
- **MySQL Server** 8.0 or higher (running locally or remotely)
- **Docker** (optional, for the containerised setup)

## Running Everything Locally (Docker)

The fastest way to run the API and frontend together:

```bash
docker compose up --build
```

- API: http://localhost:8000 (docs at `/docs`)
- Web app: http://localhost:5173

This needs a `.env` file at the repo root with your database credentials and JWT secret (see below), which `docker-compose.yml` passes into the API container.

## Running the Desktop App

Install dependencies from `requirements.txt`:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file at the repo root:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=asd_project
DB_PORT=3306
JWT_SECRET_KEY=generate_your_own_with_python_secrets_token_urlsafe
```

Set up the database, either by importing the provided dump or seeding from scratch:

```bash
mysql -u root -p asd_project < Database_dump/asd_projects_dump.sql
# or
python src/database/seed_data.py
```

Run the app:

```bash
python src/gui/login_window.py
```

Use the credentials in `LOGINS.md` to log in as different roles.

## Running the API Alone

With the same `.env` as above:

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload
```

Interactive docs at `http://127.0.0.1:8000/docs`.

## Running the Frontend Alone

```bash
cd frontend
npm install
npm run dev
```

Needs a `frontend/.env` with `VITE_API_URL=http://localhost:8000`.

## Testing

Backend:

```bash
pytest tests/
```

Frontend:

```bash
cd frontend
npm run lint
npm run build   # runs the TypeScript compiler, then builds
```

All of the above run automatically in CI on every push. Render only deploys a service once its checks pass.

## Known Limitations & Future Improvements

Things found and deliberately left as-is during the build, worth revisiting with more time:

- **Inconsistent field naming for tenants.** `GET /tenants` returns both `user_id` and `tenant_id` (copied from the same value); `GET /tenants/{id}` only returns `user_id`. This traces back to the original SQL query never aliasing the tenant table's ID, and wasn't changed at the source since the desktop GUI depends on the existing `user_id` key.
- **Some `PATCH` endpoints return a generic 400 for two different situations** — "that ID doesn't exist" and "you sent nothing to update" — because the underlying model methods don't distinguish between them. A stricter API would separate these into 404 and 400.
- **`PUT` vs `PATCH` isn't fully consistent across similar-sounding "update" methods.** Whether an endpoint got `PUT` or `PATCH` depends on whether its underlying method replaces every field or only the ones provided, which varies method by method in the original codebase (documented per-route in code comments).
- **Role checks are enforced, but not location-scoped.** A Manager can currently edit tenants, leases, and apartments across every location, not just their own. Scoping by `location_id` would be a natural next step.
- **No automated frontend tests yet** — CI currently type-checks, lints, and builds the frontend, but there's no equivalent to the backend's pytest suite for the UI.

If you're reading this as a reviewer and spot something else, it's very likely already known and just hasn't made it onto this list yet.

## Original Group Project Authors

The base PAMS application (GUI, database design, and backend) was developed as a group project by:

- Hasaan Ahmad
- Ishaq Modassir Mushtaq
- Rayyan Tahir
- Royden Dias

Everything else in this repo, the API, frontend, Docker setup, and CI/CD pipeline, is an individual continuation of that project by Ishaq Modassir Mushtaq.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
