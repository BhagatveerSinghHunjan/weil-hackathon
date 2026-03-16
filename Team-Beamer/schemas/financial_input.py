from typing import List
from pydantic import BaseModel, Field, field_validator


class FinancialInput(BaseModel):
    monthly_revenue: List[float] = Field(..., min_length=12, max_length=12)
    monthly_burn: List[float] = Field(..., min_length=12, max_length=12)
    cash_on_hand: float

    @field_validator("monthly_revenue", "monthly_burn")
    @classmethod
    def validate_no_negative_values(cls, values):
        if any(v < 0 for v in values):
            raise ValueError("Revenue and burn values cannot be negative.")
        return values

    @field_validator("cash_on_hand")
    @classmethod
    def validate_cash_positive(cls, value):
        if value < 0:
            raise ValueError("Cash on hand cannot be negative.")
        return value