from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from src.application.use_cases.get_campaign_calls import (
    GetCampaignCallsUseCase,
)
from src.core.containers import get_container
from src.core.server import create_app
from src.domain.models import CallResponse, CampaignNotFound


@pytest.fixture
def api_client():
    app = create_app()

    use_case = AsyncMock(spec=GetCampaignCallsUseCase)
    container = Mock()
    container.resolve.return_value = use_case

    app.dependency_overrides[get_container] = lambda: container

    yield app, use_case, container

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_calls_via_http_and_schema(api_client):
    app, use_case, container = api_client

    use_case.execute.return_value = [
        CallResponse(
            call_id=f"call_000{i}",
            campaign_id="camp_001",
            phone="79001234567",
            status="success",
            created_at="2026-10-20T10:06:00Z",
        )
        for i in (1, 2)
    ]

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/v1/campaigns/camp_001/calls")

        assert response.status_code == 200
        assert len(response.json()) == 2
        assert all(call["campaign_id"] == "camp_001" for call in response.json())

        use_case.execute.assert_awaited_once_with("camp_001")
        container.resolve.assert_called_once_with(GetCampaignCallsUseCase)

        schema = (await client.get("/openapi.json")).json()

        assert "/v1/campaigns/{campaign_id}/calls" in schema["paths"]


@pytest.mark.asyncio
async def test_missing_campaign_returns_http_200(api_client):
    app, use_case, container = api_client

    use_case.execute.return_value = CampaignNotFound(message="Кампания не найдена.")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/v1/campaigns/missing/calls")

        assert response.status_code == 200
        assert response.json() == {"message": "Кампания не найдена."}

        use_case.execute.assert_awaited_once_with("missing")
        container.resolve.assert_called_once_with(GetCampaignCallsUseCase)
