# Changelog

All notable changes to this repository are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project uses semantic versioning.

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
