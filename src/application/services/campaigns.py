from src.core.repositories.base import CampaignRepository
from src.domain.models import Campaign


class CampaignService:
    def __init__(self, campaigns: CampaignRepository) -> None:
        self.campaigns = campaigns

    async def ensure_exists(self, campaign: Campaign) -> None:
        await self.campaigns.ensure_exists(campaign)

    async def exists(self, campaign_id: str) -> bool:
        return (await self.campaigns.find_by_id(campaign_id)) is not None
