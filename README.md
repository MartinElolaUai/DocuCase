# DocuDash - Gestión de Casos de Prueba

Sistema centralizado para la gestión, documentación y trazabilidad de casos de prueba automatizados.

## 🚀 Características

- **Gestión de Casos de Prueba**: Definición estructurada con steps/substeps en Gherkin
- **Organización Jerárquica**: Agrupadores → Aplicaciones → Features → Casos de Prueba
- **Integración Azure DevOps**: Asociación con Historias de Usuario y Test Cases
- **Trazabilidad GitLab**: Resultados de pipelines CI/CD vinculados a casos de prueba
- **Sistema de Solicitudes**: Flujo de trabajo para solicitar nuevos casos de prueba
- **Notificaciones**: Alertas por correo según suscripciones a agrupadores

## 📋 Requisitos Previos

- Python >= 3.10
- Node.js >= 18.0.0
- PostgreSQL >= 14
- npm >= 9.0.0

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd docu-dash
```

2. **Configurar Backend (Python/FastAPI)**
```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Copiar .env.example a .env y editar con tu configuración
```

3. **Configurar Frontend**
```bash
cd frontend
npm install
```

4. **Poblar base de datos con datos iniciales**
```bash
cd backend
python seed.py
```

## 🚀 Ejecución

### Backend (Python)
```bash
cd backend

# Activar entorno virtual (si no está activado)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --port 3001
```

### Frontend (React)
```bash
cd frontend
npm run dev
```

### Acceso
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3001
- **API Docs (Swagger)**: http://localhost:3001/api/docs
- **API Docs (ReDoc)**: http://localhost:3001/api/redoc

## 📁 Estructura del Proyecto

```
docu-dash/
├── backend/                 # API REST con Python/FastAPI
│   ├── app/
│   │   ├── main.py          # Punto de entrada
│   │   ├── config.py        # Configuración
│   │   ├── database.py      # Conexión a BD
│   │   ├── models/          # Modelos SQLAlchemy
│   │   ├── schemas/         # Esquemas Pydantic
│   │   ├── routers/         # Endpoints API
│   │   ├── services/        # Servicios
│   │   ├── middleware/      # Middlewares
│   │   └── utils/           # Utilidades
│   ├── requirements.txt
│   ├── seed.py              # Datos iniciales
│   └── README.md
├── frontend/                # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/           # Páginas de la aplicación
│   │   ├── services/        # Servicios API
│   │   ├── store/           # Estado global
│   │   └── types/           # Tipos TypeScript
│   └── package.json
└── README.md
```

## 🔧 Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **PostgreSQL** - Base de datos
- **JWT** - Autenticación con tokens

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool
- **TailwindCSS** - Estilos
- **Zustand** - Estado global

## 👥 Roles

- **Usuario**: Consulta, solicita casos de prueba, suscripciones
- **Administrador**: Gestión completa de todas las entidades

## 👤 Usuarios por defecto

Después de ejecutar `seed.py`:

| Usuario | Email | Contraseña | Rol |
|---------|-------|------------|-----|
| Admin | admin@docudash.com | admin123 | ADMIN |
| Usuario | usuario@docudash.com | user123 | USER |

## 🔗 Integraciones

- **Azure DevOps**: Historias de Usuario y Test Cases
- **GitLab CI/CD**: Pipelines y resultados de ejecución
- **SMTP**: Notificaciones por correo electrónico

## 📝 Licencia

Proyecto interno - Todos los derechos reservados.
