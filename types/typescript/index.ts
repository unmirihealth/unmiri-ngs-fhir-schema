/**
 * UNMIRI cross-vendor NGS interpretation API contract
 *
 * TypeScript representation of the JSON Schemas under ../../schemas/.
 * Hand-written rather than generated so identifiers, JSDoc, and unions
 * read idiomatically. When schemas change, update both files together.
 *
 * Schema version: 0.1.0
 * License: Apache-2.0
 */

// ---------------------------------------------------------------------------
// Audit envelope
// ---------------------------------------------------------------------------

export type KnowledgeBaseName =
  | "ClinVar"
  | "ClinicalTrials.gov"
  | "openFDA"
  | "AACR Project GENIE"
  | "TCGA"
  | "HGNC"
  | "Ensembl"
  | "RefSeq"
  | "RxNorm"
  | "SNOMED-CT"
  | "LOINC"
  | "ICD-O-3"
  | "other";

export type ReportFormat =
  | "pdf"
  | "json"
  | "xml"
  | "hl7v2"
  | "hl7-fhir"
  | "edi-x12"
  | "csv"
  | "other";

/** Provenance metadata accompanying every NGS interpretation response. */
export interface AuditEnvelope {
  /** UUIDv4 uniquely identifying this response. */
  responseId: string;
  /** RFC 3339 UTC timestamp when this response was assembled. */
  generatedAt: string;
  /** Semantic version of the NGS interpretation pipeline. */
  engineVersion: string;
  /** Semantic version of this response schema. */
  schemaVersion: string;
  vendorSource: {
    vendor: string;
    product: string;
    reportId?: string | null;
    reportFormat: ReportFormat;
    /** RFC 3339 UTC timestamp when the source report was received. */
    receivedAt: string;
  };
  /** Versioned snapshots of every knowledge source consulted. */
  knowledgeBases: Array<{
    name: KnowledgeBaseName;
    version: string;
    refreshedAt: string;
  }>;
  /** Synthetic-vs-production marker. Required on every payload. */
  watermark: "Synthetic data — demonstration only" | "Production";
  /** Mandatory attributions inherited from data-use agreements. */
  dataSources?: Array<{
    name: string;
    attribution: string;
    url?: string;
  }>;
  /** Optional ordered reasoning steps for clinical-review traceability. */
  reasoningTrace?: Array<{
    step: number;
    description: string;
    inputs?: string[];
    knowledgeBaseRef?: string;
  }>;
}

// ---------------------------------------------------------------------------
// Specimen
// ---------------------------------------------------------------------------

export type SpecimenType =
  | "ffpe-tumor-tissue"
  | "fresh-frozen-tumor-tissue"
  | "blood-plasma-cfdna"
  | "blood-whole"
  | "saliva"
  | "bone-marrow-aspirate"
  | "fine-needle-aspirate"
  | "fluid-other"
  | "other";

export interface Specimen {
  specimenId?: string | null;
  specimenType: SpecimenType;
  primaryTumorSite: {
    snomedCode?: string | null;
    /** ICD-O-3 topography code (e.g., "C34.1"). */
    icdo3Topography?: string | null;
    display: string;
  };
  histology?: {
    /** ICD-O-3 morphology/behavior code (e.g., "8140/3"). */
    icdo3Morphology?: string | null;
    snomedCode?: string | null;
    display?: string;
  };
  specimenSite?: string | null;
  /** ISO 8601 date. */
  collectionDate?: string | null;
  /** ISO 8601 date. */
  receivedDate?: string | null;
  /** Tumor cellularity as percentage (0–100). */
  tumorContent?: number | null;
  /** Liquid-biopsy ctDNA tumor fraction. */
  ctdnaTumorFraction?: {
    value?: number;
    interpretation: "low" | "intermediate" | "high" | "indeterminate";
  } | null;
}

// ---------------------------------------------------------------------------
// Variant
// ---------------------------------------------------------------------------

export type VariantType =
  | "snv"
  | "mnv"
  | "insertion"
  | "deletion"
  | "indel"
  | "duplication"
  | "cnv-amplification"
  | "cnv-loss"
  | "fusion"
  | "rearrangement"
  | "exon-skipping"
  | "splice"
  | "complex"
  | "other";

