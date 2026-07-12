# EAS-011: Data Science and Machine-Learning Profile

## Status

EAS 0.1 Working Draft profile. This profile applies when a run creates,
selects, evaluates, or makes an evaluation claim about a statistical or
machine-learning model, dataset, split, metric, threshold, or experimental
result.

## Purpose

This profile prevents evaluation leakage, irreproducible experiments, and
claims that exceed the evidence produced by the experiment. It supplements the
core EAS requirements; it does not replace them.

## Requirements

- **EAS-011-R01**: Related observations MUST be partitioned across all
  documented entity, group, time-boundary, and causal dependencies, with any
  residual leakage risk recorded.
- **EAS-011-R02**: Test data MUST NOT be used to select features, models,
  preprocessing or imputation parameters, scaling, embeddings, hyperparameters,
  thresholds, stopping criteria, prompts, or reporting choices.
- **EAS-011-R03**: A run MUST record every partition actually used and label its
  role as training, validation, calibration, or final test.
- **EAS-011-R04**: Data exclusions, filtering, deduplication, relabeling, and
  missing-value handling MUST be recorded with their effect on sample counts.
- **EAS-011-R05**: Randomized operations MUST record the seed, algorithm or
  library version, and configuration needed for a reproducible rerun.
- **EAS-011-R06**: The primary metric and decision rule MUST be selected before
  inspecting final test results, with every post-hoc metric labeled
  exploratory.
- **EAS-011-R07**: An aggregate metric MUST NOT be the sole reported evidence
  when material class, subgroup, temporal, or cost asymmetry can change the
  engineering decision.
- **EAS-011-R08**: A run MUST inspect and report material class imbalance,
  subgroup coverage, and missing or sparse evaluation slices.
- **EAS-011-R09**: Training performance alone MUST NOT support a claim about
  validation, test, production, or generalization quality.
- **EAS-011-R10**: Synthetic-data results MUST be identified as synthetic and
  excluded from claims of real-world quality unless separate real-world
  evaluation supports those claims.
- **EAS-011-R11**: Experiment evidence MUST preserve dataset identity or a
  privacy-safe fingerprint, split metadata, model configuration, metric
  definitions, results, and known limitations.
- **EAS-011-R12**: A run MUST retain every attempt in its declared search or
  selection path, except attempts discarded by a pruning policy fixed before
  the search began.
- **EAS-011-R13**: Comparisons against a baseline MUST either use a compatible
  dataset, split, metric definition, and evaluation protocol or state why the
  comparison is not directly comparable.
- **EAS-011-R14**: A run SHOULD use ablation or another controlled comparison
  before attributing a multi-component result to an individual component.
- **EAS-011-R15**: Data-dependent preprocessing parameters MUST be fitted only
  on the partitions authorized for fitting and applied to evaluation partitions
  without refitting.
- **EAS-011-R16**: Before first access to final-test results, a run MUST create
  a timestamped immutable record of the selected model, primary metric, and
  decision rule.
- **EAS-011-R17**: A post-test selection change MUST be labeled exploratory or
  evaluated against a new untouched final-test set.

## Required evidence

At minimum, an applicable run records:

- dataset and partition metadata;
- preprocessing and filtering decisions;
- experiment configuration and reproducibility metadata;
- metric definitions and per-slice results where material;
- baseline identity and comparison protocol;
- negative, inconclusive, and exploratory results needed to interpret the
  conclusion.

Private or sensitive row-level data need not be copied into the run record.
Privacy-safe identifiers and externally retained artifacts may be referenced.
