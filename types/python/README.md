# `unmiri-ngs-interpretation`

Pydantic v2 models for the UNMIRI NGS interpretation
API contract. Mirrors the JSON Schemas in
[`../../schemas/`](../../schemas).

## Install

```bash
pip install unmiri-ngs-interpretation
```

## Use

```python
from pathlib import Path
from unmiri_ngs_interpretation import NgsInterpretationResponse

raw = Path("response.json").read_text()
response = NgsInterpretationResponse.model_validate_json(raw)

for variant in response.variants:
    tier = variant.evidence.amp_asco_cap_tier if variant.evidence else None
    print(variant.gene.symbol, variant.hgvs_protein, tier)
```

Camel-case JSON wire format is preserved via `populate_by_name=True` is not
needed — every snake_case Python field carries a `Field(alias=...)` for the
camel-cased JSON name. To dump back to camel case:

```python
response.model_dump_json(by_alias=True, exclude_none=True)
```

## Versioning

Models track the JSON Schemas tag-for-tag. Pre-1.0 the schema is explicitly
unstable.

## License

Apache-2.0. See `../../LICENSE`.
