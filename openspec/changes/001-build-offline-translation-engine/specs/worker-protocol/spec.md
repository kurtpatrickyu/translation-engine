## Purpose

Provide external applications a stable local subprocess contract for translation, inspection, readiness, and orderly termination.

## ADDED Requirements

### Requirement: Versioned correlated UTF-8 framing
The worker SHALL read strict UTF-8 newline-delimited JSON objects on stdin and immediately flush exactly one response per processed request on stdout. Requests SHALL contain integer `protocol_version: 1`, a nonempty string `id` of at most 128 characters, and a supported `command`. Responses SHALL contain `protocol_version`, the request `id`, `ok`, and either `result` or `error` exclusively. An unparseable or invalid ID SHALL be represented by null in an error response. Requests SHALL be processed sequentially without unsolicited stdout messages.

#### Scenario: Repeated correlated requests
- **WHEN** multiple valid requests with different IDs are sent to one worker
- **THEN** each response echoes its ID in input order and is flushed without waiting for process exit

#### Scenario: Unicode round trip
- **WHEN** text contains Chinese, emoji, escaped newlines, or mixed scripts
- **THEN** framing and responses remain valid UTF-8 JSON without encoding loss

### Requirement: Bounded recoverable validation
The worker SHALL limit a request frame to 1,048,576 bytes excluding LF and an optional preceding CR, translation text to 65,536 UTF-8 bytes, and serialized response frames to 1,048,576 bytes. It SHALL reject invalid UTF-8, malformed JSON, duplicate object keys, non-object requests, invalid field types, unknown fields, unsupported versions, unsupported commands, and oversized input with structured errors. An oversized line SHALL be drained to its newline with bounded memory before reading another request; an unterminated partial frame at EOF SHALL receive an error if stdout is writable.

#### Scenario: Bad frame followed by valid frame
- **WHEN** malformed JSON or an oversized line precedes a valid health request
- **THEN** the worker emits an appropriate error and subsequently answers health without unbounded buffering

#### Scenario: Unsupported protocol
- **WHEN** a request uses an unsupported protocol version
- **THEN** the worker returns `UNSUPPORTED_PROTOCOL` using protocol v1 and preserves a valid ID

### Requirement: Commands and readiness
The worker SHALL support `translate` with `source`, `target`, and `text`, plus `health`, `info`, and `shutdown`. Health SHALL distinguish process liveness from translation readiness and report model/backend failures. Info SHALL report engine/runtime versions, protocol version, limits, configured pairs, and ready pairs. Translation SHALL reject unsupported pairs with `UNSUPPORTED_LANGUAGE` and unavailable or incompatible models with actionable structured errors.

#### Scenario: Missing model
- **WHEN** a worker starts with an empty configured model directory
- **THEN** health reports alive but not ready, info and shutdown remain usable, and translation returns `MODEL_MISSING`

### Requirement: Lifecycle and diagnostics
Stdout SHALL contain protocol responses only; logs, dependency output, warnings, and tracebacks SHALL go to stderr. Shutdown SHALL acknowledge then terminate with status zero without processing subsequent frames. Clean EOF SHALL terminate with status zero. Fatal startup configuration or unrecoverable process errors SHALL produce stderr diagnostics and nonzero exit status. Request-level errors SHALL NOT terminate a healthy worker.

#### Scenario: Graceful shutdown
- **WHEN** the worker receives shutdown after completing translations
- **THEN** it flushes the correlated acknowledgement, releases resources, and exits zero

#### Scenario: Dependency diagnostics
- **WHEN** a dependency emits diagnostics during initialization or translation
- **THEN** stdout remains parseable response-only JSON and diagnostics appear on stderr

### Requirement: Authoritative application-neutral consumer contract
The finalized versioned protocol reference SHALL be the authoritative contract for external consumers, documenting framing, fields, limits, errors, readiness, versioning, shutdown, and failure recovery consistently with this spec and conformance tests. The worker SHALL NOT introduce Freya-specific commands, paths, fields, or behavior to accommodate a future integration. Stdout purity SHALL be tested with actual dependencies; native redirection SHALL be introduced only when observed behavior or tests require it, without weakening response-only stdout acceptance.

#### Scenario: Future desktop integration
- **WHEN** a future Freya or other external application integrates with the worker
- **THEN** its integration follows the published protocol version in its own application without requiring consumer-specific worker behavior

#### Scenario: Logging configuration is sufficient
- **WHEN** real subprocess and packaged tests show response-only stdout using supported stderr logging configuration
- **THEN** no complex native stdout redirection is required and the same purity tests remain mandatory
