import json
import os

from setuptools import setup

REQUIRES = [
    "requests>=2.22.0,<3",
]

DOCS_REQUIRE = [
    "mkdocs-material>=8.5.3,<9",
    "mkdocstrings[python]>=0.18.1",
]

TESTS_REQUIRE = [
    "pytest>=7,<8",
    "pytest-asyncio>=0.18.3",
    "pytest-recording>=0.12.0",
    "PyYAML",
]

ASYNC_REQUIRE = [
    "aiohttp>=3.7.4,<4",
]

EXTRAS_REQUIRE = {
    "docs": DOCS_REQUIRE,
    "tests": TESTS_REQUIRE,
    "async": ASYNC_REQUIRE,
}

if os.path.exists("package-data.json"):
    with open("package-data.json") as file:
        data = json.loads(file.read())
else:
    data = {}

# we still specify requirements in here so PyCharm will pick them up.
if __name__ == "__main__":
    setup(install_requires=REQUIRES, extras_require=EXTRAS_REQUIRE, **data)
