from src.core.repositories.base import CallRepository
from src.domain.models import Call


class CallService:
    def __init__(self, calls: CallRepository) -> None:
        self.calls = calls

    async def save(self, call: Call) -> None:
        await self.calls.insert_if_absent(call)

    async def list_for_campaign(self, campaign_id: str) -> list[Call]:
        return await self.calls.list_by_campaign(campaign_id)
