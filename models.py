from pydantic import BaseModel, Field
from typing import Optional


class BikeListingData(BaseModel):
    """Represents data for a Craigslist bike listing"""
    title: str
    price: Optional[str] = Field(
        description="Price of the bike listing, optionally with the currency attached. Example: `$625`",
        default=None,
    )
    bicycle_type: Optional[str] = Field(
        description="Bicycle type of the bike listing, ex. road bike, cruiser, comfort, etc.",
        default=None,
    )
    wheel_size: Optional[str] = Field(
        description="Wheel size of the bike listing, ex. `700C`", default=None
    )
    frame_size: Optional[str] = Field(
        description="Frame size of the bike listing, optionally with unit attached ex. `56cm`",
        default=None,
    )
    frame_material: Optional[str] = Field(
        description="Material of the frame, ex. carbon fiber, alumnimum, etc",
        default=None,
    )
    manufacturer: Optional[str] = Field(
        description="Manufacturer of the bike listing, ex. Trek, Scott", default=None
    )
    model: Optional[str] = Field(
        description="The model name of the bike, ex. Alpha 1.2", default=None
    )
    condition: Optional[str] = Field(
        description="The condition of the bike listing, ex. `like brand new`",
        default=None,
    )
    body: str = Field(
        description="Main posting body text. This contains the whole post description"
    )
    url: str = Field(description="URL of the bike listing")
