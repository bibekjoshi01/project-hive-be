from fastapi import APIRouter, Request, status

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
