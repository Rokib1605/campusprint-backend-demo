from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Category = Literal["PRINT", "BINDING"]
OrderStatus = Literal["DRAFT", "SUBMITTED", "PRINTING", "READY", "COLLECTED", "CANCELLED"]


class OptionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=2, max_length=24, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=2, max_length=80)
    category: Category
    unit_price_bdt: int = Field(ge=1, le=10000)
    available: bool = True


class OptionPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str | None = Field(default=None, min_length=2, max_length=24, pattern=r"^[A-Z0-9_-]+$")
    name: str | None = Field(default=None, min_length=2, max_length=80)
    category: Category | None = None
    unit_price_bdt: int | None = Field(default=None, ge=1, le=10000)
    available: bool | None = None


class PrintOption(OptionInput):
    id: int


class OrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_name: str = Field(min_length=5, max_length=120)
    pages: int = Field(ge=1, le=500)
    copies: int = Field(ge=1, le=30)
    print_option_id: int = Field(ge=1)
    binding_option_id: int | None = Field(default=None, ge=1)

    @field_validator("document_name")
    @classmethod
    def must_be_pdf(cls, value: str) -> str:
        if not value.lower().endswith(".pdf") or "/" in value or "\\" in value:
            raise ValueError("document_name must be a PDF filename, not a path")
        return value


class OrderPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_name: str | None = Field(default=None, min_length=5, max_length=120)
    pages: int | None = Field(default=None, ge=1, le=500)
    copies: int | None = Field(default=None, ge=1, le=30)
    print_option_id: int | None = Field(default=None, ge=1)
    binding_option_id: int | None = Field(default=None, ge=1)


class PrintOrder(OrderInput):
    id: int
    student_id: str
    status: OrderStatus = "DRAFT"
    print_rate_snapshot_bdt: int
    binding_rate_snapshot_bdt: int
    total_price_bdt: int


class StatusChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: OrderStatus
