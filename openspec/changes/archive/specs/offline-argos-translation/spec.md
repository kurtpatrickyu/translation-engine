## REMOVED Requirements

### Requirement: Explicit package-local MiniSBD resources
**Reason**: The replacement candidate must operate without distributed AGPL sentence-boundary code or a separately provisioned ONNX detector.
**Migration**: Use the bounded local segmentation requirement below with the unchanged translation archive and a fresh versioned installation. Preserve the baseline worker, original ONNX and Level A evidence. This removal targets the corresponding requirement in change 001, which is not yet archived.

## MODIFIED Requirements

### Requirement: Revalidate approved runtime replacements

An approved Argos dependency/segmentation replacement SHALL revalidate the actual production provisioning and worker path using the unchanged Chinese-English translation archive hash. The candidate runtime environment and loaded modules SHALL contain no MiniSBD or other AGPL runtime component. Stanza/Torch SHALL remain absent; unused spaCy/Thinc frozen exclusions SHALL require source absence tests plus packaged validation. Source-level experiments SHALL NOT count as frozen or clean-machine acceptance. Prior runtime/model/ONNX results SHALL remain historical evidence rather than substitute for the replacement artifact's checks. The candidate SHALL reuse initialized translation/tokenizer/segmentation resources, retain direct Argos inference and preserve protocol v1, Unicode compatibility, offline behavior, integrity checks and graceful lifecycle handling.

#### Scenario: Approved segmentation candidate replaces the runtime artifact
- **WHEN** the explicitly identified patched Argos candidate is adopted after implementation authorization
- **THEN** local warm-up, repeated real zh-to-en translation, retained resources, representative quality checks, no-network-attempt instrumentation and stdout purity pass before reduced frozen dependency collection is accepted

#### Scenario: Replacement fails essential behavior
- **WHEN** the candidate loses critical translation content, violates source coverage, exceeds model limits unsafely or fails offline/packaged validation
- **THEN** migration acceptance fails with evidence and the retained baseline remains available without silently loading retired segmentation code in the candidate

## ADDED Requirements

### Requirement: Bounded local Chinese segmentation
The candidate SHALL segment Chinese and mixed Chinese-English text locally without a neural sentence-boundary asset or automatic downloads. It SHALL recognize sentence punctuation and paragraph boundaries, retain source punctuation and original Unicode substrings, and subdivide oversized input using the actual model tokenizer and inspected model/runtime capacity with special-token headroom. Each attempt SHALL submit every source span exactly once in original order without gaps or overlap. Segmentation SHALL NOT decode split token pieces back into source text. Empty text SHALL return an empty result. Per-request work and inference batch sizes SHALL remain bounded by the existing protocol limits and the reviewed model policy.

#### Scenario: Chinese sentences and product descriptions
- **WHEN** accepted text contains short/multiple sentences, quotes, Chinese punctuation, mixed English, names, decimals, versions or product identifiers
- **THEN** the source spans reconstruct the original paragraph exactly and are submitted in order without destructive punctuation or identifier normalization

#### Scenario: Single oversized sentence
- **WHEN** one sentence or unpunctuated string exceeds the approved source token budget, including inputs beyond the runtime's default truncation threshold
- **THEN** it is split into model-safe ordered source spans before inference and no suffix is silently discarded

#### Scenario: Paragraph and Unicode compatibility
- **WHEN** accepted input contains newlines, blank paragraphs, accented text, Chinese characters, combining sequences or emoji
- **THEN** the established paragraph behavior and Unicode transport/path compatibility remain valid and any neural-model content loss is distinguished from segmentation or transport loss

### Requirement: No successful silently truncated translation
The candidate SHALL enforce explicit source and generated-output bounds within the inspected model capacity. It SHALL detect generation-cap saturation, discard tentative output and retry only through bounded deterministic subdivision, or return the existing translation failure without partial successful output. It SHALL NOT use overlapping windows, reorder sentence results or append duplicated retry output. It SHALL preserve the same native translator and tokenizer across requests and retries.

#### Scenario: Decoder reaches its bound
- **WHEN** a translation hypothesis reaches the configured output cap
- **THEN** it is not returned as successful complete text; the request completes safely after bounded subdivision or fails with `TRANSLATION_FAILED`

#### Scenario: Indivisible input cannot fit
- **WHEN** a single indivisible source unit cannot meet model bounds or retries exhaust the finite subdivision policy
- **THEN** the worker returns `TRANSLATION_FAILED` without partial output, hangs or a protocol change

### Requirement: Paired translation quality acceptance
Before candidate adoption, the project SHALL compare the candidate with the retained approved MiniSBD worker on a fixed corpus covering short/multiple sentences, product names/descriptions, Chinese punctuation, mixed text, paragraphs, empty text, Unicode, repeated requests and long unpunctuated text. The exact greeting and empty-output baselines SHALL pass. Reviewed examples SHALL show no newly lost, duplicated or reordered sentences or critical factual fields. Every changed output SHALL have paired evidence and a documented semantic review. Model-quality limitations SHALL NOT be confused with source span correctness or erased from historical evidence.

#### Scenario: Boundary changes alter wording
- **WHEN** the candidate splits punctuation differently and changes English wording
- **THEN** the change is acceptable only if the paired review confirms retained propositions, critical numbers/names and sentence order without a new critical regression

#### Scenario: Repeated boilerplate conceals missing text
- **WHEN** long-input acceptance is exercised
- **THEN** distinct ordered head/middle/tail facts and source-token submission evidence supplement repeated-sentence tests so count-only checks cannot conceal lost text
