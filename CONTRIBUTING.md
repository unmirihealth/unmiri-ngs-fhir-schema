# Contributing

Thanks for considering a contribution. This repo is a public artifact —
schema decisions affect anyone who relies on the contract — so the bar for
changes is deliberately a bit higher than a typical open-source project.

## Before you start

1. **Open a discussion first.** Use GitHub Discussions or open an Issue
   describing the change and the use case it unblocks. Schema changes that
   land without prior discussion are likely to be reverted, not because they
   are bad ideas but because the contract has many downstream consumers who
   need a chance to weigh in.
2. **Read the FHIR Genomics IG.** This contract is shaped to align with the
   FHIR R5 Genomics IG. Proposed additions should map cleanly to a FHIR
   Observation profile, MolecularSequence, or Provenance representation, or
   they should explain why the FHIR mapping breaks down.
3. **Read AMP/ASCO/CAP 2017.** This is the public, citable academic evidence
   tier the contract carries. Contributions that introduce a new evidence
   axis need to explain how it composes with AMP/ASCO/CAP, and proprietary
   level systems should be wired in through `evidence.externalLevels`
   (keyed by knowledge-base name) rather than added to the closed contract.

## What kinds of changes are welcome

- **Real-world vendor-format quirks** that the current contract cannot
  represent. Open an Issue with a sample (synthetic, redacted) report and
  the field that does not round-trip.
- **Additional biomarker types** with stable LOINC coding, when the absence
  is blocking a real implementation.
- **New `enum` values** in closed value sets — but only when the missing
  value is a real-world report value not derivable from the existing set.
- **Documentation improvements** — descriptions, examples, alignment notes.
- **Validation tooling improvements** — more thorough validators, conformance
  test suites, fixtures.

## What kinds of changes are **not** welcome

- **Adding patient identifiers, dates of birth, or PHI fields.** The interpretation contract is
  a stateless interpretation contract. Identity belongs to the calling
  system, under its own privacy controls.
- **Adding licensed third-party content** (NCCN, OncoKB, COSMIC, etc.) to
  schemas, descriptions, or examples. This repo treats those as third-party
  datasets that downstream consumers integrate themselves under their own
  licensing terms. Examples and descriptions in the open contract must
  reference only public sources: FDA labels, ClinVar, ClinicalTrials.gov,
  openFDA, peer-reviewed publications. Proprietary level systems plug in
  via `evidence.externalLevels`, not into the schema's enum.
- **Loosening required fields in `audit`.** Provenance is load-bearing for
  clinical reproducibility. The watermark, response ID, engine version,
  schema version, vendor source, and knowledge-base list are not negotiable.
- **Removing the synthetic-data watermark from any example.** The exact
  string `Synthetic data — demonstration only` is required on every example.

## How to make a change

Schemas, TypeScript types, and pydantic models must all stay in sync. A PR
that touches one but not the others will not pass review.

1. Fork and branch. Keep the branch focused on a single change.
2. Edit the schema(s) under `schemas/`.
3. Mirror the change in `types/typescript/index.ts`.
4. Mirror the change in `types/python/unmiri_ngs_interpretation/models.py`.
5. Add or update an example under `examples/` that exercises the new shape.
6. Update the table in `examples/README.md`.
7. Run the validator:
   ```bash
   python3 -m pip install jsonschema pydantic
   python3 scripts/validate.py
   ```
8. Update `CHANGELOG.md` (create one if not present) with a one-line summary.
9. Open a PR. Reference the discussion or issue that motivated the change.

## Style

- **JSON Schema.** Use Draft 2020-12. Set `additionalProperties: false` on
  every object schema. Use `$id` URLs under
  `https://schemas.unmiri.com/ngs-interpretation/v0/`. Cross-reference via `$ref`. Every
  property gets a `description`.
- **TypeScript.** Hand-written. Prefer `Literal` unions over enums. Mark
  optional fields with `?:` and `| null` only when the JSON Schema permits
  null. JSDoc each non-trivial field; keep wording aligned with the schema
  description.
- **Python.** pydantic v2. Use `Literal` types over `Enum`. Snake-case field
  names with camel-case `Field(alias=...)`. Use `model_config =
  ConfigDict(extra="forbid")`. Round-trip behavior with `by_alias=True` is
  part of the contract — preserve it.

## Sign-off

We use the
[Developer Certificate of Origin](https://developercertificate.org/). Sign
your commits:

```bash
git commit -s -m "your message"
```

By signing, you certify that you have the right to submit the change under
the project's open-source license.

## License

Contributions are licensed under Apache-2.0 (see `LICENSE`). By submitting a
contribution, you agree it can be redistributed under those terms.
