from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path

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
    ResponseOut,
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
            "rating": "avg_rating",
        },
    )

    sql = f"""
        WITH filtered AS (
            SELECT
                p.*,
                COALESCE(AVG(pr.rating)::numeric(3,2), 0) AS avg_rating,
                COUNT(*) OVER() AS total_count
            FROM project AS p
            LEFT JOIN project_rating AS pr ON pr.project_id = p.id
            WHERE p.is_active
              AND (%s IS NULL OR p.title ILIKE '%%' || %s || '%%')
              AND (%s IS NULL OR p.category_id   = %s)
              AND (%s IS NULL OR p.department_id = %s)
              AND (%s IS NULL OR p.batch_year_id = %s)
            GROUP BY p.id
        )
        SELECT *
        FROM filtered
        ORDER BY {order_sql}
        LIMIT %s OFFSET %s;
    """

    params = (
        search,
        search,
        category_id,
        category_id,
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
        results.append(ProjectResponse(**data))

    return {"count": rows[0]["total_count"] if rows else 0, "results": results}


@router.patch(
    "/projects/{project_id}/rate", response_model=ResponseOut, status_code=201
)
def rate_project(
    project_id: int,
    rating: int,
    user=Depends(get_current_user),
):
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
