from src.application.services.calls import CallService
from src.application.services.campaigns import CampaignService
from src.domain.models import CallResponse, CampaignNotFound


class GetCampaignCallsUseCase:
    def __init__(self, campaigns: CampaignService, calls: CallService) -> None:
        self.campaigns = campaigns
        self.calls = calls

    async def execute(self, campaign_id: str) -> list[CallResponse] | CampaignNotFound:
        if not await self.campaigns.exists(campaign_id):
            return CampaignNotFound(message="Кампания не найдена.")
        calls = await self.calls.list_for_campaign(campaign_id)
        return [CallResponse.model_validate(call.model_dump()) for call in calls]