export type MolecularConsequence =
  | "missense_variant"
  | "synonymous_variant"
  | "stop_gained"
  | "stop_lost"
  | "frameshift_variant"
  | "inframe_insertion"
  | "inframe_deletion"
  | "splice_donor_variant"
  | "splice_acceptor_variant"
  | "splice_region_variant"
  | "intron_variant"
  | "5_prime_UTR_variant"
  | "3_prime_UTR_variant"
  | "coding_sequence_variant"
  | "structural_variant"
  | "fusion"
  | "regulatory_region_variant"
  | "intergenic_variant";

export type FunctionalEffect =
  | "loss-of-function"
  | "gain-of-function"
  | "neutral"
  | "switch-of-function"
  | "unknown";

export type ClinicalSignificance =
  | "pathogenic"
  | "likely-pathogenic"
  | "uncertain-significance"
  | "likely-benign"
  | "benign"
  | "conflicting"
  | "not-classified";

export type AmpAscoCapTier = "I-A" | "I-B" | "II-C" | "II-D" | "III" | "IV";

/**
 * Open-ended map of proprietary or third-party evidence levels keyed by
 * knowledge-base identifier (e.g., `{ civic: "A" }`). Use only with
 * appropriate licensing for the referenced knowledge base. The schema does
 * not prescribe values for any particular KB.
 */
export type ExternalLevels = Record<string, string>;

export interface KbSourceRef {
  knowledgeBase: string;
  recordId: string;
  url?: string;
}

export interface Variant {
  variantId: string;
  gene: {
    /** HGNC official gene symbol. */
    symbol: string;
    /** "HGNC:NNNN". */
    hgncId?: string | null;
  };
  /** RefSeq NM_/Ensembl ENST accession used for HGVS pinning. */
  transcript?: string | null;
  hgvsCoding?: string | null;
  hgvsProtein?: string | null;
  hgvsGenomic?: string | null;
  assembly?: "GRCh37" | "GRCh38" | "T2T-CHM13" | null;
  chromosome?: string | null;
  start?: number | null;
  end?: number | null;
  referenceAllele?: string | null;
  alternateAllele?: string | null;
  variantType: VariantType;
  molecularConsequence?: MolecularConsequence | null;
  functionalEffect?: FunctionalEffect | null;
  /** Variant allele fraction as a 0–1 number. */
  variantAlleleFraction?: number | null;
  copyNumber?: number | null;
  fusionPartner?: string | null;
  exon?: number | null;
  /** ClinVar Variation ID (numeric). */
  clinvarId?: string | null;
  cosmicId?: string | null;
  clinicalSignificance?: ClinicalSignificance | null;
  germlineOrSomatic: "somatic" | "germline" | "unknown";
  evidence?: {
    ampAscoCapTier?: AmpAscoCapTier | null;
    externalLevels?: ExternalLevels;
  };
  sources?: KbSourceRef[];
}

// ---------------------------------------------------------------------------
// Biomarker
// ---------------------------------------------------------------------------

export type BiomarkerType =
  | "tmb"
  | "msi"
  | "mmr"
  | "hrd"
  | "loh"
  | "pd-l1"
  | "er"
  | "pr"
  | "her2-ihc"
  | "her2-ish"
  | "ar"
  | "ki-67"
  | "tumor-fraction"
  | "tumor-purity"
  | "other";

export type BiomarkerInterpretation =
  | "positive"
  | "negative"
  | "high"
  | "intermediate"
  | "low"
  | "stable"
  | "unstable"
  | "deficient"
  | "proficient"
  | "amplified"
  | "not-amplified"
  | "equivocal"
  | "indeterminate"
  | "not-applicable";

export interface Biomarker {
  biomarkerId: string;
  type: BiomarkerType;
  /** LOINC code identifying the measurement. */
  loincCode?: string | null;
  method: "ngs" | "ihc" | "fish" | "cish" | "pcr" | "ish" | "other";
  value?: number | string | null;
  unit?: string | null;
  interpretation: BiomarkerInterpretation;
  threshold?: {
    value: number;
    operator: "gte" | "lte" | "gt" | "lt" | "eq";
    unit?: string | null;
  } | null;
  /** Antibody clone for IHC measurements (e.g., "SP142", "22C3"). */
  antibodyClone?: string | null;
  scoringSystem?: string | null;
  score?: string | null;
  evidence?: {
    ampAscoCapTier?: AmpAscoCapTier | null;
    externalLevels?: ExternalLevels;
  };
  sources?: KbSourceRef[];
}

