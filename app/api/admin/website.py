from fastapi import APIRouter, Depends
from typing import Optional, List
from fastapi import Query

from app.database import perform_query
from app.dependencies import get_current_admin_user
from .schemas.website import (
    ContactList,
    ContactResponse,
    ContactSummary,
    DashboardSummaryResponse,
    ProjectSummary,
)

router = APIRouter(prefix="/website-app")


@router.get("/contacts", response_model=ContactList)
async def list_contact_requests(
    search: Optional[str] = Query(None, description="Search contact name ILIKE"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin_user),
):
    sql = """
        SELECT
        cm.*,
        c.total_count
        FROM (
        SELECT *
        FROM contact_message
        WHERE (%s IS NULL OR full_name ILIKE '%%' || %s || '%%')
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        ) cm
        CROSS JOIN (
        SELECT COUNT(*) AS total_count
        FROM contact_message
        WHERE (%s IS NULL OR full_name ILIKE '%%' || %s || '%%')
        ) c;
    """

    params = (search, search, limit, offset, search, search)
    rows = perform_query(sql, params)

    results: List[ContactResponse] = []
    total_count = 0
    for r in rows:
        data = dict(r)
        data["created_at"] = r["created_at"].isoformat()
        total_count = r["total_count"]
        results.append(ContactResponse(**data))

    return {"count": total_count, "results": results}


@router.get(
    "/dashboard-summary",
    response_model=DashboardSummaryResponse,
    status_code=200,
)
async def get_dashboard_summary(
    current_user: dict = Depends(get_current_admin_user),
):
    def extract_count(result):
        if isinstance(result, list) and len(result) > 0:
            row = result[0]
            if isinstance(row, dict):
                return list(row.values())[0]
        return 0

    # Queries
    query_contact_total = "SELECT COUNT(*) AS count FROM contact_message;"
    query_contact_new = """
        SELECT COUNT(*) AS count
        FROM contact_message
        WHERE created_at >= date_trunc('week', now());
    """

    query_total_projects = "SELECT COUNT(*) AS count FROM project;"
    query_pending = "SELECT COUNT(*) AS count FROM project WHERE status = 'PENDING';"
    query_accepted = "SELECT COUNT(*) AS count FROM project WHERE status = 'APPROVED';"
    query_rejected = "SELECT COUNT(*) AS count FROM project WHERE status = 'REJECTED';"

    total_contacts = extract_count(perform_query(query_contact_total))
    new_contacts = extract_count(perform_query(query_contact_new))

    total_projects = extract_count(perform_query(query_total_projects))
    pending = extract_count(perform_query(query_pending))
    accepted = extract_count(perform_query(query_accepted))
    rejected = extract_count(perform_query(query_rejected))

    success_rate = (
        round((accepted / total_projects) * 100, 2) if total_projects else 0.0
    )

    return DashboardSummaryResponse(
        contact_requests=ContactSummary(
            total=total_contacts,
            new=new_contacts,
        ),
        projects=ProjectSummary(
            total=total_projects,
            pending=pending,
            accepted=accepted,
            rejected=rejected,
            success_rate=success_rate,
        ),
    )
