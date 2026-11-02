from unittest.mock import MagicMock

from src.application.use_cases.get_campaign_calls import GetCampaignCallsUseCase
from src.application.use_cases.save_call_event import SaveCallEventUseCase
from src.core.containers import build_container
from src.core.repositories.base import CallRepository, CampaignRepository
from src.infrastructure.repositories.calls import MongoCallRepository
from src.infrastructure.repositories.campaigns import MongoCampaignRepository


def test_punq_wires_repository_services_and_use_cases():
    db = {"campaigns": MagicMock(), "calls": MagicMock()}
    container = build_container(db)

    assert isinstance(container.resolve(CampaignRepository), MongoCampaignRepository)
    assert isinstance(container.resolve(CallRepository), MongoCallRepository)
    save = container.resolve(SaveCallEventUseCase)
    read = container.resolve(GetCampaignCallsUseCase)
    assert save.campaigns.campaigns is container.resolve(CampaignRepository)
    assert save.calls.calls is container.resolve(CallRepository)
    assert read.campaigns.campaigns is container.resolve(CampaignRepository)
