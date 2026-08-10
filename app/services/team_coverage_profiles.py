"""Static workflow coverage profiles for Team Gap v1.

Product workflow definitions only. Not astrology rules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RequiredFunctionDef:
    team_function: str
    workflow_stage: str
    why_it_matters: str


@dataclass(frozen=True)
class CoverageProfile:
    key: str
    name: str
    required_functions: tuple[RequiredFunctionDef, ...]


AI_ML_PRODUCT_DELIVERY = CoverageProfile(
    key="ai_ml_product_delivery",
    name="AI / ML Product Delivery",
    required_functions=(
        RequiredFunctionDef(
            team_function="Explorer / Innovator",
            workflow_stage="Explore",
            why_it_matters=(
                "Surfaces alternative approaches, experiments with emerging technology, "
                "and helps the team discover new technical options."
            ),
        ),
        RequiredFunctionDef(
            team_function="Precision Analyst / Validator",
            workflow_stage="Validate",
            why_it_matters=(
                "Checks assumptions, errors, model behavior, data quality, and whether "
                "an experimental result can be trusted."
            ),
        ),
        RequiredFunctionDef(
            team_function="Structurer / Planner",
            workflow_stage="Productionize",
            why_it_matters=(
                "Turns promising work into structured, repeatable, maintainable "
                "technical delivery."
            ),
        ),
        RequiredFunctionDef(
            team_function="Connector / Communicator",
            workflow_stage="Connect",
            why_it_matters=(
                "Connects technical work with product, integrations, stakeholders, "
                "and the information flow around the system."
            ),
        ),
    ),
)

COVERAGE_PROFILES: dict[str, CoverageProfile] = {
    AI_ML_PRODUCT_DELIVERY.key: AI_ML_PRODUCT_DELIVERY,
}
