# DocuDash Backend - Python/FastAPI

Backend API para DocuDash, migrado de Node.js/Express a Python/FastAPI.

## Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **PostgreSQL** - Base de datos
- **JWT** - Autenticación con tokens
- **Uvicorn** - Servidor ASGI

## Requisitos

- Python 3.10+
- PostgreSQL 12+

## Instalación

1. Crear entorno virtual:

```bash
cd backend_python
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:

Copiar `.env.example` a `.env` y configurar las variables:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/docu_dash

# JWT
JWT_SECRET=tu-secreto-super-seguro

# CORS
CORS_ORIGIN=http://localhost:5173
```

4. Ejecutar migraciones (crear tablas):

Las tablas se crean automáticamente al iniciar la aplicación.

5. Poblar base de datos con datos iniciales:

```bash
python seed.py
```

## Ejecución

### Desarrollo

```bash
uvicorn app.main:app --reload --port 3001
```

### Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3001
```

## API Endpoints

La API estará disponible en `http://localhost:3001/api`

### Documentación

- Swagger UI: `http://localhost:3001/api/docs`
- ReDoc: `http://localhost:3001/api/redoc`

### Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/auth/login | Login |
| POST | /api/auth/register | Registro |
| GET | /api/auth/me | Usuario actual |
| GET | /api/users | Listar usuarios (admin) |
| GET | /api/groups | Listar agrupadores |
| GET | /api/applications | Listar aplicaciones |
| GET | /api/features | Listar features |
| GET | /api/test-cases | Listar casos de prueba |
| GET | /api/test-requests | Listar solicitudes |
| GET | /api/pipelines | Listar pipelines |
| GET | /api/dashboard/stats | Estadísticas |

## Usuarios por defecto

Después de ejecutar `seed.py`:

- **Admin:** admin@docudash.com / admin123
- **Usuario:** usuario@docudash.com / user123

## Estructura del proyecto

```
backend_python/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión a BD
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── application.py
│   │   ├── feature.py
│   │   ├── test_case.py
│   │   ├── pipeline.py
│   │   ├── test_request.py
│   │   └── integration.py
│   ├── schemas/             # Esquemas Pydantic
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── application.py
│   │   ├── feature.py
│   │   ├── test_case.py
│   │   ├── pipeline.py
│   │   └── test_request.py
│   ├── routers/             # Endpoints API
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   ├── applications.py
│   │   ├── features.py
│   │   ├── test_cases.py
│   │   ├── test_requests.py
│   │   ├── pipelines.py
│   │   └── dashboard.py
│   ├── services/            # Servicios
│   │   ├── auth_service.py
│   │   └── notification_service.py
│   ├── middleware/          # Middlewares
│   │   ├── auth.py
│   │   ├── error_handler.py
│   │   └── request_logger.py
│   └── utils/               # Utilidades
│       └── id_generator.py
├── requirements.txt
├── seed.py                  # Script de seed
└── README.md
```

## Diferencias con el backend Node.js

| Característica | Node.js | Python |
|---------------|---------|--------|
| Framework | Express | FastAPI |
| ORM | Prisma | SQLAlchemy |
| Validación | Zod | Pydantic |
| Auth | jsonwebtoken | python-jose |
| Hash passwords | bcryptjs | passlib |

## Notas de migración

- Las rutas mantienen la misma estructura `/api/*`
- Los campos en las respuestas usan camelCase para compatibilidad con el frontend
- La autenticación JWT es compatible con el frontend existente
- Los IDs se generan con formato CUID para compatibilidad

