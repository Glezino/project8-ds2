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

- Docker y Docker Compose
- Python 3.11+
- Node.js 18+
- Make

## Inicio rápido

```bash
# Clonar el repositorio
git clone https://github.com/Glezino/project8-ds2.git
cd project8-ds2

# Configurar el entorno
cp .env.example .env
# Editar .env con tus variables de entorno

# Instalar dependencias y levantar servicios
make setup

# Iniciar el desarrollo
make start
```

## Comandos disponibles

```bash
make help          # Ver todos los comandos disponibles
make setup         # Instalar dependencias y configurar el entorno
make start         # Levantar todos los servicios
make test          # Ejecutar la suite de tests
make lint          # Ejecutar el linter
make stop          # Detener todos los servicios
```

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
