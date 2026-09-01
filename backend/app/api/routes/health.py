from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    summary="Check API health",
    description="Verifies that the API is running correctly.",
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}
