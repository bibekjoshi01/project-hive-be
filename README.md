# PROJECT HIVE BACKEND

To store the project archives of students.
---

## Prerequisites

1. Python 3.10+ installed (if running locally)
2. Docker installed (if running with Docker)
3. `.env` file with required environment variables set (see `.env.example`)

---

## Running Locally (Without Docker)

1. Clone the repo

   ```bash
   git clone https://github.com/bibekjoshi01/project-hive-be
   cd project-hive-be

2. Create and activate a virtual environment

    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate
   ```

    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
   ```

  3. Install Dependencies

     ```bash
     pip install -r requirements.txt

  4. Setup *.env* file (create from .env.example and fill in required variables)

  6. Start the FastAPI Server

     ```bash
     uvicorn main:app --reload

  **The app will be available at http://localhost:8000**

---

## Running with Docker

1. Clone the repo

   ```bash
   git clone https://github.com/bibekjoshi01/project-hive-be
   cd project-hive-be

2. Create a *.env* file in the project root with required variables (see .env.example).

4. Build and Run the docker image

   ```bash
   docker compose up --build


**The app will be available at http://localhost:8000**

**Note:** To stop the Docker container, use docker ps to find the container ID and then docker stop <container_id>

---

## Formatting and Linting Code

   ```pre-commit install```

1. ruff check / ruff check --fix / ruff format
2. black .
3. pre-commit run --all-files


## Migrations

    MAKE MIGRATIONS: alembic revision -m "message"
    MIGRATE: alembic upgrade head

## Running Tests

   ```bash
   pytest -v -s