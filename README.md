# Progress Management Tool

A small full-stack project progress management tool built with FastAPI, SQLite, Vue 3, Vite, and Tailwind CSS.

## Features

- User registration and login with JWT authentication
- Project, issue, milestone, category, comment, and wiki management
- Project member and join-request workflows
- Dashboard and multi-project Gantt views
- File upload support

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: Vue 3, Pinia, Vue Router, Vite, Tailwind CSS
- Local runtime: Docker Compose

## Quick Start

1. Copy the environment template.

```bash
cp .env.example .env
```

2. Edit `.env` and replace `SECRET_KEY` and `DEFAULT_ADMIN_PASSWORD`.

3. Start the app.

```bash
docker compose up --build
```

4. Open the frontend.

```text
http://localhost:8080
```

The backend API runs on `http://localhost:8000`.

## Local Development Without Docker

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Configuration

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL. Defaults to SQLite. |
| `SECRET_KEY` | JWT signing secret. Replace before deployment. |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins. |
| `DEFAULT_ADMIN_EMAIL` | Initial administrator email. |
| `DEFAULT_ADMIN_USERNAME` | Initial administrator username. |
| `DEFAULT_ADMIN_NAME` | Initial administrator display name. |
| `DEFAULT_ADMIN_PASSWORD` | Initial administrator password. Replace before deployment. |
| `CREATE_DEMO_DATA` | Set to `false` to skip demo project creation. |
| `VITE_API_URL` | Optional frontend API base URL. Leave empty when using the Vite proxy. |

Demo data is only inserted when the initial administrator has no projects. Existing project data is not deleted on startup.

## Public Repository Notes

This repository intentionally excludes local databases, uploaded files, virtual environments, `node_modules`, local network setup notes, screenshots, and machine-specific launch scripts.

## Security

Do not use the example credentials in production. Set a strong `SECRET_KEY`, change `DEFAULT_ADMIN_PASSWORD`, and restrict `CORS_ORIGINS` before deploying the app.
