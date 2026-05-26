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
- Local runtime: Python and Node.js, no Docker required

## Quick Start

Run the backend and frontend in two separate terminals.

Backend:

```powershell
.\scripts\start-backend.ps1
```

Frontend:

```powershell
.\scripts\start-frontend.ps1
```

Open the frontend:

```text
http://localhost:5173
```

The backend API runs on:

```text
http://127.0.0.1:8000
```

## Manual Setup

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Default Login

The first run creates a local administrator account.

```text
Email: admin@example.com
Password: changeme-admin-password
```

Change the password after logging in, or set `DEFAULT_ADMIN_PASSWORD` before starting the backend.

## Configuration

You can create a local `.env` file from `.env.example`, or set environment variables directly before starting the backend.

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL. Defaults to local SQLite. |
| `SECRET_KEY` | JWT signing secret. A temporary key is generated for local development when omitted. |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins. |
| `UPLOAD_DIR` | File upload directory. Defaults to `./data/uploads`. |
| `DEFAULT_ADMIN_EMAIL` | Initial administrator email. |
| `DEFAULT_ADMIN_USERNAME` | Initial administrator username. |
| `DEFAULT_ADMIN_NAME` | Initial administrator display name. |
| `DEFAULT_ADMIN_PASSWORD` | Initial administrator password. |
| `CREATE_DEMO_DATA` | Set to `false` to skip demo project creation. |
| `VITE_API_URL` | Optional frontend API base URL. Leave empty when using the Vite proxy. |

Demo data is only inserted when the initial administrator has no projects. Existing project data is not deleted on startup.

## Public Repository Notes

This repository intentionally excludes local databases, uploaded files, virtual environments, `node_modules`, local network setup notes, screenshots, machine-specific launch scripts, and Docker-specific files.

## Security

Do not use the default credentials in production. Set a strong `SECRET_KEY`, change `DEFAULT_ADMIN_PASSWORD`, and restrict `CORS_ORIGINS` before deploying the app.
