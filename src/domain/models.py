from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Campaign(StrictModel):
    campaign_id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1)
    created_at: AwareDatetime


class Call(StrictModel):
    call_id: str = Field(min_length=1, max_length=128)
    campaign_id: str = Field(min_length=1, max_length=128)
    phone: str = Field(pattern=r"^\d{11}$")
    status: str = Field(min_length=1)
    created_at: AwareDatetime


class CallEvent(StrictModel):
    campaign: Campaign
    call: Call

    @model_validator(mode="after")
    def validate_campaign_relation(self) -> "CallEvent":
        if self.campaign.campaign_id != self.call.campaign_id:
            raise ValueError("campaign_id в вызове должен совпадать с campaign.campaign_id")
        return self


class CallResponse(Call):
    """Модель ответа API"""


class CampaignNotFound(StrictModel):
    message: str = Field(examples=["Кампания не найдена."])
