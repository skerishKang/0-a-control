# scripts package scaffolds

This note records package scaffolds added before moving runtime files.

- `scripts/cli/`: future CLI entrypoint package.
- `scripts/queue_runtime/`: future queue runtime package. Do not use `scripts/queue/`, because it shadows Python's standard library `queue` module.
- `scripts/integrations/`: future external integration package.

These scaffolds contain no behavior changes.
