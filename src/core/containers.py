from typing import Annotated

import punq
from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from src.application.services.calls import CallService
from src.application.services.campaigns import CampaignService
from src.application.use_cases.get_campaign_calls import GetCampaignCallsUseCase
from src.application.use_cases.save_call_event import SaveCallEventUseCase
from src.core.repositories.base import CallRepository, CampaignRepository
from src.infrastructure.repositories.calls import MongoCallRepository
from src.infrastructure.repositories.campaigns import MongoCampaignRepository


def build_container(db: AsyncDatabase) -> punq.Container:
    container = punq.Container()

    container.register(
        CampaignRepository,
        instance=MongoCampaignRepository(db["campaigns"]),
    )
    container.register(
        CallRepository,
        instance=MongoCallRepository(db["calls"]),
    )

    container.register(CampaignService)
    container.register(CallService)

    container.register(SaveCallEventUseCase)
    container.register(GetCampaignCallsUseCase)

    return container


def get_container(request: Request) -> punq.Container:
    return request.app.state.container


ContainerDep = Annotated[punq.Container, Depends(get_container)]
