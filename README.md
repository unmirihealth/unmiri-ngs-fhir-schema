# unmiri-ngs-fhir-schema

A vendor-agnostic, FHIR-Genomics-aligned API contract for next-generation
sequencing (NGS) interpretation in oncology. Open-sourced by
[UNMIRI LLC](https://unmiri.com).

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## What this is

A set of JSON Schemas (Draft 2020-12) plus matching TypeScript types and
Python pydantic v2 models that describe the *output* of an NGS interpretation
pipeline. The shape covers everything a downstream EHR, CDS module, oncology
platform, or trial-matching engine needs from a parsed report:

- **variants** — gene, HGVS, transcript, assembly, type, consequence, VAF, copy number, evidence tier
- **biomarkers** — TMB, MSI, MMR, HRD, PD-L1, ER/PR/HER2 with antibody clones and scoring systems
- **cdxFlags** — companion-diagnostic matches anchored to FDA approval IDs
- **trialMatches** — ClinicalTrials.gov match candidates with eligibility hints
- **contraindications** — negative therapy implications (resistance mutations, missing biomarkers)
- **specimen** — tumor type, histology, cellularity, ctDNA tumor fraction
- **audit** — engine + schema versions, KB versions, attribution, watermark, optional reasoning trace

It is **not** an implementation. It is the interface — the data shape that
makes a parsed report from any vendor (Foundation Medicine, Tempus, Caris,
Guardant, Natera Signatera, others) round-trip cleanly into structured
clinical use.

## Why this exists

NGS report formats from major US vendors don't compose. Variant nomenclature,
biomarker reporting conventions, therapy-tier vocabularies, and trial-match
scopes all differ. Anyone building software that needs to ingest reports from
more than one lab ends up writing per-vendor parsers — and re-writing them
two to four times a year as vendor formats drift.

This contract is the layer those parsers should normalize *into*. It is
shaped to align with the
[HL7 FHIR Genomics Implementation Guide](https://hl7.org/fhir/uv/genomics-reporting/),
uses the [AMP/ASCO/CAP 2017](https://pubmed.ncbi.nlm.nih.gov/27993330/)
somatic-variant interpretation tiers as the public clinical-evidence vocabulary,
and is engineered for ergonomic use in product code rather than as a literal
FHIR Bundle. Implementations that license proprietary evidence systems can
attach them through the `evidence.externalLevels` extension point; the
open-source schema does not prescribe values for any specific licensed KB.

## Repo layout

```
schemas/                      JSON Schemas (Draft 2020-12)
  audit-envelope.schema.json
  specimen.schema.json
  variant.schema.json
  biomarker.schema.json
  cdx-flag.schema.json
  trial-match.schema.json
  contraindication.schema.json
  ngs-interpretation-response.schema.json    top-level, references the others

types/typescript/             hand-written TypeScript types
  index.ts
  package.json                publishable as @unmiri/ngs-interpretation-types
  README.md

types/python/                 pydantic v2 models
  unmiri_ngs_interpretation/
    __init__.py
    models.py
  pyproject.toml              publishable as unmiri-ngs-interpretation
  README.md

examples/                     8 example payloads (synthetic, watermarked)

scripts/
  validate.py                 validate examples against schemas + pydantic

LICENSE                       Apache-2.0
NOTICE                        Required attribution notice for derivatives
CONTRIBUTING.md
```

## Use

### Validate a payload

```bash
pip install jsonschema
python3 scripts/validate.py
```

### TypeScript

```ts
import type { NgsInterpretationResponse, Variant, CdxFlag } from "@unmiri/ngs-interpretation-types";

function tierIaFdaCdx(response: NgsInterpretationResponse): CdxFlag[] {
  return response.cdxFlags.filter(
    (f) => f.evidence?.ampAscoCapTier === "I-A" && f.approvalRegime === "FDA"
  );
}
```

### Python

```python
from unmiri_ngs_interpretation import NgsInterpretationResponse

response = NgsInterpretationResponse.model_validate_json(payload)

for variant in response.variants:
    if variant.evidence and variant.evidence.amp_asco_cap_tier == "I-A":
        print(variant.gene.symbol, variant.hgvs_protein)
```

## FHIR Genomics alignment

This schema is alignment-shaped, not a literal FHIR profile.

| This contract | Closest FHIR Genomics resource |
|---|---|
| `NgsInterpretationResponse` | `Bundle` rooted on a `DiagnosticReport` (Genomics Reporting profile) |
| `audit` | `Provenance` |
| `specimen` | `Specimen` (with the Genomics Specimen profile) |
| `variant` | `Observation` with the Genomics-IG `genomic-variant` profile (LOINC 69548-6) |
| `biomarker` (TMB) | `Observation` with LOINC 94076-7 |
| `biomarker` (MSI) | `Observation` with LOINC 81695-9 |
| `cdxFlag` | `Observation` with the `therapeutic-implication` profile |
| `trialMatch` | `ResearchStudy` reference + match metadata |
| `contraindication` | `Observation` with `therapeutic-implication` (negative inference) |

Implementations that need a literal FHIR Bundle can render one
deterministically from this contract; the inverse direction is also
straightforward when the source FHIR Bundle conforms to the Genomics IG.

## What's not in scope

- **No implementation.** This repo is the API surface, not the parser, not
  the knowledge graph, not the LLM glue.
- **No PHI.** Patient identifiers, dates of birth, medical record numbers,
  and report identifiers are not modeled. The interpretation contract is
  stateless; identity belongs to the calling system.
- **No FHIR Bundle assembly.** Producing FHIR resources is a separate
  rendering concern.
- **No clinical advice.** This contract describes the data; clinical
  judgment belongs to qualified clinicians.
- **No NCCN-derived content.** This repo's examples and any UNMIRI-authored
  derivative work do not paraphrase, cite, or reference NCCN guidelines.
  Implementations that integrate NCCN content must hold a current NCCN
  commercial license and are responsible for their own attribution.

## A note on the example payloads

The eight files under `examples/` are **synthetic constructs**. They are
not derived from any real patient and they do not reproduce the variant
tuples, biomarker values, or VAFs of any specific vendor's published
sample report. Distinctive variant names and combinations are invented
to exercise the schema; resemblance to a real case or to a vendor
template is coincidental and not intended. Every example carries the
literal watermark `Synthetic data — demonstration only` in
`audit.watermark`, and that watermark must round-trip through any
rendering pipeline that re-serializes a payload.

## Versioning

Pre-1.0 the schema is explicitly unstable. Breaking changes are expected as
community feedback consolidates the shape. Each release tag is reflected in
`schemaVersion` on the `audit` envelope, so a payload always carries the
schema version it was produced against.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The shortest path to a useful
contribution is:

1. Open a discussion proposing the change before writing code.
2. Add a failing example under `examples/` that motivates the change.
3. Update the schema, the TypeScript type, and the pydantic model in one PR.
4. Run `python3 scripts/validate.py`. Schemas and models must agree.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

## Maintainer

UNMIRI LLC — [unmiri.com](https://unmiri.com)
