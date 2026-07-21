# Private data

Notes and IDs are private even when they contain no patient name. Notes leave
the process through `VLLM_BASE_URL`; confirm the endpoint, its logs, storage,
operators, and backups are approved before use.

Defaults: no prompt/response log, response cache, telemetry, remote error
reporting, console note text, credential display, or trace. Results and hidden
partial/resume files beside the chosen output contain private data. An explicit
trace contains the full prompt and response. Restrictive file permissions are
requested where the host supports them, but directory policy remains the
operator's responsibility.

Delete results, traces, and interrupted partial files according to the local
retention policy. Never send a real note, API key, full provider exception, or
private trace in a support request. Safe support material is limited to command
name, package/source-manifest hash, non-secret configuration, stable error code,
JSON mode, finish reason, and aggregate counts.

