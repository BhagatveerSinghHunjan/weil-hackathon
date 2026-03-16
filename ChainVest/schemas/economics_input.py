from pydantic import BaseModel, field_validator


class UnitEconomicsInput(BaseModel):
    ltv: float
    cac: float
    gross_margin: float
    monthly_new_customers: int

    @field_validator("cac")
    @classmethod
    def validate_cac(cls, value):
        if value <= 0:
            raise ValueError("CAC must be greater than zero.")
        return value

    @field_validator("gross_margin")
    @classmethod
    def validate_margin(cls, value):
        if not (0 <= value <= 100):
            raise ValueError("Gross margin must be between 0 and 100.")
        return value

    @field_validator("monthly_new_customers")
    @classmethod
    def validate_customers(cls, value):
        if value < 0:
            raise ValueError("Monthly new customers cannot be negative.")
        return value