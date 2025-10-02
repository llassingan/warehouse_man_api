# Warehouse Management API

This is a RESTful API for managing items in a warehouse. It provides endpoints for user authentication, item management, tagging, and adding notes to items. The API is built with FastAPI and leverages a modern, asynchronous Python stack.

## Project Overview

The Warehouse Management API offers a complete solution for tracking warehouse inventory. Key features include:

*   **User Authentication**: Secure user registration, login, and session management using JWT. Includes email verification, password reset, and token revocation.
*   **Role-Based Access Control**: Differentiates between user roles (e.g., `user`, `admin`) to restrict access to certain endpoints.
*   **Item Management**: Full CRUD (Create, Read, Update, Delete) operations for warehouse items.
*   **Tagging System**: Ability to create tags and associate them with items for better organization and searching.
*   **Notes**: Attach notes to items for additional information.
*   **Asynchronous Tasks**: Uses Celery and Redis for background tasks like sending emails for verification and password resets.

## Tech Stack

*   **Backend Framework**: FastAPI
*   **Database**: PostgreSQL
*   **ORM / Data Validation**: SQLModel
*   **Database Migrations**: Alembic
*   **Asynchronous Task Queue**: Celery
*   **Message Broker & Cache**: Redis
*   **Authentication**: JWT with `passlib` for password hashing.
*   **Containerization**: Docker & Docker Compose

## How to Run the Project

You can easily run the entire application stack using Docker and Docker Compose.

### 1. Prerequisites

*   Docker
*   Docker Compose

### 2. Environment Configuration

Create a `.env` file in the root directory of the project. This file will hold all the necessary environment variables. Copy the contents of `.env.example` (if available) or use the template below.

```env
# PostgreSQL Configuration
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=warehouse_db
POSTGRES_PORT=5432

# Database URL for the API
DATABASE_URL=postgresql+asyncpg://your_db_user:your_db_password@db:5432/warehouse_db

# Redis Configuration
REDIS_PORT=6379
REDIS_HOST=redis

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_key_for_jwt
JWT_ALGORITHM=HS256

# Application Domain
DOMAIN=localhost:8000

# Email Configuration (for Celery)
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

**Note**: The `DATABASE_URL` uses the service name `db` as the host, which is the name of the PostgreSQL service in `docker-compose.yaml`.

### 3. Build and Run

Open your terminal in the project's root directory and run the following command:

```bash
docker-compose up --build -d
```

This command will:
1.  Build the Docker images for the API and Celery worker.
2.  Start all the services (`api`, `db`, `redis`, `celery`) in detached mode.
3.  The API service will automatically run database migrations using Alembic before starting the FastAPI server.

The API will be available at `http://localhost:8000`.

## Accessing the API Documentation

Once the application is running, you can access the interactive OpenAPI (Swagger UI) documentation to explore and test the API endpoints.

Navigate to the following URL in your browser:

**http://localhost:8000/api/v1/docs**

