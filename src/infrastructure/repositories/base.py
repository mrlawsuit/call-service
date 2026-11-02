from typing import Any, Generic

from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.collection import AsyncCollection

from src.core.repositories.base import BaseRepository, ModelT


class BaseMongoRepository(BaseRepository[ModelT], Generic[ModelT]):
    def __init__(
        self, collection: AsyncCollection, model_class: type[ModelT], id_field: str
    ) -> None:
        self.collection = collection
        self.model_class = model_class
        self.id_field = id_field

    def _to_model(self, document: dict[str, Any]) -> ModelT:
        return self.model_class.model_validate(document)

    @staticmethod
    def _sort(order_: dict[str, list[str]] | None) -> list[tuple[str, int]]:
        sort_fields: list[tuple[str, int]] = []
        if order_:
            for field in order_.get("asc", []):
                sort_fields.append((field, ASCENDING))
            for field in order_.get("desc", []):
                sort_fields.append((field, DESCENDING))
        return sort_fields

    async def create(self, attributes: dict[str, Any]) -> ModelT:
        model = self.model_class.model_validate(attributes)
        await self.collection.insert_one(model.model_dump())
        return model

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_: dict[str, list[str]] | None = None,
    ) -> list[ModelT]:
        result = await self.get_by_filter({}, skip=skip, limit=limit, order_=order_)
        assert isinstance(result, list)
        return result

    async def get_by(
        self,
        field: str,
        value: Any,
        *,
        unique: bool = False,
        order_: dict[str, list[str]] | None = None,
    ) -> list[ModelT] | ModelT | None:
        return await self.get_by_filter({field: value}, unique=unique, order_=order_)

    async def get_by_filter(
        self,
        filter_params: dict[str, Any],
        *,
        unique: bool = False,
        skip: int = 0,
        limit: int = 100,
        order_: dict[str, list[str]] | None = None,
    ) -> list[ModelT] | ModelT | None:
        if skip < 0 or limit < 0:
            raise ValueError("skip and limit must be >= 0")
        cursor = self.collection.find(filter_params, {"_id": 0})
        sorting = self._sort(order_)
        if sorting:
            cursor = cursor.sort(sorting)
        cursor = cursor.skip(skip).limit(1 if unique else limit)
        records = await cursor.to_list(length=1 if unique else limit)
        if unique:
            return self._to_model(records[0]) if records else None
        return [self._to_model(record) for record in records]

    async def update(
        self, instance_id: str, attributes: dict[str, Any]
    ) -> ModelT | None:
        # Обновление неизменяемого бизнес-ключа или исходного поля _id в MongoDB запрещено.
        data = {
            key: value
            for key, value in attributes.items()
            if key not in (self.id_field, "_id")
        }
        if data:
            await self.collection.update_one(
                {self.id_field: instance_id}, {"$set": data}
            )
        return await self.get_by(self.id_field, instance_id, unique=True)

    async def delete(self, instance: ModelT) -> None:
        await self.collection.delete_one(
            {self.id_field: getattr(instance, self.id_field)}
        )
