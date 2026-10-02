# Read-Only Provider Adapter Boundary

The provider adapter layer is intentionally split from authorization and financial
logic. In the current implementation it contains only a deterministic synthetic
CI adapter; there is no production network adapter.

## Safety properties

- provider registration must be independently verified and adapter-ready;
- synchronization has a bounded offer count;
- adapter identity/version must match the registry;
- adapter output is untrusted and is normalized by the canonical offer validator;
- normalization does not grant execution authority;
- adapters have no wallet, withdrawal, promotion, permission, or credential authority;
- future network adapters must remain behind an approved source allowlist and bounded
  timeout/retry/concurrency controls;
- provider or offer failures must fail closed into stale/failed/quarantined state.

This separation supports the NIST AI RMF emphasis on continuous monitoring and
third-party resource risk controls. citeturn0search6turn0search0
