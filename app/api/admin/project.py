from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional, List
from fastapi import Query, Path
import urllib.parse

from app.database import execute_query, perform_query
from app.dependencies import get_current_admin_user

from .schemas.project import (
    ProjectApprovalPayload,
    ProjectList,
    ProjectResponse,
    ProjectRetrieveResponse,
)

router = APIRouter(prefix="/project-app")


@router.get("/projects", response_model=ProjectList)
async def list_projects(
    search: Optional[str] = Query(None, description="Search project title ILIKE"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin_user),
):
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
            WHERE p.is_active
            AND (%s IS NULL OR p.title ILIKE '%%' || %s || '%%')
            GROUP BY p.id, c.id, d.id, b.id, u.id
        )
        SELECT * FROM filtered
        ORDER BY submitted_at DESC
        LIMIT %s OFFSET %s;
    """

    params = (search, search, limit, offset)

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


@router.get("/projects/{project_slug}", response_model=ProjectRetrieveResponse)
async def get_project(
    project_slug: str = Path(..., description="project slug unique"),
):
    sql = """
    WITH rating_stats AS (
        SELECT
            project_id,
            COUNT(*) AS total_ratings,
            COALESCE(AVG(rating)::numeric(3,2), 5.0) AS avg_rating
        FROM project_rating
        GROUP BY project_id
    ), filtered AS (
        SELECT
            p.id,
            p.title,
            p.abstract,
            p.level,
            p.views,
            p.slug,
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
            COALESCE(rs.total_ratings, 0) AS total_ratings,
            COALESCE(rs.avg_rating, 5.0) AS avg_rating
        FROM project AS p
        LEFT JOIN rating_stats AS rs ON rs.project_id = p.id
        JOIN category AS c ON p.category_id = c.id
        JOIN department AS d ON p.department_id = d.id
        JOIN batch_year AS b ON p.batch_year_id = b.id
        JOIN "user" AS u ON p.submitted_by = u.id
        WHERE p.is_active AND p.status = 'APPROVED' AND p.slug = %s
    )
    SELECT * FROM filtered;

    """

    project_rows = perform_query(sql, (project_slug,))
    if not project_rows:
        raise HTTPException(status_code=404, detail="Project not found")

    project_row = project_rows[0]

    team_sql = "SELECT id, full_name, roll_no, photo FROM project_team_member WHERE project_id = %s;"
    files_sql = "SELECT id, file_type, file FROM project_files WHERE project_id = %s;"

    team_members = perform_query(team_sql, (project_row["id"],))
    files = perform_query(files_sql, (project_row["id"],))

    # Convert comma-separated strings into arrays
    technologies = (
        [tech.strip() for tech in project_row["technologies_used"].split(",")]
        if project_row["technologies_used"]
        else []
    )
    github_links = (
        [
            urllib.parse.unquote(link.strip())
            for link in project_row["github_link"].split(",")
        ]
        if project_row["github_link"]
        else []
    )

    data = {
        "id": project_row["id"],
        "slug": project_row["slug"],
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
        "views": project_row["views"],
        "total_ratings": project_row["total_ratings"],
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


@router.post("/review-project", status_code=200)
async def review_project(request: Request, payload: ProjectApprovalPayload):
    try:
        sql = """
            UPDATE project
            SET status = %s, updated_at = NOW()
            WHERE id = %s;
        """
        execute_query(sql, (payload.status.value, payload.project_id))
    except Exception:
        raise HTTPException("Failed to update the status")

    return {
        "message": f"Project {payload.project_id} has been marked as {payload.status.value}."
    }
