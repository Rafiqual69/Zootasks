# AI Provider Offer Change Detection

## Purpose

ZooTasks must not silently continue executing an offer when a provider changes a
material contract property. The change detector is deterministic and network-free:
provider adapters or ingestion code supply observations, and this module decides
whether the observed offer is unchanged or requires review.

## Material-change contract

Changes to any of these fields require review:

- provider identity/name
- authorization status/route/contract reference
- source kind/identifier
- regions, languages, or eligibility requirements
- task category
- reward amount, currency, or payment terms
- data sensitivity, retention, or processing restrictions
- qualification requirements/method
- verification method
- adapter identity/version

A display title change alone is not a material change.

## Fail-closed behavior

1. Both observations are validated and normalized through the canonical offer validator.
2. Material fields are compared in a fixed contract order.
3. No material difference produces `unchanged`.
4. Any material difference produces `review_required`.
5. Invalid observations are rejected rather than treated as safe.
6. Review/quarantine is required before an affected offer can become executable again.

This design supports continuous monitoring and change management without granting
the detector any network access, worker authority, or financial authority. NIST
AI RMF identifies ongoing monitoring, third-party resource monitoring, and change
management as lifecycle risk-management activities. See the NIST AI RMF Core and
post-deployment monitoring guidance.
