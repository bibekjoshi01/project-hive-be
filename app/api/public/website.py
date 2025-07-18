from typing import List, Optional
from fastapi import APIRouter, Query, Request, status

from app.api.public.schemas.project import CategoryList, CategoryResponse
from app.utils.db import parse_ordering

from .schemas.website import ContactPayload, NewsletterSubscribePayload, StatsOut
from app.database import execute_query, perform_query
from app.utils.throttling import limiter


router = APIRouter(prefix="/website-app")

CONTACT_LIMIT = "5/minute"  # allow 5 messages per IP per minute


@router.post("/subscribe-newsletter", status_code=status.HTTP_201_CREATED)
@limiter.limit(CONTACT_LIMIT)
async def subscribe_newsletter(request: Request, payload: NewsletterSubscribePayload):
    sql = """
        INSERT INTO newsletter_subscriber (email)
        VALUES (%s)
        ON CONFLICT (email) DO NOTHING;
    """
    execute_query(sql, (payload.email,))
    return {
        "message": "Thank you for subscribing! You'll receive the latest project updates."
    }


@router.post("/contact", status_code=status.HTTP_201_CREATED)
@limiter.limit(CONTACT_LIMIT)
async def send_contact_request(request: Request, payload: ContactPayload):
    sql = """
        INSERT INTO contact_message (full_name, email, phone_no, subject, message)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        payload.full_name,
        payload.email,
        payload.phone_no,
        payload.subject,
        payload.message,
    )
    execute_query(sql, params)

    return {
        "message": "Thank you for your message! We'll get back to you soon.",
    }


@router.get("/stats", response_model=StatsOut)
def get_stats():
    """
    Return simple aggregate counts used for dashboard cards.
    """
    row = perform_query(
        """
        SELECT
            (SELECT COUNT(*) FROM department WHERE is_active) AS departments,
            (SELECT COUNT(*) FROM category WHERE is_active) AS categories,
            (SELECT COUNT(*) FROM batch_year WHERE is_active) AS batches,
            (SELECT COUNT(*) FROM project WHERE is_active) AS projects;
        """
    )[0]

    return StatsOut(**row)


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
