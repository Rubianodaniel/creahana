# Task Manager API

A complete REST and GraphQL API for task and task list management, built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **Strawberry GraphQL**.

## Features

### Core Functionality
- **Complete CRUD** for task lists and tasks
- **Task status management** (pending, in_progress, completed)
- **Advanced filtering** by status and priority
- **Automatic completion percentage** in task lists
- **JWT Authentication** with registration and login
- **User assignment** to tasks
- **Email notification simulation**

### Available APIs
- **REST API** - Traditional endpoints with FastAPI
- **GraphQL API** - queries with Strawberry GraphQL

## Architecture

**Clean Architecture** implementation by layers:

```
src/
├── domain/           # Entities and business rules
├── application/      # Use cases and services
├── infrastructure/   # Database, repositories, configuration
└── presentation/     # REST controllers and GraphQL resolvers
```

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy (async)
- **GraphQL**: Strawberry GraphQL
- **Authentication**: JWT with python-jose
- **Testing**: pytest + pytest-asyncio + pytest-cov
- **Linting**: flake8, black, isort
- **Containerization**: Docker + docker-compose

## 🚦 Prerequisites

- Python 3.11+
- Docker and docker-compose
- Git

## Quick Start

### 1. Clone the repository
```bash
git clone <https://github.com/Rubianodaniel/creahana.git>
cd crehana
```

### 2. Set up local environment

#### Option A: With Docker (Recommended)
```bash
# Start the entire application
docker-compose up -d

# View logs
docker-compose logs -f app
```

#### Option B: Local development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start only the database
docker-compose up -d postgres postgres_test

# Apply migrations
alembic upgrade head

# Run application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the application

- **REST API**: http://localhost:8000/docs (Swagger UI)
- **GraphQL**: http://localhost:8000/graphql (GraphiQL interface)


## Usage Examples

### Complete REST API Workflow
Here's a step-by-step example showing the complete authentication and task management flow:

#### Step 1: Register a new user
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```
**Response:**
```json
{
  "id": 1,
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Step 2: Login to get JWT token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Step 3: Create a task list (using the Bearer token)
```bash
curl -X POST "http://localhost:8000/task-lists" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "title": "My Project Tasks",
    "description": "Tasks for the new project"
  }'
```
**Response:**
```json
{
  "id": 1,
  "title": "My Project Tasks",
  "description": "Tasks for the new project",
  "user_id": 1,
  "is_active": true,
  "created_at": "2024-01-15T10:35:00Z"
}
```

#### Step 4: Create tasks in the list
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "title": "Setup database",
    "description": "Configure PostgreSQL database",
    "task_list_id": 1,
    "priority": "high",
    "assigned_user_id": 1
  }'
```

#### Step 5: Get task list with completion percentage
```bash
curl -X GET "http://localhost:8000/task-lists/1/tasks" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```
**Response:**
```json
{
  "id": 1,
  "title": "My Project Tasks",
  "completion_percentage": 0.0,
  "total_tasks": 1,
  "completed_tasks": 0,
  "tasks": [
    {
      "id": 1,
      "title": "Setup database",
      "status": "pending",
      "priority": "high",
      "assigned_user_id": 1
    }
  ]
}
```

### Complete GraphQL Workflow

#### Step 1: Get authentication token via REST API
```bash
# Register user (REST only)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "securepass123"}'

# Login to get JWT token (REST only)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "securepass123"}'
```

#### Step 2: Use token in GraphQL queries and mutations
```graphql
# Headers: { "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }

query {
  getTaskListWithTasks(id: 1) {
    id
    title
    completion_percentage
    total_tasks
    completed_tasks
    tasks {
      id
      title
      status
      priority
      assigned_user_id
    }
  }
}
```

#### Step 3: Create task via GraphQL mutation
```graphql
# Headers: { "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }

mutation {
  createTask(input: {
    title: "Write API documentation"
    description: "Complete API documentation for the project"
    task_list_id: 1
    priority: MEDIUM
    assigned_user_id: 1
  }) {
    id
    title
    status
    priority
  }
}
```


## Testing

### Run all tests
```bash
pytest
```

### Unit tests only
```bash
pytest tests/unit/
```

### Integration tests only
```bash
pytest tests/integration/
```

### With coverage report
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

**Current coverage**:

## Development

### Linting and formatting
```bash
# Format code
black src/ tests/
isort src/ tests/

# Check style
flake8 src/

# Run full quality pipeline
make quality  # if Makefile exists
```

### Database migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# View history
alembic history
```

## Project Metrics

- **Tests**: 134 tests (100% passing)
- **Coverage**: 83%
- **Architecture**: Clean Architecture
- **APIs**: REST + GraphQL
- **Authentication**: JWT implemented
- **Docker**: Multi-stage build ready

## Security

- JWT Authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS protection configured
- Environment variables for secrets

## Project Structure

```
├── src/
│   ├── application/          # Use cases and services
│   ├── domain/              # Entities, exceptions, repositories
│   ├── infrastructure/      # Database, mappers, configuration
│   └── presentation/        # REST controllers and GraphQL resolvers
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── alembic/                # Database migrations
├── docker-compose.yml      # Service orchestration
├── Dockerfile             # Application image
├── pytest.ini            # Pytest configuration
├── .flake8               # Linting configuration
└── requirements.txt      # Python dependencies
```

## Docker

### Manual build
```bash
# Build image
docker build -t task-manager-api .

# Run container
docker run -p 8000:8000 --env-file .env task-manager-api
```

### Required environment variables
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
TEST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5433/test_db
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EMAIL_FROM=noreply@company.com
EMAIL_ENABLED=true
```
