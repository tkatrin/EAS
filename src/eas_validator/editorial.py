"""Editorial checks for EAS normative Markdown specifications."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


_START = re.compile(r"^- \*\*(EAS-[0-9]{3}-R[0-9]{2})\*\*: (.*)$")
_NORMATIVE = re.compile(r"\b(MUST NOT|SHOULD NOT|MUST|SHOULD|MAY)\b")
_VAGUE = re.compile(
    r"\b(properly|adequately|reasonable|sufficient|appropriate(?:ly)?|significant|relevant)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RequirementText:
    identifier: str
    text: str
    path: Path
    line: int


@dataclass(frozen=True)
class EditorialIssue:
    identifier: str
    path: Path
    line: int
    kind: str
    message: str


def extract_requirements(paths: Iterable[Path]) -> list[RequirementText]:
    requirements: list[RequirementText] = []
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        current_id: str | None = None
        current_line = 0
        fragments: list[str] = []
        for line_number, line in enumerate(lines, start=1):
            match = _START.match(line)
            if match:
                if current_id is not None:
                    requirements.append(
                        RequirementText(current_id, " ".join(fragments), path, current_line)
                    )
                current_id = match.group(1)
                current_line = line_number
                fragments = [match.group(2).strip()]
            elif current_id is not None and (line.startswith("  ") or not line.strip()):
                if line.strip():
                    fragments.append(line.strip())
            elif current_id is not None:
                requirements.append(
                    RequirementText(current_id, " ".join(fragments), path, current_line)
                )
                current_id = None
                fragments = []
        if current_id is not None:
            requirements.append(
                RequirementText(current_id, " ".join(fragments), path, current_line)
            )
    return requirements


def review_requirements(requirements: Iterable[RequirementText]) -> list[EditorialIssue]:
    issues: list[EditorialIssue] = []
    seen: set[str] = set()
    for requirement in requirements:
        if requirement.identifier in seen:
            issues.append(
                EditorialIssue(
                    requirement.identifier,
                    requirement.path,
                    requirement.line,
                    "duplicate",
                    "requirement identifier is reused",
                )
            )
        seen.add(requirement.identifier)

        keywords = _NORMATIVE.findall(requirement.text)
        if not keywords:
            issues.append(
                EditorialIssue(
                    requirement.identifier,
                    requirement.path,
                    requirement.line,
                    "missing-keyword",
                    "normative clause has no BCP 14 keyword",
                )
            )
        if len(keywords) > 1:
            issues.append(
                EditorialIssue(
                    requirement.identifier,
                    requirement.path,
                    requirement.line,
                    "compound-obligation",
                    f"contains {len(keywords)} BCP 14 keywords",
                )
            )

        vague_terms = sorted({item.lower() for item in _VAGUE.findall(requirement.text)})
        if vague_terms:
            issues.append(
                EditorialIssue(
                    requirement.identifier,
                    requirement.path,
                    requirement.line,
                    "operational-definition",
                    f"review operational criteria for: {', '.join(vague_terms)}",
                )
            )
    return issues
