from fastapi import APIRouter

from src.application.use_cases.get_campaign_calls import GetCampaignCallsUseCase
from src.core.containers import ContainerDep
from src.domain.models import CallResponse, CampaignNotFound

router = APIRouter()


@router.get(
    "/campaigns/{campaign_id}/calls",
    response_model=list[CallResponse] | CampaignNotFound,
    status_code=200,
    summary="Get calls of a campaign",
)
async def get_campaign_calls(
    campaign_id: str,
    container: ContainerDep,
) -> list[CallResponse] | CampaignNotFound:
    use_case: GetCampaignCallsUseCase = container.resolve(GetCampaignCallsUseCase)
    return await use_case.execute(campaign_id)