// ---------------------------------------------------------------------------
// Cross-cutting reference type — variant or biomarker pointer
// ---------------------------------------------------------------------------

export interface FindingRef {
  refType: "variant" | "biomarker";
  /** UUID of the Variant or Biomarker in this same response. */
  refId: string;
}

// ---------------------------------------------------------------------------
// CDx Flag
// ---------------------------------------------------------------------------

export interface DrugRef {
  /** International nonproprietary name, lowercase. */
  name: string;
  brandName?: string | null;
  rxNormCui?: string | null;
  atcCode?: string | null;
}

export interface CdxFlag {
  cdxFlagId: string;
  triggeredBy: FindingRef[];
  drug: DrugRef;
  indication: {
    tumorType: string;
    line?:
      | "first-line"
      | "second-line"
      | "third-line-or-later"
      | "any-line"
      | "maintenance"
      | "adjuvant"
      | "neoadjuvant"
      | null;
    snomedCode?: string | null;
    icdo3Topography?: string | null;
  };
  approvalRegime: "FDA" | "EMA" | "MHRA" | "PMDA" | "NMPA" | "Health-Canada" | "TGA" | "other";
  approvalDate?: string | null;
  approvedAssay?: {
    vendor: string;
    product: string;
    fdaApprovalNumber?: string | null;
  } | null;
  evidence?: {
    ampAscoCapTier?: AmpAscoCapTier | null;
    externalLevels?: ExternalLevels;
  };
  citations?: Array<{
    citation: string;
    url?: string;
    knowledgeBase?: string | null;
  }>;
}

// ---------------------------------------------------------------------------
// Trial Match
// ---------------------------------------------------------------------------

export interface TrialMatch {
  trialMatchId: string;
  /** ClinicalTrials.gov registry ID. */
  nctId: string;
  title: string;
  phase?:
    | "early-phase-1"
    | "phase-1"
    | "phase-1-2"
    | "phase-2"
    | "phase-2-3"
    | "phase-3"
    | "phase-4"
    | "not-applicable"
    | null;
  status:
    | "not-yet-recruiting"
    | "recruiting"
    | "enrolling-by-invitation"
    | "active-not-recruiting"
    | "suspended"
    | "terminated"
    | "completed"
    | "withdrawn"
    | "unknown";
  trialDataAsOf?: string | null;
  sponsor?: string | null;
  matchStrength: "likely-eligible" | "possibly-eligible" | "ineligible-but-relevant";
  triggeredBy: FindingRef[];
  eligibilityHints?: Array<{
    criterion: string;
    matchStatus: "match" | "mismatch" | "unknown";
    reason?: string | null;
  }>;
  drugs?: Array<{
    name: string;
    rxNormCui?: string | null;
  }>;
  /** Coarse geographic facets, not site-level addresses. */
  locations?: Array<{
    city?: string | null;
    stateOrRegion?: string | null;
    country: string;
  }>;
  url?: string | null;
}

// ---------------------------------------------------------------------------
// Contraindication
// ---------------------------------------------------------------------------

export type ContraindicationReason =
  | "resistance-mutation"
  | "lack-of-benefit-evidence"
  | "absence-of-required-biomarker"
  | "drug-gene-interaction"
  | "immunotherapy-low-tmb"
  | "tumor-type-not-indicated"
  | "germline-toxicity-risk"
  | "regulator-warning"
  | "other";

export interface Contraindication {
  contraindicationId: string;
  triggeredBy: FindingRef[];
  drug: DrugRef & { drugClass?: string | null };
  reason: ContraindicationReason;
  narrative?: string | null;
  evidence?: {
    ampAscoCapTier?: AmpAscoCapTier | null;
    externalLevels?: ExternalLevels;
  };
  citations?: Array<{
    citation: string;
    url?: string;
    knowledgeBase?: string | null;
  }>;
}

// ---------------------------------------------------------------------------
// Top-level response
// ---------------------------------------------------------------------------

/** Top-level NGS interpretation response payload. */
export interface NgsInterpretationResponse {
  audit: AuditEnvelope;
  specimen: Specimen;
  variants: Variant[];
  biomarkers: Biomarker[];
  cdxFlags: CdxFlag[];
  trialMatches: TrialMatch[];
  contraindications: Contraindication[];
}
