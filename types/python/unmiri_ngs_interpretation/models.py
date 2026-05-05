"""
Pydantic v2 models for the cross-vendor NGS interpretation
API contract. Mirrors the JSON Schemas in ../../schemas/. Hand-written so
field types, Field(description=...) text, and validators stay readable;
when schemas change, update both representations together.

Schema version: 0.1.0
License: Apache-2.0
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Closed value sets — kept as Literal aliases rather than Enum classes for
# JSON Schema parity (Literal serializes as the string value directly).
# ---------------------------------------------------------------------------

KnowledgeBaseName = Literal[
    "ClinVar",
    "ClinicalTrials.gov",
    "openFDA",
    "AACR Project GENIE",
    "TCGA",
    "HGNC",
    "Ensembl",
    "RefSeq",
    "RxNorm",
    "SNOMED-CT",
    "LOINC",
    "ICD-O-3",
    "other",
]

ReportFormat = Literal["pdf", "json", "xml", "hl7v2", "hl7-fhir", "edi-x12", "csv", "other"]

SpecimenType = Literal[
    "ffpe-tumor-tissue",
    "fresh-frozen-tumor-tissue",
    "blood-plasma-cfdna",
    "blood-whole",
    "saliva",
    "bone-marrow-aspirate",
    "fine-needle-aspirate",
    "fluid-other",
    "other",
]

VariantType = Literal[
    "snv",
    "mnv",
    "insertion",
    "deletion",
    "indel",
    "duplication",
    "cnv-amplification",
    "cnv-loss",
    "fusion",
    "rearrangement",
    "exon-skipping",
    "splice",
    "complex",
    "other",
]

MolecularConsequence = Literal[
    "missense_variant",
    "synonymous_variant",
    "stop_gained",
    "stop_lost",
    "frameshift_variant",
    "inframe_insertion",
    "inframe_deletion",
    "splice_donor_variant",
    "splice_acceptor_variant",
    "splice_region_variant",
    "intron_variant",
    "5_prime_UTR_variant",
    "3_prime_UTR_variant",
    "coding_sequence_variant",
    "structural_variant",
    "fusion",
    "regulatory_region_variant",
    "intergenic_variant",
]

FunctionalEffect = Literal[
    "loss-of-function", "gain-of-function", "neutral", "switch-of-function", "unknown"
]

ClinicalSignificance = Literal[
    "pathogenic",
    "likely-pathogenic",
    "uncertain-significance",
    "likely-benign",
    "benign",
    "conflicting",
    "not-classified",
]

AmpAscoCapTier = Literal["I-A", "I-B", "II-C", "II-D", "III", "IV"]

BiomarkerType = Literal[
    "tmb",
    "msi",
    "mmr",
    "hrd",
    "loh",
    "pd-l1",
    "er",
    "pr",
    "her2-ihc",
    "her2-ish",
    "ar",
    "ki-67",
    "tumor-fraction",
    "tumor-purity",
    "other",
]

BiomarkerInterpretation = Literal[
    "positive",
    "negative",
    "high",
    "intermediate",
    "low",
    "stable",
    "unstable",
    "deficient",
    "proficient",
    "amplified",
    "not-amplified",
    "equivocal",
    "indeterminate",
    "not-applicable",
]

ContraindicationReason = Literal[
    "resistance-mutation",
    "lack-of-benefit-evidence",
    "absence-of-required-biomarker",
    "drug-gene-interaction",
    "immunotherapy-low-tmb",
    "tumor-type-not-indicated",
    "germline-toxicity-risk",
    "regulator-warning",
    "other",
]

ApprovalRegime = Literal[
    "FDA", "EMA", "MHRA", "PMDA", "NMPA", "Health-Canada", "TGA", "other"
]

LineOfTherapy = Literal[
    "first-line",
    "second-line",
    "third-line-or-later",
    "any-line",
    "maintenance",
    "adjuvant",
    "neoadjuvant",
]

TrialPhase = Literal[
    "early-phase-1",
    "phase-1",
    "phase-1-2",
    "phase-2",
    "phase-2-3",
    "phase-3",
    "phase-4",
    "not-applicable",
]

TrialStatus = Literal[
    "not-yet-recruiting",
    "recruiting",
    "enrolling-by-invitation",
    "active-not-recruiting",
    "suspended",
    "terminated",
    "completed",
    "withdrawn",
    "unknown",
]

# ---------------------------------------------------------------------------
# Common base — strict, no extra fields
# ---------------------------------------------------------------------------


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Audit envelope
# ---------------------------------------------------------------------------


class VendorSource(_Strict):
    vendor: str = Field(description="Lab or vendor that produced the source report.")
    product: str = Field(description="Specific assay product (e.g., 'FoundationOne CDx').")
    report_id: Optional[str] = Field(default=None, alias="reportId")
    report_format: ReportFormat = Field(alias="reportFormat")
    received_at: datetime = Field(alias="receivedAt", description="When the pipeline received the source report.")


class KnowledgeBaseRef(_Strict):
    name: KnowledgeBaseName
    version: str = Field(description="KB-specific version string.")
    refreshed_at: datetime = Field(alias="refreshedAt")


class DataSourceAttribution(_Strict):
    name: str
    attribution: str
    url: Optional[str] = None


class ReasoningStep(_Strict):
    step: int = Field(ge=1)
    description: str
    inputs: Optional[List[str]] = None
    knowledge_base_ref: Optional[str] = Field(default=None, alias="knowledgeBaseRef")


class AuditEnvelope(_Strict):
    """Provenance metadata accompanying every NGS interpretation response."""

    response_id: UUID = Field(alias="responseId")
    generated_at: datetime = Field(alias="generatedAt")
    engine_version: str = Field(alias="engineVersion", description="Semver of the NGS interpretation pipeline.")
    schema_version: str = Field(alias="schemaVersion", description="Semver of this response schema.")
    vendor_source: VendorSource = Field(alias="vendorSource")
    knowledge_bases: List[KnowledgeBaseRef] = Field(alias="knowledgeBases", min_length=1)
    watermark: Literal["Synthetic data — demonstration only", "Production"]
    data_sources: Optional[List[DataSourceAttribution]] = Field(default=None, alias="dataSources")
    reasoning_trace: Optional[List[ReasoningStep]] = Field(default=None, alias="reasoningTrace")


# ---------------------------------------------------------------------------
# Specimen
# ---------------------------------------------------------------------------


class TumorSiteCoding(_Strict):
    snomed_code: Optional[str] = Field(default=None, alias="snomedCode")
    icdo3_topography: Optional[str] = Field(default=None, alias="icdo3Topography")
    display: str


class HistologyCoding(_Strict):
    icdo3_morphology: Optional[str] = Field(default=None, alias="icdo3Morphology")
    snomed_code: Optional[str] = Field(default=None, alias="snomedCode")
    display: Optional[str] = None


class CtdnaTumorFraction(_Strict):
    value: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    interpretation: Literal["low", "intermediate", "high", "indeterminate"]


class Specimen(_Strict):
    specimen_id: Optional[str] = Field(default=None, alias="specimenId")
    specimen_type: SpecimenType = Field(alias="specimenType")
    primary_tumor_site: TumorSiteCoding = Field(alias="primaryTumorSite")
    histology: Optional[HistologyCoding] = None
    specimen_site: Optional[str] = Field(default=None, alias="specimenSite")
    collection_date: Optional[date] = Field(default=None, alias="collectionDate")
    received_date: Optional[date] = Field(default=None, alias="receivedDate")
    tumor_content: Optional[float] = Field(default=None, alias="tumorContent", ge=0.0, le=100.0)
    ctdna_tumor_fraction: Optional[CtdnaTumorFraction] = Field(default=None, alias="ctdnaTumorFraction")


# ---------------------------------------------------------------------------
# Shared evidence + KB-source models
# ---------------------------------------------------------------------------


class EvidenceLevel(_Strict):
    """Evidence-tier metadata. AMP/ASCO/CAP 2017 is the public taxonomy carried in
    the open contract. Proprietary or third-party levels go in external_levels
    keyed by knowledge-base name; obtain appropriate licensing before populating it.
    """

    amp_asco_cap_tier: Optional[AmpAscoCapTier] = Field(default=None, alias="ampAscoCapTier")
    external_levels: Optional[dict[str, str]] = Field(
        default=None,
        alias="externalLevels",
        description=(
            "Open-ended map of proprietary evidence levels keyed by knowledge-base "
            "identifier (e.g., {'civic': 'A'}). Use only with appropriate licensing."
        ),
    )


class KbSourceRef(_Strict):
    knowledge_base: str = Field(alias="knowledgeBase")
    record_id: str = Field(alias="recordId")
    url: Optional[str] = None


# ---------------------------------------------------------------------------
# Variant
# ---------------------------------------------------------------------------


class Gene(_Strict):
    symbol: str = Field(description="HGNC official gene symbol.")
    hgnc_id: Optional[str] = Field(default=None, alias="hgncId")


class Variant(_Strict):
    variant_id: UUID = Field(alias="variantId")
    gene: Gene
    transcript: Optional[str] = None
    hgvs_coding: Optional[str] = Field(default=None, alias="hgvsCoding")
    hgvs_protein: Optional[str] = Field(default=None, alias="hgvsProtein")
    hgvs_genomic: Optional[str] = Field(default=None, alias="hgvsGenomic")
    assembly: Optional[Literal["GRCh37", "GRCh38", "T2T-CHM13"]] = None
    chromosome: Optional[str] = None
    start: Optional[int] = Field(default=None, ge=1)
    end: Optional[int] = Field(default=None, ge=1)
    reference_allele: Optional[str] = Field(default=None, alias="referenceAllele")
    alternate_allele: Optional[str] = Field(default=None, alias="alternateAllele")
    variant_type: VariantType = Field(alias="variantType")
    molecular_consequence: Optional[MolecularConsequence] = Field(default=None, alias="molecularConsequence")
    functional_effect: Optional[FunctionalEffect] = Field(default=None, alias="functionalEffect")
    variant_allele_fraction: Optional[float] = Field(default=None, alias="variantAlleleFraction", ge=0.0, le=1.0)
    copy_number: Optional[int] = Field(default=None, alias="copyNumber", ge=0)
    fusion_partner: Optional[str] = Field(default=None, alias="fusionPartner")
    exon: Optional[int] = Field(default=None, ge=1)
    clinvar_id: Optional[str] = Field(default=None, alias="clinvarId")
    cosmic_id: Optional[str] = Field(default=None, alias="cosmicId")
    clinical_significance: Optional[ClinicalSignificance] = Field(default=None, alias="clinicalSignificance")
    germline_or_somatic: Literal["somatic", "germline", "unknown"] = Field(alias="germlineOrSomatic")
    evidence: Optional[EvidenceLevel] = None
    sources: Optional[List[KbSourceRef]] = None


# ---------------------------------------------------------------------------
# Biomarker
# ---------------------------------------------------------------------------


class BiomarkerThreshold(_Strict):
    value: float
    operator: Literal["gte", "lte", "gt", "lt", "eq"]
    unit: Optional[str] = None


class Biomarker(_Strict):
    biomarker_id: UUID = Field(alias="biomarkerId")
    type: BiomarkerType
    loinc_code: Optional[str] = Field(default=None, alias="loincCode")
    method: Literal["ngs", "ihc", "fish", "cish", "pcr", "ish", "other"]
    value: Optional[Union[float, str]] = None
    unit: Optional[str] = None
    interpretation: BiomarkerInterpretation
    threshold: Optional[BiomarkerThreshold] = None
    antibody_clone: Optional[str] = Field(default=None, alias="antibodyClone")
    scoring_system: Optional[str] = Field(default=None, alias="scoringSystem")
    score: Optional[str] = None
    evidence: Optional[EvidenceLevel] = None
    sources: Optional[List[KbSourceRef]] = None


# ---------------------------------------------------------------------------
# Cross-cutting reference: variant or biomarker pointer
# ---------------------------------------------------------------------------


class FindingRef(_Strict):
    ref_type: Literal["variant", "biomarker"] = Field(alias="refType")
    ref_id: UUID = Field(alias="refId")


# ---------------------------------------------------------------------------
# Drug + indication shared types
# ---------------------------------------------------------------------------


class DrugRef(_Strict):
    name: str = Field(description="International nonproprietary name (lowercase).")
    brand_name: Optional[str] = Field(default=None, alias="brandName")
    rx_norm_cui: Optional[str] = Field(default=None, alias="rxNormCui")
    atc_code: Optional[str] = Field(default=None, alias="atcCode")


class DrugRefWithClass(DrugRef):
    drug_class: Optional[str] = Field(default=None, alias="drugClass")


class Indication(_Strict):
    tumor_type: str = Field(alias="tumorType")
    line: Optional[LineOfTherapy] = None
    snomed_code: Optional[str] = Field(default=None, alias="snomedCode")
    icdo3_topography: Optional[str] = Field(default=None, alias="icdo3Topography")


class ApprovedAssay(_Strict):
    vendor: str
    product: str
    fda_approval_number: Optional[str] = Field(default=None, alias="fdaApprovalNumber")


class Citation(_Strict):
    citation: str
    url: Optional[str] = None
    knowledge_base: Optional[str] = Field(default=None, alias="knowledgeBase")


# ---------------------------------------------------------------------------
# CDx Flag
# ---------------------------------------------------------------------------


class CdxFlag(_Strict):
    cdx_flag_id: UUID = Field(alias="cdxFlagId")
    triggered_by: List[FindingRef] = Field(alias="triggeredBy", min_length=1)
    drug: DrugRef
    indication: Indication
    approval_regime: ApprovalRegime = Field(alias="approvalRegime")
    approval_date: Optional[date] = Field(default=None, alias="approvalDate")
    approved_assay: Optional[ApprovedAssay] = Field(default=None, alias="approvedAssay")
    evidence: Optional[EvidenceLevel] = None
    citations: Optional[List[Citation]] = None


# ---------------------------------------------------------------------------
# Trial Match
# ---------------------------------------------------------------------------


class EligibilityHint(_Strict):
    criterion: str
    match_status: Literal["match", "mismatch", "unknown"] = Field(alias="matchStatus")
    reason: Optional[str] = None


class TrialDrug(_Strict):
    name: str
    rx_norm_cui: Optional[str] = Field(default=None, alias="rxNormCui")


class TrialLocation(_Strict):
    city: Optional[str] = None
    state_or_region: Optional[str] = Field(default=None, alias="stateOrRegion")
    country: str


class TrialMatch(_Strict):
    trial_match_id: UUID = Field(alias="trialMatchId")
    nct_id: str = Field(alias="nctId", pattern=r"^NCT\d{8}$")
    title: str
    phase: Optional[TrialPhase] = None
    status: TrialStatus
    trial_data_as_of: Optional[date] = Field(default=None, alias="trialDataAsOf")
    sponsor: Optional[str] = None
    match_strength: Literal["likely-eligible", "possibly-eligible", "ineligible-but-relevant"] = Field(alias="matchStrength")
    triggered_by: List[FindingRef] = Field(alias="triggeredBy", min_length=1)
    eligibility_hints: Optional[List[EligibilityHint]] = Field(default=None, alias="eligibilityHints")
    drugs: Optional[List[TrialDrug]] = None
    locations: Optional[List[TrialLocation]] = None
    url: Optional[str] = None


# ---------------------------------------------------------------------------
# Contraindication
# ---------------------------------------------------------------------------


class Contraindication(_Strict):
    contraindication_id: UUID = Field(alias="contraindicationId")
    triggered_by: List[FindingRef] = Field(alias="triggeredBy", min_length=1)
    drug: DrugRefWithClass
    reason: ContraindicationReason
    narrative: Optional[str] = None
    evidence: Optional[EvidenceLevel] = None
    citations: Optional[List[Citation]] = None


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------


class NgsInterpretationResponse(_Strict):
    """Top-level NGS interpretation response payload."""

    audit: AuditEnvelope
    specimen: Specimen
    variants: List[Variant]
    biomarkers: List[Biomarker]
    cdx_flags: List[CdxFlag] = Field(alias="cdxFlags")
    trial_matches: List[TrialMatch] = Field(alias="trialMatches")
    contraindications: List[Contraindication]
