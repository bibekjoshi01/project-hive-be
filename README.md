# Project Hive Backend

Backend service for the **College Project Archive Platform**, responsible for storing and managing project archives of students. This API handles project data, categorization, file storage, search functionality, and user/admin operations.

---

## Prerequisites

- **Python**: 3.10+ (if running locally)
- **Docker** (optional, if running with Docker)
- `.env` file with required environment variables (see `.env.example`)

---

## Running Locally (Without Docker)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/bibekjoshi01/project-hive-be
   cd project-hive-be

2. **Create & Activate a Virtual Environment**
   - **Windows**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt

3. **Set Up Environment Variables**
   - Copy .env.example to .env
   - Fill in the required variables

4. **Start the FastAPI Server**
   ```bash
   uvicorn main:app --reload
   ```
   - The API will be available at: http://localhost:8000

---

## Running with Docker

1. **Clone the Repository**
   ```bash
   git clone https://github.com/bibekjoshi01/project-hive-be
   cd project-hive-be

2. **Set Up Environment Variables**
   - Copy .env.example to .env
   - Fill in the required variables

3. **Build and Run with docker**
   ```bash
   docker compose up --build

3. **Stop the container**
   ```bash
   docker ps   # find container ID
   docker stop <container_id>

---

## Code Formatting & Linting

1. **Install pre-commit hooks**
   ```bash
   pre-commit install

2. **Format and Lint**
   ```bash
   ruff check
   ruff check --fix
   ruff format
   black .
   pre-commit run --all-files

3. **Running Tests**
   ```bash
   pytest -v -s```


---

## Database Migrations

1. **Create a new migration:**
   ```bash
   alembic revision -m "your message"

2. **Apply migrations:**
   ```bash
   alembic upgrade head
