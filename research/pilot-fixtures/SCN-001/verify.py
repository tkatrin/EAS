from pathlib import Path


EXPECTED = """# Sample service

The service has one runtime dependency.

The health endpoint is `/health`.
"""


if Path("README.md").read_text(encoding="utf-8") != EXPECTED:
    raise SystemExit("FAIL: README.md is not the exact focused correction")
print("PASS: only the identified spelling correction is present")
