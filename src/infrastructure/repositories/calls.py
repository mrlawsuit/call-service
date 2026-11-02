from pymongo.asynchronous.collection import AsyncCollection

from src.core.repositories.base import CallRepository
from src.domain.models import Call
from src.infrastructure.repositories.base import BaseMongoRepository


class MongoCallRepository(BaseMongoRepository[Call], CallRepository):
    def __init__(self, collection: AsyncCollection) -> None:
        super().__init__(collection, Call, id_field="call_id")

    async def insert_if_absent(self, call: Call) -> None:
        await self.collection.update_one(
            {"call_id": call.call_id},
            {"$setOnInsert": call.model_dump()},
            upsert=True,
        )

    async def list_by_campaign(self, campaign_id: str) -> list[Call]:
        cursor = self.collection.find({"campaign_id": campaign_id}, {"_id": 0})
        cursor = cursor.sort([("created_at", 1), ("call_id", 1)])
        records = await cursor.to_list(length=None)
        return [self._to_model(record) for record in records]
