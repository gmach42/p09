from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing_extensions import Self
from enum import Enum


class Rank(Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True

    def __str__(self):
        return (
            f"- {self.name} ({self.rank.value}) - {self.specialization}"
            )


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)  # max 10 years
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def check_mission_id(self) -> Self:
        mission_id = self.mission_id
        if not mission_id.startswith("M"):
            raise ValueError("mission_id must start with 'M'")
        return self

    @model_validator(mode='after')
    def check_crew_rank(self) -> Self:
        crew = self.crew
        high_ranked = [
            c for c in crew if (
                c.rank == Rank.COMMANDER or c.rank == Rank.CAPTAIN)
            ]
        if not high_ranked:
            raise ValueError(
                "Crew must have at least one Commander or Captain")
        return self

    @model_validator(mode='after')
    def check_long_missions(self) -> Self:
        duration_days = self.duration_days
        experienced_crew = self.experienced_crew()
        if duration_days > 365 and not experienced_crew:
            raise ValueError(
                "For long missions (> 365 days), "
                "at least half the crew needs to be experienced (5+ years))"
                )
        return self

    def experienced_crew(self) -> bool:
        experienced = [
            exp_c for exp_c in self.crew
            if exp_c.years_experience >= 5
            ]
        if len(experienced)*2 >= len(self.crew):
            return True
        return False

    @model_validator(mode='after')
    def check_all_active(self) -> Self:
        all_active = True if all(c.is_active for c in self.crew) else False
        if not all_active:
            raise ValueError("All crew members must be active")
        return self


def main():
    print("\nSpace Mission Crew Validation")
    print("=========================================")

    print("Valid mission created:")
    try:
        valid_crew = [
            CrewMember(
                name="Sarah Connor",
                rank='commander',
                specialization="Mission Command",
                years_experience=10,
                member_id="C001",
                age=40
            ),
            john_smith := CrewMember(
                name="John Smith",
                rank='lieutenant',
                specialization="Navigation",
                years_experience=6,
                member_id="C002",
                age=35
            ),
            alice_johnson := CrewMember(
                name="Alice Johnson",
                rank='officer',
                specialization="Engineering",
                years_experience=4,
                member_id="C003",
                age=30
            )
        ]
        valid_mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination='Mars',
            duration_days=900,
            budget_millions=2500,
            crew=valid_crew,
            launch_date=datetime.now()
        )

        print(
            f"Mission: {valid_mission.mission_name}\n"
            f"ID: {valid_mission.mission_id}\n"
            f"Destination: {valid_mission.destination}\n"
            f"Duration: {valid_mission.duration_days} days\n"
            f"Budget: ${valid_mission.budget_millions}M\n"
            f"Crew size: {len(valid_mission.crew)}\n"
            f"Crew Members:"
        )
        for member in valid_mission.crew:
            print(member)

    except Exception as e:
        print(e)

    print(
        "\n=========================================\n"
        "Expected validation error:\n"
        "Mission must have at least one Commander or Captain"
    )

    invalid_crew = [
        john_smith, alice_johnson,
        CrewMember(
            name="Anakin Skywalker",
            rank="cadet",
            specialization="Jedi Knight",
            years_experience=2,
            member_id="C004",
            age=28
        )
    ]

    try:
        invalid_mission = SpaceMission(
            mission_id="M2024_VENUS",
            mission_name="Venus Atmospheric Study",
            destination='Venus',
            duration_days=200,
            budget_millions=1500,
            crew=invalid_crew,
            launch_date=datetime.now()
        )
        print(invalid_mission)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
