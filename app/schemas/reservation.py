from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ReservationCreate(BaseModel):
    item_id: int = Field(ge=1)
    date_debut: date
    date_fin: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_fin <= self.date_debut:
            raise ValueError("date_fin doit être postérieure à date_debut")
        return self


class ReservationRead(BaseModel):
    id: int
    item_id: int
    date_debut: date
    date_fin: date
    statut: Literal["active", "annulee"]