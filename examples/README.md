# Examples

Eight example payloads conforming to
[`schemas/ngs-interpretation-response.schema.json`](../schemas/ngs-interpretation-response.schema.json).

> **These examples are synthetic constructs.** They are not derived from
> any real patient. They do not reproduce variant tuples, biomarker
> values, or VAFs from any specific vendor's published sample report.
> Distinctive variant names and combinations are invented to exercise
> the schema; resemblance to a real case or vendor template is
> coincidental and not intended.

The eight examples cover the cancer types and finding patterns most
commonly encountered in cross-vendor NGS interpretation:

| File | Source vendor format | Tumor | Headline finding |
|---|---|---|---|
| `01-fmi-f1cdx-nsclc-egfr-l858r.json` | FoundationOne CDx | NSCLC | EGFR L858R → osimertinib CDx (1L); TMB low |
| `02-fmi-f1cdx-nsclc-met-exon14.json` | FoundationOne CDx | NSCLC | MET exon 14 splice + TP53 → capmatinib + tepotinib CDx |
| `03-fmi-f1cdx-nsclc-ntrk1-fusion.json` | FoundationOne CDx | NSCLC | NTRK1 fusion → larotrectinib + entrectinib (tumor-agnostic) |
| `04-fmi-f1lcdx-lung-erbb2-tp53.json` | FoundationOne Liquid CDx | NSCLC | ERBB2 G776delinsVC + TP53 R175H → trastuzumab deruxtecan |
| `05-tempus-xt-nsclc-kras-g12c.json` | Tempus xT | NSCLC | KRAS G12C + STK11 LOF co-mutation → sotorasib + adagrasib |
| `06-caris-endometrium-dmmr-msih.json` | Caris MI Profile | Endometrium | dMMR + MSI-H + TMB high → pembrolizumab |
| `07-caris-breast-tnbc-pdl1.json` | Caris MI Profile | Breast (TNBC) | PD-L1 SP142 IC 1% → sacituzumab govitecan; endocrine + anti-HER2 contraindications |
| `08-caris-breast-er-pr-tmb-pik3ca.json` | Caris MI Profile | Breast (HR+) | TMB-H pembrolizumab; PIK3CA M1043I → INAVO120 candidate |

**Every example carries the watermark
`Synthetic data — demonstration only` in `audit.watermark`.** The watermark
is required on any non-production payload. Do not remove it from these
files.

## Validation

The examples are tested against the schemas as part of CI. To re-run the
validation locally:

```bash
# Python (any version with jsonschema):
python3 -m pip install jsonschema
python3 -c "
import json, glob
from jsonschema import Draft202012Validator, RefResolver
schema = json.load(open('schemas/ngs-interpretation-response.schema.json'))
store = {json.load(open(p))['\$id']: json.load(open(p)) for p in glob.glob('schemas/*.json')}
resolver = RefResolver.from_schema(schema, store=store)
validator = Draft202012Validator(schema, resolver=resolver)
for ex in sorted(glob.glob('examples/*.json')):
    payload = json.load(open(ex))
    validator.validate(payload)
    print('ok:', ex)
"
```

## What's intentionally absent

These examples do not include patient identifiers, dates of birth,
medical record numbers, or report identifiers. The interpretation
contract is stateless; PHI is not part of the wire format.
