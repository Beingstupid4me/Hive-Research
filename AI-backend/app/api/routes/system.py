from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_services
from app.services.container import ServiceContainer

router = APIRouter()


@router.get("/status")
def system_status(services: ServiceContainer = Depends(get_services)) -> dict[str, object]:
    return services.system.get_shell_metrics()
