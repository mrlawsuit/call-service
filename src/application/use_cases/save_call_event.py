from src.application.services.calls import CallService
from src.application.services.campaigns import CampaignService
from src.domain.models import CallEvent


class SaveCallEventUseCase:
    def __init__(self, campaigns: CampaignService, calls: CallService) -> None:
        self.campaigns = campaigns
        self.calls = calls

    async def execute(self, event: CallEvent) -> None:
        # Обе операции upsert являются идемпотентными на случай, если RabbitMQ повторно доставит сообщение.
        await self.campaigns.ensure_exists(event.campaign)
        await self.calls.save(event.call)
