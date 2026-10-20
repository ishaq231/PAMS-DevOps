# PAMS DevOps Pipeline

A web version of **PAMS (Paragon Apartment Management System)**, an apartment management platform for tenants and staff across several locations. It started as a desktop application built as a group project for the **Advanced Software Development** module (UFCF8S-30-2) at UWE Bristol. This repo is my individual continuation: a REST API, a web frontend, Docker containers and an automated, test gated deployment pipeline.

**Live demo**

- Web app: https://pams-devops-1.onrender.com
- API docs (Swagger): https://pams-devops.onrender.com/docs

Demo accounts for every role are listed in [LOGINS.md](LOGINS.md). Both services run on Render's free tier, which sleeps after 15 minutes of inactivity, so the first request can take 30 to 60 seconds.

<!-- Add screenshots here once they are in docs/screenshots/:
![Dashboard](docs/screenshots/dashboard.png)
![GitHub Actions run](docs/screenshots/ci.png)
-->

## Who built what

| Part | Where | Who |
|---|---|---|
| PyQt6 desktop GUI | `src/gui/` | Group project |
| Database schema and Python model classes | `src/database/` | Group project. I was the sole architect of the schema and the backend model classes. |
| pytest and pytest-qt test suite | `tests/` | Group project |
| FastAPI layer | `api/` | Individual |
| React frontend | `frontend/` | Individual |
| Docker, CI pipeline and deployment | `Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `.github/workflows/` | Individual |

## What this adds

The original PAMS backend was only reachable through the desktop GUI, a window that runs on one machine. This project gives the same backend two new ways in:

1. **A REST API** (`api/`) built with FastAPI. It has **62 endpoints** that expose the model classes in `src/database/` for authentication, tenants, invoices, payments, complaints, enquiries, locations, apartments, leases, maintenance, users and staff. It is secured with JWT authentication and role based access control. The original model classes are called directly and are not modified.
2. **A web frontend** (`frontend/`) built with React, TypeScript and Tailwind. It talks to the API and follows the desktop app's design (colours, layout, sidebar), so it is recognisably the same product in a browser.

The desktop app is untouched and still works as before.

```
PyQt6 desktop GUI ────────────────────────┐
                                           ├──> shared model classes (src/database/) ──> MySQL
React frontend ──(HTTPS + JWT)──> FastAPI ─┘
```

## What each role can do in the web app

The system has six roles, five staff roles and tenants. The sidebar is built per role from `frontend/src/lib/nav.ts`, which is ported from the desktop app, and the API enforces the same rules on the server.

| Role | Screens |
|---|---|
| Administrator | User management, apartments, tenants, staff members, lease tracking |
| Manager | Locations, users, apartments, tenants, leases, register tenant, maintenance, complaints, invoices, payments, maintenance requests, log resolution, schedule |
| Front Desk Staff | Register tenant, tenant info, maintenance, complaints |
| Finance Manager | Invoices, payments |
| Maintenance Staff | My requests, log resolution, schedule |
| Tenant | My lease, payments, maintenance, profile |

Desktop screens with no backing data yet (Reports, Settings, Occupancy, Expand Business, Late Payments, Financial Reports, Notifications) show a "coming soon" state instead of invented data.

## Security

- **Passwords** are hashed with bcrypt.
- **Sessions** use signed JWTs (HS256) that expire after 8 hours. The token carries the user's id, role and location.
- **Authorisation is checked on the server**, not only hidden in the frontend. Routes use FastAPI dependencies: `require_roles`, `require_staff_or_self`, `require_staff_self` and `require_user_self_or_staff`.
- **Every endpoint needs a valid token** except `POST /login`.
- **A 401 logs the user out** everywhere in the frontend, handled in one place in `frontend/src/lib/api.ts`.
- **CORS** only allows the local dev origin and the deployed frontend.
- **Secrets are not in the repo.** Database credentials and the JWT secret come from environment variables, and `.env` is git ignored. The accounts in `LOGINS.md` are demo data only.

## Project structure

```
api/                    FastAPI layer (individual)
  main.py               App setup, CORS, router registration
  auth.py               JWT creation and verification, role dependencies
  *_routes.py           One route file per domain
frontend/               React + TypeScript + Tailwind web app (individual)
  src/pages/            Screens: Login, Dashboard, Users, Tenants, Leases,
                        Maintenance, Invoices, Operations, Tenant screens
  src/components/       Sidebar, header bar, data table, forms, protected layout
  src/lib/              API client, auth context, role navigation, shared types
  nginx.conf            Serves the built app and handles client side routes
src/
  gui/                  PyQt6 windows and role based panels (group project)
  database/             Model classes, connection handling, seed data (group project)
