from pydantic import BaseModel, Field, model_validator, ValidationError
from datetime import datetime
from typing import Optional
from typing_extensions import Self
from enum import Enum


class ContactType(Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)  # up to 24 hours
    witness_count: int = Field(ge=1, le=100)
    message_received: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = False

    # @model_validator(mode='after')
    # def check_id(self) -> Self:
    #     if not self.contact_id.startswith("AC"):
    #         raise ValueError("contact_id must start with 'AC'")
    #     return self

    # @model_validator(mode='after')
    # def check_physical_contact(self) -> Self:
    #     if (self.contact_type == ContactType.PHYSICAL
    #           and not self.is_verified):
    #         raise ValueError("Physical contacts reports must be verified")
    #     return self

    # @model_validator(mode='after')
    # def check_telepathic_contact(self) -> Self:
    #     if (self.contact_type == ContactType.TELEPATHIC
    #             and self.witness_count < 3):
    #         raise ValueError(
    #             "Telepathic contacts requires at least 3 witnesses")
    #     return self

    # @model_validator(mode='after')
    # def check_strong_signal(self) -> Self:
    #     if self.signal_strength > 7.0 and not self.message_received:
    #         raise ValueError("Strong signals must have a message received")
    #     return self

    @model_validator(mode='after')
    def check_all_rules(self) -> Self:
        errors = []

        if not self.contact_id.startswith("AC"):
            errors.append("contact_id must start with 'AC'")

        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            errors.append("Physical contacts reports must be verified")

        if (self.contact_type == ContactType.TELEPATHIC
                and self.witness_count < 3):
            errors.append("Telepathic contacts requires at least 3 witnesses")

        if self.signal_strength > 7.0 and not self.message_received:
            errors.append("Strong signals must have a message received")

        if errors:
            raise ValueError("\n".join(errors))

        return self


def main():
    print("\nAlien Contact Data Validation\n"
          "========================================")
    print("Valid contact created:")
    contact = AlienContact(
        contact_id="AC12345",
        timestamp=datetime.now(),
        location="Sector 7G",
        contact_type=ContactType.TELEPATHIC,
        signal_strength=8.5,
        duration_minutes=15,
        witness_count=5,
        message_received="We come in peace.",
        is_verified=True)
    print(f"ID: {contact.contact_id}\n"
          f"Location: {contact.location}\n"
          f"Type: {contact.contact_type.value}\n"
          f"Signal Strength: {contact.signal_strength}\n")

    print("========================================\n"
          "Expected validation error:\n"
          "Telepathic contact requires at least 3 witnesses\n"
          "and Strong signals must have a message received\n")

    try:
        invalid_contact = AlienContact(
            contact_id="AC54321",
            timestamp=datetime.now(),
            location="Sector 9B",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=8.0,
            duration_minutes=30,
            witness_count=2,
            message_received=None,
            is_verified=True)
        print(invalid_contact)
    except ValidationError as e:
        for error in e.errors():
            print(f"Error: {error['msg']} (field: "
                  f"{error['loc'][0] if error['loc'] else 'model_validator'})")


if __name__ == "__main__":
    main()
