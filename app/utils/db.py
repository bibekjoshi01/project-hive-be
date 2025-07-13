from fastapi import HTTPException, status


def parse_ordering(ordering: str, ORDERABLE_COLUMNS: set) -> str:
    """Translate '-name' → 'name DESC', 'id' → 'id ASC'."""

    desc = ordering.startswith("-")
    col = ordering.lstrip("-")

    if col not in ORDERABLE_COLUMNS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ordering field")

    return f"{col} {'DESC' if desc else 'ASC'}"
