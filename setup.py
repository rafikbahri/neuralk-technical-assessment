#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for neuralk."""

import io
import os
import re

from setuptools import find_packages, setup

# Package meta-data
NAME = "neuralk"
DESCRIPTION = "A machine learning API service"
URL = "https://github.com/rafikbahri/neuralk-technical-assessment"
EMAIL = "team@neuralk.com"
AUTHOR = "Neuralk Team"
REQUIRES_PYTHON = ">=3.8.0"

def read_requirements():
    """Read the requirements file."""
    with open("requirements.txt", encoding="utf-8") as f:
        return [line.strip() for line in f if not line.startswith("#")]

REQUIRED = read_requirements()

EXTRAS = {
    "dev": [
        "black>=23.3.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
    ],
    "test": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
}

# Import the README and use it as the long-description
here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module
about = {}
try:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, "src", "__version__.py")) as f:
        exec(f.read(), about)
except FileNotFoundError:
    about["__version__"] = "0.1.0"

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
