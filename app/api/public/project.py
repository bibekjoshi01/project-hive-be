from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status, Path

# Project Imports
from app.utils.db import parse_ordering
from app.database import perform_query
from .schemas.project import (
    BatchYearList,
    BatchYearResponse,
    CategoryList,
    CategoryResponse,
    DepartmentList,
    DepartmentResponse,
)


router = APIRouter(prefix="/project-app")


@router.get("/categories", response_model=CategoryList)
async def list_categories(
    search: Optional[str] = Query(None, description="Filter by name icontains"),
    ordering: str = Query("id", description="e.g. id, -name"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    order_sql = parse_ordering(ordering, {"id", "name"})

    data_sql = f"""
        SELECT id, name, COUNT(*) OVER() AS total
        FROM category
        WHERE (%s IS NULL OR name ILIKE '%%' || %s || '%%') AND is_active
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
