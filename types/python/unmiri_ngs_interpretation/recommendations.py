"""Pydantic v2 models for Engine 2 (CDS) Recommendation types.

Mirrors schemas/recommendation.schema.json + finding-ref.schema.json.

Design intent — Non-Device Clinical Decision Support:
  Every Recommendation must trace to an explicit evidence chain and
  carry a NonDeviceCdsAttestation. The attestation's four boolean
  fields are required by the schema; missing any one fails validation.
  The engine emits all four = True per the FDA Non-Device CDS criteria.
"""
from __future__ import annotations

from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .models import FindingRef  # canonical FindingRef shared with cdx-flag etc.


class _Strict(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


# ─── Closed value sets ───────────────────────────────────────────────────────

RecommendationType = Literal[
    "therapy-match",
    "resistance-warning",
    "drug-interaction",
    "pgx-dosing",
    "contraindication",
    "hereditary-finding",
    "evidence-gap",
]

RecommendationPriority = Literal["informational", "advisory", "safety-critical"]

EvidenceKbSource = Literal[
    "CIViC", "ClinVar", "ClinicalTrials.gov", "openFDA", "CPIC",
    "PubMed", "ACMG-AMP-2015", "AMP-ASCO-CAP-2017", "literature",
]


# FindingRef is imported from .models at the top of this module.

# ─── Evidence chain ──────────────────────────────────────────────────────────

class EvidenceLink(_Strict):
    """One link in a recommendation's evidence chain.

    `kbSource` must be from the licensing-cleared set. Authors MUST NOT
    reproduce verbatim text from copyrighted sources — `summaryShort`
    is paraphrased.
    """
    kb_source: EvidenceKbSource = Field(alias="kbSource")
    evidence_level: Optional[str] = Field(default=None, alias="evidenceLevel")
    citation: str = Field(min_length=1)
    url: Optional[str] = None
    summary_short: Optional[str] = Field(
        default=None, alias="summaryShort", max_length=600,
    )


# ─── Non-Device CDS attestation ──────────────────────────────────────────────

class NonDeviceCdsAttestation(_Strict):
    """Per-recommendation Non-Device CDS attestation.

    All four booleans MUST be present (Pydantic enforces this — schema
    validation rejects any recommendation missing an attestation field).
    Engine 2 always emits all four = True; surfacing them on every
    recommendation is part of the transparent-explanation invariant.
    """
    time_not_critical: bool = Field(alias="timeNotCritical")
    publicly_available_evidence: bool = Field(alias="publiclyAvailableEvidence")
    transparently_explained: bool = Field(alias="transparentlyExplained")
    clinician_can_verify: bool = Field(alias="clinicianCanVerify")


# ─── Optional drug + disease context on a Recommendation ────────────────────

class RecommendationDrug(_Strict):
    name: str
    rxnorm_cui: Optional[str] = Field(default=None, alias="rxnormCui")
    ncit_id: Optional[str] = Field(default=None, alias="ncitId")


class RecommendationDisease(_Strict):
    code: Optional[str] = None
    code_system: Optional[Literal["NCIt", "DOID", "display"]] = Field(
        default=None, alias="codeSystem",
    )
    display: Optional[str] = None


# ─── Recommendation ──────────────────────────────────────────────────────────

class Recommendation(_Strict):
    recommendation_id: UUID = Field(alias="recommendationId")
    recommendation_type: RecommendationType = Field(alias="recommendationType")
    triggered_by: List[FindingRef] = Field(alias="triggeredBy")
    evidence_chain: List[EvidenceLink] = Field(alias="evidenceChain")
    confidence: float = Field(ge=0.0, le=1.0)
    priority: RecommendationPriority
    narrative: str = Field(max_length=4000)
    non_device_cds_attestation: NonDeviceCdsAttestation = Field(
        alias="nonDeviceCdsAttestation",
    )
    rule_id: Optional[str] = Field(default=None, alias="ruleId")
    associated_drug: Optional[RecommendationDrug] = Field(
        default=None, alias="associatedDrug",
    )
    associated_disease: Optional[RecommendationDisease] = Field(
        default=None, alias="associatedDisease",
    )
