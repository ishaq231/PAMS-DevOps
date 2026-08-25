from fastapi import HTTPException


def get_or_404(result, detail="Not found"):
    """Raise a 404 if result is falsy, otherwise return it unchanged."""
    if not result:
        raise HTTPException(status_code=404, detail=detail)
    return result