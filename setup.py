#!/usr/bin/env python

# Copyright 2023 Blue Brain Project / EPFL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 8):
    sys.exit("Sorry, Python < 3.8 is not supported")

# read the contents of the README file
with open("README.rst", encoding="utf-8") as f:
    README = f.read()

EXTRA_EXAMPLE = ["scipy", "bluepyopt", "emodelrunner>=1.1.5"]

setup(
    name="currentscape",
    author="Blue Brain Project, EPFL",
    use_scm_version={
        "version_scheme": "python-simplified-semver",
        "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
    description="Module to easily plot currentscape.",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/BlueBrain/Currentscape",
    project_urls={
        "Tracker": "https://github.com/BlueBrain/Currentscape",
        "Source": "https://github.com/BlueBrain/Currentscape",
    },
    license="Apache 2.0",
    install_requires=[
        "numpy",
        "matplotlib",
        "palettable",
    ],
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    extras_require={
        "docs": ["sphinx", "sphinx-bluebrain-theme"],
        "example": EXTRA_EXAMPLE,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
