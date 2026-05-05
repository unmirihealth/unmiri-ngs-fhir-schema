# `@unmiri/ngs-interpretation-types`

TypeScript types for the UNMIRI NGS interpretation API.

These types are hand-written to mirror the JSON Schemas in
[`../../schemas/`](../../schemas). They are not auto-generated; identifiers
and JSDoc are tuned for ergonomic use in product code.

## Install

```bash
npm install @unmiri/ngs-interpretation-types
```

## Use

```ts
import type { NgsInterpretationResponse } from "@unmiri/ngs-interpretation-types";

async function interpret(reportPdf: Buffer): Promise<NgsInterpretationResponse> {
  const res = await fetch("https://api.unmiri.com/v1/ngs/interpret", {
    method: "POST",
    headers: { "Content-Type": "application/pdf" },
    body: reportPdf,
  });
  return res.json();
}
```

## Versioning

Types track the JSON Schemas tag-for-tag. Breaking changes bump the major
version. Pre-1.0 the schema is explicitly unstable and may break across
minor versions while community feedback consolidates the shape.

## License

Apache-2.0. See `../../LICENSE`.
