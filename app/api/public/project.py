from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from psycopg2 import IntegrityError, DataError

# Project Imports
from app.dependencies import get_current_user
from app.utils.db import parse_ordering
from app.database import execute_query, perform_query
from .schemas.project import (
    BatchYearList,
    BatchYearResponse,
    CategoryList,
    CategoryResponse,
    DepartmentList,
    DepartmentResponse,
    DiscussionIn,
    ProjectList,
    ProjectResponse,
    ProjectRetrieveResponse,
    ResponseOut,
    SubmitProjectPayload,
)


router = APIRouter(prefix="/project-app")


@router.get("/categories", response_model=CategoryList)
async def list_categories(
    search: Optional[str] = Query(None, description="Filter by name icontains"),
    ordering: str = Query("id", description="e.g. id, -name"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    order_sql = parse_ordering(ordering, {"id", "name", "project_count"})

    data_sql = f"""
        WITH c AS (
            SELECT
                cat.id,
                cat.name,
                COUNT(*) FILTER (WHERE proj.is_active) AS project_count
            FROM category AS cat
            LEFT JOIN project AS proj
                   ON proj.category_id = cat.id
            GROUP BY cat.id
        )
        SELECT *,
               COUNT(*) OVER() AS total
        FROM c
        WHERE (%s IS NULL OR name ILIKE '%%' || %s || '%%')            
        ORDER BY {order_sql}
        LIMIT %s OFFSET %s;
    """
    rows = perform_query(data_sql, (search, search, limit, offset))

    results: List[CategoryResponse] = [CategoryResponse(**row) for row in rows]

    return {"count": rows[0]["total"] if rows else 0, "results": results}


@router.get("/categories/{cat_id}", response_model=CategoryResponse)
async def get_category(
    cat_id: int = Path(..., gt=0, description="Numeric primary key of category"),
):
    rows = perform_query("SELECT id, name FROM category WHERE id = %s;", (cat_id,))

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return rows[0]


@router.get("/departments", response_model=DepartmentList)
async def list_departments(
    search: Optional[str] = Query(None, description="Filter by name icontains"),
    ordering: str = Query("id", description="e.g. id, -name"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    order_sql = parse_ordering(ordering, {"id", "name"})

    data_sql = f"""
        SELECT id, name, COUNT(*) OVER() AS total
        FROM department
        WHERE (%s IS NULL OR name ILIKE '%%' || %s || '%%') AND is_active
        ORDER BY {order_sql}
        LIMIT %s OFFSET %s;
    """
    rows = perform_query(data_sql, (search, search, limit, offset))

    results: List[DepartmentResponse] = [DepartmentResponse(**row) for row in rows]

    return {"count": rows[0]["total"] if rows else 0, "results": results}


@router.get("/departments/{dept_id}", response_model=DepartmentResponse)
async def get_department(
    dept_id: int = Path(..., gt=0, description="Numeric primary key of department"),
):
    rows = perform_query("SELECT id, name FROM department WHERE id = %s;", (dept_id,))

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    return rows[0]


@router.get("/batch-years", response_model=BatchYearList)
async def list_batch_years(
    ordering: str = Query("id", description="e.g. id, -year"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    order_sql = parse_ordering(ordering, {"id", "year"})

    data_sql = f"""
        SELECT id, year, COUNT(*) OVER() AS total
        FROM batch_year
        WHERE is_active
        ORDER BY {order_sql}
        LIMIT %s OFFSET %s;
    """
    rows = perform_query(data_sql, (limit, offset))

    results: List[BatchYearResponse] = [BatchYearResponse(**row) for row in rows]

    return {"count": rows[0]["total"] if rows else 0, "results": results}


@router.get("/batch-years/{batch_id}", response_model=BatchYearResponse)
async def get_batch_year(
    batch_id: int = Path(..., gt=0, description="Numeric primary key of batch year id"),
):
    rows = perform_query("SELECT id, year FROM batch_year WHERE id = %s;", (batch_id,))

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batch Year not found"
        )

    return rows[0]


@router.get("/projects", response_model=ProjectList)
async def list_projects(
    search: Optional[str] = Query(None, description="Search project title ILIKE"),
    category_id: Optional[int] = Query(None, gt=0),
    department_id: Optional[int] = Query(None, gt=0),
    batch_year_id: Optional[int] = Query(None, gt=0),
    level: Optional[str] = Query(None),
    ordering: str = Query(
        "id", description="Prefix with '-' for DESC. e.g. -submitted_at, rating"
    ),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    order_sql = parse_ordering(
        ordering,
        {
            "id": "p.id",
            "title": "p.title",
            "submitted_at": "p.submitted_at",
            "avg_rating": "avg_rating",
        },
    )

    sql = f"""
        WITH filtered AS (
            SELECT
                p.*,
                c.id AS category_id,
                c.name AS category_name,
                d.id AS department_id,
                d.name AS department_name,
                b.id AS batch_year_id,
                b.year AS batch_year_year,
                u.first_name || ' ' || u.last_name AS submitted_by_full_name,
                COALESCE(AVG(pr.rating)::numeric(3,2), 5.0) AS avg_rating,
                COUNT(*) OVER() AS total_count
            FROM project AS p
            LEFT JOIN project_rating AS pr ON pr.project_id = p.id
            JOIN category AS c ON p.category_id = c.id
            JOIN department AS d ON p.department_id = d.id
            JOIN batch_year AS b ON p.batch_year_id = b.id
            JOIN "user" AS u ON p.submitted_by = u.id
            WHERE p.is_active AND p.status = 'APPROVED'
            AND (%s IS NULL OR p.title ILIKE '%%' || %s || '%%')
            AND (%s IS NULL OR p.category_id   = %s)
            AND (%s IS NULL OR p.level   = %s)
            AND (%s IS NULL OR p.department_id = %s)
            AND (%s IS NULL OR p.batch_year_id = %s)
            GROUP BY p.id, c.id, d.id, b.id, u.id
        )
        SELECT * FROM filtered
        ORDER BY {order_sql}
        LIMIT %s OFFSET %s;
    """

    params = (
        search,
        search,
        category_id,
        category_id,
        level,
        level,
        department_id,
        department_id,
        batch_year_id,
        batch_year_id,
        limit,
        offset,
    )

    rows = perform_query(sql, params)

    results: List[ProjectResponse] = []
    for r in rows:
        data = dict(r)
        data["submitted_at"] = r["submitted_at"].isoformat()
        data["rating_average"] = float(r["avg_rating"])

        data["category"] = {"id": r["category_id"], "name": r["category_name"]}
        data["department"] = {"id": r["department_id"], "name": r["department_name"]}
        data["batch_year"] = {"id": r["batch_year_id"], "year": r["batch_year_year"]}

        # Remove individual FK fields
        for fk in [
            "category_id",
            "category_name",
            "department_id",
            "department_name",
            "batch_year_id",
            "batch_year_year",
            "avg_rating",
        ]:
            data.pop(fk, None)

        results.append(ProjectResponse(**data))

    return {"count": rows[0]["total_count"] if rows else 0, "results": results}


@router.get("/projects/{project_id}", response_model=ProjectRetrieveResponse)
async def get_project(
    project_id: int = Path(..., gt=0, description="Numeric primary key of project id"),
):
    sql = """
        WITH filtered AS (
            SELECT
                p.id,
                p.title,
                p.abstract,
                p.level,
                p.supervisor,
                p.technologies_used,
                p.github_link,
                p.documentation_link,
                p.project_details,
                p.status,
                p.submitted_at,
                u.first_name || ' ' || u.last_name AS submitted_by_full_name,
                c.id AS category_id,
                c.name AS category_name,
                d.id AS department_id,
                d.name AS department_name,
                b.id AS batch_year_id,
                b.year AS batch_year_year,
                COALESCE(AVG(pr.rating)::numeric(3,2), 5.0) AS avg_rating
            FROM project AS p
            LEFT JOIN project_rating AS pr ON pr.project_id = p.id
            JOIN category AS c ON p.category_id = c.id
            JOIN department AS d ON p.department_id = d.id
            JOIN batch_year AS b ON p.batch_year_id = b.id
            JOIN "user" AS u ON p.submitted_by = u.id
            WHERE p.is_active AND p.status = 'APPROVED' AND p.id = %s
            GROUP BY p.id, c.id, d.id, b.id, u.id
        )
        SELECT * FROM filtered;
    """

    project_rows = perform_query(sql, (project_id,))
    if not project_rows:
        raise HTTPException(status_code=404, detail="Project not found")

    project_row = project_rows[0]

    team_sql = "SELECT id, full_name, roll_no, photo FROM project_team_member WHERE project_id = %s;"
    files_sql = "SELECT id, file_type, file FROM project_files WHERE project_id = %s;"

    team_members = perform_query(team_sql, (project_id,))
    files = perform_query(files_sql, (project_id,))

    # Convert comma-separated strings into arrays
    technologies = (
        [tech.strip() for tech in project_row["technologies_used"].split(",")]
        if project_row["technologies_used"]
        else []
    )
    github_links = (
        [link.strip() for link in project_row["github_link"].split(",")]
        if project_row["github_link"]
        else []
    )

    data = {
        "id": project_row["id"],
        "title": project_row["title"],
        "abstract": project_row["abstract"],
        "level": project_row["level"],
        "supervisor": project_row["supervisor"],
        "technologies_used": technologies,
        "github_links": github_links,
        "documentation_link": project_row["documentation_link"],
        "project_details": project_row["project_details"],
        "status": project_row["status"],
        "submitted_at": (
            project_row["submitted_at"].isoformat()
            if hasattr(project_row["submitted_at"], "isoformat")
            else project_row["submitted_at"]
        ),
        "submitted_by_full_name": project_row["submitted_by_full_name"],
        "category": {
            "id": project_row["category_id"],
            "name": project_row["category_name"],
        },
        "department": {
            "id": project_row["department_id"],
            "name": project_row["department_name"],
        },
        "batch_year": {
            "id": project_row["batch_year_id"],
            "year": project_row["batch_year_year"],
        },
        "rating_average": float(project_row["avg_rating"]),
        # "views": project_row["views"],
        "team_members": [
            {
                "id": t["id"],
                "full_name": t["full_name"],
                "roll_no": t["roll_no"],
                "photo": t["photo"],
            }
            for t in team_members
        ],
        "files": [
            {"id": f["id"], "file_type": f["file_type"], "file": f["file"]}
            for f in files
        ],
    }

    return data


@router.post("/submit-project", response_model=ResponseOut, status_code=201)
async def submit_project(payload: SubmitProjectPayload, user=Depends(get_current_user)):
    try:
        execute_query(
            """
            INSERT INTO project (
                title, abstract, batch_year_id, category_id, 
                department_id, level, supervisor, project_details, 
                technologies_used, github_link, documentation_link, 
                submitted_by, submitted_at, approved_by
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
            """,
            (
                payload.title,
                payload.abstract,
                payload.batch_year,
                payload.category,
                payload.department,
                payload.level.value,
                payload.supervisor or "Not Assigned",
                payload.project_details,
                payload.technologies_used,
                str(payload.github_link),
                str(payload.documentation_link),
                user["id"],
                user["id"],
            ),
        )
    except IntegrityError as e:
        # Handle foreign key violation
        raise HTTPException(
            status_code=400,
            detail="Invalid foreign key: Please check batch_year, category, or department.",
        )
    except DataError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {e.pgerror}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while submitting the project.",
        )

    return ResponseOut(message="Project submitted successfully")


@router.patch(
    "/projects/{project_id}/rate", response_model=ResponseOut, status_code=201
)
def rate_project(
    project_id: int,
    rating: int,
    user=Depends(get_current_user),
):
    try:
        execute_query(
            """
            INSERT INTO project_rating (project_id, user_id, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (project_id, user_id)
            DO UPDATE SET rating = EXCLUDED.rating, updated_at = now();
            """,
            (project_id, user["id"], rating),
        )

        return {"message": "Thank you for your feedback."}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while submitting the project.",
        )


@router.post("/{project_id}/comments", response_model=ResponseOut, status_code=201)
def add_comment(
    project_id: int,
    payload: DiscussionIn,
    user=Depends(get_current_user),
):
    """
    Add a root comment or reply (`parent_id` optional).
    """
    # Validate parent belongs to same project (if provided)
    if payload.parent_id is not None:
        parent = perform_query(
            "SELECT project_id FROM project_discussion WHERE id = %s;",
            (payload.parent_id,),
        )
        if not parent:
            raise HTTPException(404, "Parent comment not found")
        if parent[0]["project_id"] != project_id:
            raise HTTPException(400, "Parent comment belongs to another project")

    return {"message": "Commented Successfully."}
