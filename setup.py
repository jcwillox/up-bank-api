from setuptools import find_packages, setup

PACKAGE_NAME = "up-bank-api"
VERSION = "0.3.0"
PROJECT_URL = "https://github.com/jcwillox/up-bank-api"
PROJECT_AUTHOR = "Joshua Cowie-Willox"
DOWNLOAD_URL = f"{PROJECT_URL}/archive/{VERSION}.zip"
PACKAGES = find_packages()

with open("README.md", "r", encoding="UTF-8") as file:
    LONG_DESCRIPTION = file.read()

if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        url=PROJECT_URL,
        download_url=DOWNLOAD_URL,
        author=PROJECT_AUTHOR,
        author_email="",
        packages=PACKAGES,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        python_requires=">=3.7",
        install_requires=["requests>=2.14.0"],
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
