from setuptools import find_packages, setup

PACKAGE_NAME = "up-bank-api"
VERSION = "0.1.0"
PROJECT_URL = "https://github.com/jcwillox/up-bank-api"
PROJECT_AUTHOR = "Joshua Cowie-Willox"
DOWNLOAD_URL = f"{PROJECT_URL}/archive/{VERSION}.zip"
PACKAGES = find_packages()

if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        url=PROJECT_URL,
        download_url=DOWNLOAD_URL,
        author=PROJECT_AUTHOR,
        packages=PACKAGES,
        python_requires=">=3.7",
        install_requires=["requests>=2.14.0"],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
