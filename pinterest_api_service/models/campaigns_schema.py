from pydantic import BaseModel,Field,constr
from typing import Optional,List

# Define the Pydantic model for the campaign item
class TrackingUrls(BaseModel):
    impression: Optional[List[str]] = []
    click: Optional[List[str]] = []
    engagement: Optional[List[str]] = []
    buyable_button: Optional[List[str]] = []
    audience_verification: Optional[List[str]] = []

class CampaignItem(BaseModel):
    name: str
    status: str
    lifetime_spend_cap: int
    daily_spend_cap: int
    start_time: int
    end_time: int
    is_flexible_daily_budgets: bool
    default_ad_group_budget_in_micro_currency: int
    is_automated_campaign: bool
    objective_type: str
    is_performance_plus: bool
    tracking_urls: Optional[TrackingUrls] = None

class CreateCampaignRequest(BaseModel):
    items: List[CampaignItem]

#--------------------------------------------------------------


# Define the Pydantic model for the campaign item
class TrackingUrls(BaseModel):
    impression: Optional[List[str]] = []
    click: Optional[List[str]] = []
    engagement: Optional[List[str]] = []
    buyable_button: Optional[List[str]] = []
    audience_verification: Optional[List[str]] = []

class CampaignItem(BaseModel):
    id: str
    name: Optional[str] = None
    status: Optional[str] = None
    lifetime_spend_cap: Optional[int] = None
    daily_spend_cap: Optional[int] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    is_flexible_daily_budgets: Optional[bool] = None
    default_ad_group_budget_in_micro_currency: Optional[int] = None
    is_automated_campaign: Optional[bool] = None
    is_campaign_budget_optimization: Optional[bool] = None
    objective_type: Optional[str] = None
    is_performance_plus: Optional[bool] = None
    tracking_urls: Optional[TrackingUrls] = None

class UpdateCampaignRequest(BaseModel):
    items: List[CampaignItem]

#----------------------------------------------
# Pydantic model for the request parameters
