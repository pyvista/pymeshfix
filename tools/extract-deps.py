"""Create a requirements_testing.txt file directly from a pyproject.toml."""

import tomli

data = tomli.load(open("pyproject.toml", "rb"))
deps = data["project"]["optional-dependencies"]["tests"]
with open("requirements-tests.txt", "w") as f:
    f.write("\n".join(deps))
