# Changelog

All notable changes to this repository are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project uses semantic versioning.

## [0.3.0] — 2026-05-07

### Added — Engine 2 (CDS) Recommendation types

- New `Recommendation` schema (`schemas/recommendation.schema.json`)
  representing a clinical-decision-support output from Engine 2.
- New `FindingRef` schema (`schemas/finding-ref.schema.json`) extracted
  as a shared definition (used by `cdxFlag.triggeredBy`,
  `contraindication.triggeredBy`, `recommendation.triggeredBy`, and
  trial-match references).
- `NonDeviceCdsAttestation` embedded in every `Recommendation` —
  required four-boolean attestation per FDA Non-Device CDS criteria:
  `timeNotCritical`, `publiclyAvailableEvidence`,
  `transparentlyExplained`, `clinicianCanVerify`.
- `EvidenceLink` type with `kbSource` enum restricted to the
  licensing-cleared set: `CIViC`, `ClinVar`, `ClinicalTrials.gov`,
  `openFDA`, `CPIC`, `PubMed`, `ACMG-AMP-2015`, `AMP-ASCO-CAP-2017`,
  `literature`. OncoKB / NCCN / COSMIC are excluded from the enum to
  prevent the engine from emitting recommendations cited against
  proprietary KBs we don't license.

### Added — Pydantic types

- New module `unmiri_ngs_interpretation/recommendations.py` exporting
  `Recommendation`, `EvidenceLink`, `NonDeviceCdsAttestation`,
  `RecommendationType`, `RecommendationPriority`, `EvidenceKbSource`,
  `RecommendationDrug`, `RecommendationDisease`.
- `unmiri_ngs_interpretation` package now re-exports the new types
  from its `__init__.py`.

### Changed — backward compatible

- `NgsInterpretationResponse.recommendations` is added as an optional
  list. Existing parsers that don't emit recommendations continue to
  validate. Engine 2's `/v2/recommendations` API returns a separate
  envelope; downstream consumers may merge into the parsed response.
- Python types package version bumped from `0.1.0` (per pyproject)
  / `0.2.0` (per `__version__`) to `0.3.0` — both are now consistent.

### Why

Engine 2 is the genomics-aware clinical-decision-support engine. It
emits structured recommendations citing evidence chains rather than
free-form clinical advice. The `NonDeviceCdsAttestation` enforces
the FDA Non-Device CDS posture in the schema itself: a recommendation
without an attestation block fails validation.

The `kbSource` enum is the load-bearing piece for license hygiene —
it restricts the engine to publicly available reference data and
makes proprietary-KB citations impossible without a schema change.

## [0.2.0] — 2026-05-06

### Added

- New `Provenance` schema (`schemas/provenance.schema.json`) tracking
  source-tier metadata required on every extracted finding. Fields:
  `sourceTier`, `sourceFormat`, `sourcePage`, `sourceBbox`,
  `sourceTextQuote`, `sourceSection`, `extractorVersion`,
  `judgeVerdict`, `confidence`, `validationFlags`.
- `Provenance`, `SourceBbox`, `SourceTier`, `SourceFormat`,
  `JudgeVerdict`, `ValidationFlag` exported from the Python types
  package.

### Changed (BREAKING)

- `Variant.provenance` is now **required**. A Variant emitted to the
  canonical store without complete provenance is a clinical-safety
  failure per the engine 1 architecture. Findings without provenance
  must be routed to human review.
- `Biomarker.provenance` is now **required** for the same reason.
- Python types package version bumped to `0.2.0`.

### Why

The `unmiri-engine-1` 5-tier extraction pipeline (per
`docs/architecture.md`) routes each PDF page through Triage →
Deterministic → ML layout (deferred) → Cloud OCR → Vision LLM, with
validation gates between every tier and an LLM-as-judge gate after
Tier 4. Without provenance metadata on the finding, a clinical-
incident reviewer cannot answer "where did this BRCA2 variant come
from" — which extractor, which page, with what supporting text quote,
whether a downstream judge agreed. v0.1.0 made this optional. v0.2.0
makes it required to align with the production pipeline.

### Migration

Consumers building `Variant` or `Biomarker` instances must populate
`.provenance`. For ingestion paths that come from a vendor structured
feed (XML / JSON / HL7-FHIR), use `sourceTier="structured-feed"`.
For PDF parsers, use the appropriate `tier-N-...` value. For human
overrides, use `sourceTier="human-curated"`.

---

## [0.1.0] — 2026-05-05

Initial public release.

### Added
- 8 JSON Schemas (Draft 2020-12) covering audit envelope, specimen,
  variant, biomarker, CDx flag, trial match, contraindication, and the
  top-level `NgsInterpretationResponse`.
- Hand-written TypeScript types in `types/typescript/index.ts` mirroring
  the schemas, publishable as `@unmiri/ngs-interpretation-types`.
- Pydantic v2 models in `types/python/unmiri_ngs_interpretation/`,
  publishable as `unmiri-ngs-interpretation`.
- 8 synthetic, watermarked example payloads under `examples/`,
  designed to exercise the schema across the cancer types and finding
  patterns most commonly encountered in cross-vendor NGS interpretation.
  Distinctive variant names and combinations are invented to exercise
  the contract; resemblance to a real case or to any vendor's published
  template is coincidental and not intended. Every example carries the
  literal watermark `Synthetic data — demonstration only` in
  `audit.watermark`.
- `scripts/validate.py` — runs both JSON Schema and pydantic validators
  over every example. CI parity is part of the contract.
- README, CONTRIBUTING, LICENSE (Apache-2.0), NOTICE.

### Design decisions
- **Public clinical-evidence taxonomy**: `evidence.ampAscoCapTier` uses
  AMP/ASCO/CAP 2017 (Li MM et al., J Mol Diagn 2017). Values:
  `"I-A" | "I-B" | "II-C" | "II-D" | "III" | "IV"`.
- **Extension hook for licensed level systems**: `evidence.externalLevels`
  is an open-ended `Record<string, string>` map keyed by knowledge-base
  identifier (e.g., `{"oncokb": "1"}`, `{"civic": "A"}`). Use only with
  appropriate licensing for the referenced KB. The open contract does
  not prescribe values for any particular KB and intentionally does not
  bake any specific proprietary level taxonomy into the schema.
- **Licensed proprietary KBs are NOT part of the open contract**.
  OncoKB, COSMIC's curated content, and NCCN guidelines all require
  separate commercial licensing arrangements. The `KnowledgeBaseName`
  enum in the audit envelope intentionally excludes them.
  Implementations that integrate licensed KBs do so under their own
  licensing terms via the `evidence.externalLevels` hook; identifier-only
  fields (`cosmicId`, `clinvarId`) are permitted on the same principle
  as a PubMed ID — references to a record, not redistribution of
  curated content.

### Notes
- Pre-1.0. The contract is explicitly unstable; breaking changes may
  land in subsequent 0.x releases as community feedback consolidates
  the shape.
