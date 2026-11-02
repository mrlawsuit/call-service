from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from src.domain.models import Call, Campaign

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(ABC, Generic[ModelT]):

    @abstractmethod
    async def create(self, attributes: dict[str, Any]) -> ModelT: ...

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_: dict[str, list[str]] | None = None,
    ) -> list[ModelT]: ...

    @abstractmethod
    async def get_by(
        self,
        field: str,
        value: Any,
        *,
        unique: bool = False,
        order_: dict[str, list[str]] | None = None,
    ) -> list[ModelT] | ModelT | None: ...

    @abstractmethod
    async def get_by_filter(
        self,
        filter_params: dict[str, Any],
        *,
        unique: bool = False,
        skip: int = 0,
        limit: int = 100,
        order_: dict[str, list[str]] | None = None,
    ) -> list[ModelT] | ModelT | None: ...

    @abstractmethod
    async def update(
        self, instance_id: str, attributes: dict[str, Any]
    ) -> ModelT | None: ...

    @abstractmethod
    async def delete(self, instance: ModelT) -> None: ...


class CampaignRepository(BaseRepository[Campaign], ABC):
    @abstractmethod
    async def ensure_exists(self, campaign: Campaign) -> None: ...

    @abstractmethod
    async def find_by_id(self, campaign_id: str) -> Campaign | None: ...


class CallRepository(BaseRepository[Call], ABC):
    @abstractmethod
    async def insert_if_absent(self, call: Call) -> None: ...

    @abstractmethod
    async def list_by_campaign(self, campaign_id: str) -> list[Call]: ...
