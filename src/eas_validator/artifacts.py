"""Integrity checks for external artifacts used by behavioral assessment."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ArtifactIssue:
    """One artifact-bundle integrity or coverage failure."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def validate_artifact_files(
    bundle: Any,
    bundle_directory: Path,
    *,
    expected_run_id: str | None = None,
    required_kinds: Iterable[str] = (),
) -> list[ArtifactIssue]:
    """Validate local paths, hashes, sizes, run binding, and kind coverage.

    JSON Schema validation is a separate Level 1 operation. These checks prove
    that the declared bytes are present and unchanged; they do not establish
    that an artifact is authentic or semantically supports a report claim.
    """

    if not isinstance(bundle, dict):
        return [ArtifactIssue("$artifacts", "bundle must be an object")]

    issues: list[ArtifactIssue] = []
    if expected_run_id is not None and bundle.get("run_id") != expected_run_id:
        issues.append(
            ArtifactIssue(
                "$artifacts.run_id",
                f"must equal source run_id {expected_run_id!r}",
            )
        )

    artifacts = bundle.get("artifacts")
    if not isinstance(artifacts, list):
        return issues + [ArtifactIssue("$artifacts.artifacts", "must be an array")]

    root = bundle_directory.resolve()
    identifiers: set[str] = set()
    observed_kinds: set[str] = set()
    for index, artifact in enumerate(artifacts):
        path = f"$artifacts.artifacts[{index}]"
        if not isinstance(artifact, dict):
            issues.append(ArtifactIssue(path, "must be an object"))
            continue

        identifier = artifact.get("id")
        if isinstance(identifier, str):
            if identifier in identifiers:
                issues.append(ArtifactIssue(f"{path}.id", f"duplicate id {identifier!r}"))
            identifiers.add(identifier)

        kind = artifact.get("kind")
        if isinstance(kind, str):
            observed_kinds.add(kind)

        relative = artifact.get("path")
        if not isinstance(relative, str):
            continue
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            issues.append(ArtifactIssue(f"{path}.path", "must remain inside bundle directory"))
            continue
        if not candidate.is_file():
            issues.append(ArtifactIssue(f"{path}.path", f"file does not exist: {relative}"))
            continue

        content = candidate.read_bytes()
        expected_size = artifact.get("byte_length")
        if isinstance(expected_size, int) and not isinstance(expected_size, bool):
            if len(content) != expected_size:
                issues.append(
                    ArtifactIssue(
                        f"{path}.byte_length",
                        f"declares {expected_size}, observed {len(content)}",
                    )
                )
        expected_digest = artifact.get("sha256")
        if isinstance(expected_digest, str):
            observed_digest = hashlib.sha256(content).hexdigest()
            if observed_digest != expected_digest:
                issues.append(
                    ArtifactIssue(
                        f"{path}.sha256",
                        f"declared digest does not match {relative}",
                    )
                )

    for kind in sorted(set(required_kinds) - observed_kinds):
        issues.append(
            ArtifactIssue(
                "$artifacts.artifacts",
                f"required artifact kind {kind!r} is absent",
            )
        )
    return issues
