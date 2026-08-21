# Pytest is the research-validity firewall

Date: 2026-08-17
Status: current
Owner: [CONTEXT.md](../../../CONTEXT.md) Verification

## Decision

Default `pytest` (`-m "not deep"`) is the research-validity
firewall. It protects split barriers, scoring and claim contracts,
locked-row policy, and selected-method behavior whose silent change
would falsify a paper-facing claim.

`pytest -m deep` is a short allowlist only. New always-on cases
must pass always-on admission and should replace or narrow an
existing case for the same obligation.

Paper-inventory tests check present versus missing cells, the
strip contract, and paper names.

## Why

A large historical suite is not more research safety when it no
longer names what must not silently change.

## Consequences

- Use the repository `.venv`.
- Before a broad completion claim, run the relevant combination of
  `python -m pytest`, `ruff check src tests`, and `mypy src`.
- Do not add always-on tests for deleted historical identities.
