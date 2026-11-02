from pymongo.asynchronous.collection import AsyncCollection

from src.core.repositories.base import CampaignRepository
from src.domain.models import Campaign
from src.infrastructure.repositories.base import BaseMongoRepository


class MongoCampaignRepository(BaseMongoRepository[Campaign], CampaignRepository):
    def __init__(self, collection: AsyncCollection) -> None:
        super().__init__(collection, Campaign, id_field="campaign_id")

    async def ensure_exists(self, campaign: Campaign) -> None:
        await self.collection.update_one(
            {"campaign_id": campaign.campaign_id},
            {"$setOnInsert": campaign.model_dump()},
            upsert=True,
        )

    async def find_by_id(self, campaign_id: str) -> Campaign | None:
        result = await self.get_by("campaign_id", campaign_id, unique=True)
        return result
