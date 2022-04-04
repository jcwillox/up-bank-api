from setuptools import find_packages, setup

PACKAGES = find_packages(exclude=["tests", "tests.*"])

REQUIRES = [
    "requests>=2.22.0,<3",
]

DOCS_REQUIRE = [
    "mkdocs-material>=8.2.8,<9",
    "mkdocstrings>=0.18.1",
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


if __name__ == "__main__":
    setup(
        packages=PACKAGES,
        install_requires=REQUIRES,
        tests_require=TESTS_REQUIRE,
        extras_require=EXTRAS_REQUIRE,
        python_requires=">=3.7",
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
