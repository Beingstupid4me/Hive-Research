from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_services
from app.schemas.contracts import AgentQueryRequest
from app.services.container import ServiceContainer

router = APIRouter()


@router.get("/brief")
async def agent_brief(services: ServiceContainer = Depends(get_services)) -> dict[str, object]:
    payload = await services.agent.get_agent_payload()
    return {"agent": payload["agent"]}


@router.get("/stream")
def agent_stream(
    limit: int = Query(default=100, ge=1, le=1000),
    services: ServiceContainer = Depends(get_services),
) -> dict[str, object]:
    return {"agent": {"worker_stream": services.agent.get_worker_stream(limit=limit)}}


@router.post("/query")
async def agent_query(
    payload: AgentQueryRequest,
    services: ServiceContainer = Depends(get_services),
) -> dict[str, object]:
    return await services.agent.answer_query(payload.query)
