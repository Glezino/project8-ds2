# Project8 DS2

Aplicación fullstack con separación clara de frontend, backend y módulos de machine learning.

## Estructura del proyecto

```
.
├── frontend/          # React (Vite), TypeScript, Tailwind, Shadcn/ui
├── backend/           # Python, FastAPI, Pydantic, SQLAlchemy, Alembic
│   └── ml/            # Polars, Scikit-learn, XGBoost, Optuna
├── openspec/          # Especificaciones y gestión de cambios
└── Makefile           # Comandos de setup, desarrollo y tests
```

## Requisitos previos

- **Python 3.12** (usado por el backend; gestionado por `uv`)
- **uv** ([instalación](https://docs.astral.sh/uv/getting-started/installation/)) — gestor de dependencias y entornos del backend
- **Node.js 18+** y **npm** — tooling del frontend
- **Make** (GNU Make en Linux/macOS; `make` en Windows vía Git Bash o similar)
- **Playwright browsers** — se instalan con `npx playwright install chromium` la primera vez que se vaya a ejecutar `make test`

## Inicio rápido

```bash
# Clonar el repositorio
git clone https://github.com/Glezino/project8-ds2.git
cd project8-ds2

# Instalar dependencias del backend y frontend y crear .env si no existe
make setup

# Iniciar el desarrollo (backend en :8000, frontend en :5173)
make start
```

`make setup` ejecuta `uv sync` en `backend/`, `npm install` en `frontend/` y crea `.env` a partir de `.env.example` si aún no existe.

## Variables de entorno (.env)

El archivo `.env` en la raíz del repositorio es la única fuente de configuración para ambos stacks. Copia `.env.example` a `.env` y completa los valores:

- **Backend** (leído por `backend/app/config.py` vía `pydantic-settings`): `DATABASE_URL`, `API_HOST`, `API_PORT`, `DEBUG`
- **Frontend** (leído por `frontend/src/api/client.ts` vía `import.meta.env`): `VITE_API_URL`
- **PostgreSQL local** (docker-compose): `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

`.env` está ignorado por version control y nunca debe commitearse.

## Comandos disponibles

```bash
make help          # Ver todos los comandos disponibles
make setup         # Instalar dependencias y configurar el entorno
make start         # Levantar backend (uvicorn) y frontend (vite)
make stop          # Detener backend y frontend
make test          # Ejecutar backend (pytest) y frontend (Playwright)
make lint          # Ejecutar ruff, ESLint y Prettier check
make clean         # Eliminar .venv, node_modules y cachés
```

| Target   | Descripción |
|----------|-------------|
| `help`   | Muestra todos los comandos disponibles |
| `setup`  | Instala dependencias (uv sync + npm install) y crea `.env` si falta |
| `start`  | Levanta los dev servers (uvicorn en :8000, vite en :5173) |
| `stop`   | Detiene ambos dev servers |
| `test`   | Ejecuta `pytest` (backend) y Playwright (frontend) |
| `lint`   | Ejecuta `ruff check`, `ruff format --check`, `eslint`, `prettier --check` |
| `clean`  | Elimina `.venv`, `node_modules`, `dist` y cachés |

## Stack tecnológico

| Capa | Tecnologías |
|------|-------------|
| Frontend | React, Vite, TypeScript, Tailwind, Shadcn/ui, Axios, React Router DOM |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy, Alembic |
| ML | Polars, Scikit-learn, XGBoost, Optuna, Seaborn, Matplotlib |
| Base de datos | Supabase (Postgres) en producción, PostgreSQL en Docker para desarrollo |
| Infraestructura | Docker, Docker Compose |

## Contribuir

Los cambios se gestionan a través de ramas `feature/DS-XX-<slug>` que se mergean en `dev`. Cuando `dev` está estable, se crea un PR hacia `main`.

Ver `openspec/` para la documentación de especificaciones y el flujo de trabajo de desarrollo.