tests/                  pytest and pytest-qt tests (group project)
Database_dump/          SQL dump of the 16 table schema with sample data
docs/                   Authentication test evidence from the group project
Dockerfile              API image
frontend/Dockerfile     Multi stage build: Node compiles the app, nginx serves it
docker-compose.yml      Runs API and web app together locally
.github/workflows/      CI pipeline
LOGINS.md               Demo accounts for every role
```

## API surface

| Domain | Endpoints |
|---|---|
| Auth | `POST /login`, `GET /me` |
| Tenants | list, get, create |
| Invoices | list, list for tenant, create, update, mark paid |
| Payments | list, list for tenant, create, update |
| Complaints | list, get, list for tenant, stats, create, update status, delete |
| Enquiries | list, list for tenant, create |
| Locations | list, create |
| Apartments | list, count, update, update status, update rent |
| Leases | list, list for tenant, create, update, update status, terminate |
| Maintenance | list, get, stats, staff, staff availability, list for tenant, list for staff, create, update status, priority, schedule and cost, assign staff, work logs |
| Users | list, count, get, create, update, delete, change password |
| Staff | list, update |

## CI/CD pipeline

GitHub Actions runs on every push and pull request (`.github/workflows/pytest.yml`):

```
push ──> Backend tests ───┐
         (pytest, Qt      ├──> Docker build ──> Render deploys
          offscreen)      │    (API + web        (only after the
push ──> Frontend build ──┘     images)           checks pass)
         (npm ci, eslint,
          tsc + vite build)
```

1. **Backend tests** installs the Qt libraries and runs the full pytest suite.
2. **Frontend build** installs with `npm ci` from the lockfile, lints, then runs the TypeScript compiler and the Vite build. A type error here is the kind of field name mistake that would otherwise show up as a blank column in production.
3. **Docker build** runs only if both jobs pass, and builds the API and frontend images.

Render's "After CI Checks Pass" setting means each service deploys only once these checks succeed.

## Deployment

- **API:** Docker image from the root `Dockerfile` (Python 3.12), served by uvicorn on Render.
- **Frontend:** Docker image from `frontend/Dockerfile`. Node builds the static app, then nginx serves it, so no Node or source code ships in the final image.
- **Database:** MySQL 8.0, hosted on Aiven for the live deployment.
- **Configuration:** the API reads `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT` and `JWT_SECRET_KEY` from the environment. The frontend reads `VITE_API_URL` at build time.

## Tech stack

| Layer | Technology |
|---|---|
| Languages | Python 3.10+, TypeScript |
| Desktop GUI | PyQt6 |
| API | FastAPI, uvicorn, PyJWT |
| Frontend | React, Vite, Tailwind CSS v4, React Router |
| Database | MySQL 8.0 via `mysql-connector-python` |
| Authentication | bcrypt, JWT |
| Containers | Docker (multi stage builds), nginx |
| CI/CD | GitHub Actions, Render |
| Testing | pytest, pytest-qt, tsc, eslint |

## Requirements

- Python 3.10 or higher
- Node.js 22 or higher (frontend)
- MySQL Server 8.0 or higher, local or remote
- Docker (optional)

## Running everything locally with Docker

```bash
docker compose up --build
```

- API: http://localhost:8000 (docs at `/docs`)
- Web app: http://localhost:5173

This needs a `.env` file at the repo root (see below), which `docker-compose.yml` passes to the API container.

## Running the API on its own

Create a `.env` file at the repo root:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=asd_project
DB_PORT=3306
JWT_SECRET_KEY=generate_your_own_with_python_secrets_token_urlsafe
```

Set up the database from the provided dump, or seed it from scratch:

```bash
mysql -u root -p asd_project < Database_dump/asd_projects_dump.sql
# or
python src/database/seed_data.py
```

Then start the API:

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload
```

Interactive docs are at http://127.0.0.1:8000/docs.

## Running the frontend on its own

```bash
cd frontend
npm install
npm run dev
```

It needs a `frontend/.env` with `VITE_API_URL=http://localhost:8000`.

## Running the desktop app

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/gui/login_window.py
```

Use the accounts in [LOGINS.md](LOGINS.md) to sign in as each role.

## Testing

```bash
pytest tests/                    # backend, 270+ tests
cd frontend
npm run lint
npm run build                    # TypeScript compiler, then Vite build
```

All of this runs automatically in CI.

## Known limitations and next steps

- **The API routes have no automated tests of their own.** The pytest suite covers the desktop GUI and the shared model logic that the API calls. Adding FastAPI `TestClient` tests for the routes and role checks is the most useful next step.
- **No automated frontend tests.** CI type checks, lints and builds the frontend, but there is no equivalent of the backend suite for the UI.
- **Role checks are not location scoped.** A Manager can edit tenants, leases and apartments across every location. Scoping by `location_id` is a natural next step.
- **Inconsistent tenant field names.** `GET /tenants` returns both `user_id` and `tenant_id`, and `GET /tenants/{id}` returns only `user_id`. This comes from the original SQL query, and the desktop GUI depends on the existing key, so I did not change it.
- **Some `PATCH` endpoints return a generic 400** both for an ID that does not exist and for an empty update, because the underlying model methods do not tell the two apart. A stricter API would return 404 and 400.
- **`PUT` and `PATCH` are not fully consistent.** The choice follows whether the original method replaces every field or only the ones provided, which differs method by method (noted in code comments).

## Original group project authors

The base PAMS application (GUI, database design and backend) was built by Hasaan Ahmad, Ishaq Modassir Mushtaq, Rayyan Tahir and Royden Dias. The API, frontend, Docker setup and CI/CD pipeline are my individual continuation of it.

## License

MIT. See [LICENSE](LICENSE).
