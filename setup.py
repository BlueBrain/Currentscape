#!/usr/bin/env python

import imp
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

# read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    README = f.read()

VERSION = imp.load_source("", "currentscape/version.py").__version__

EXTRA_EXTRACT_CURRS = ["bluepyopt", "neuron"]

EXTRA_EXAMPLE = ["scipy"]

setup(
    name="currentscape",
    author="Aurelien Jaquier",
    author_email="aurelien.jaquier@epfl.ch",
    version=VERSION,
    description="Module to easily plot currentscape.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://bbpteam.epfl.ch/documentation/projects/currentscape",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/NSETM/issues",
        "Source": "ssh://bbpcode.epfl.ch/cells/currentscape",
    },
    license="BBP-internal-confidential",
    install_requires=[
        "numpy",
        "matplotlib",
        "palettable",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    extras_require={
        "docs": ["sphinx", "sphinx-bluebrain-theme"],
        "extract_currs": EXTRA_EXTRACT_CURRS,
        "example": EXTRA_EXAMPLE,
        "all": EXTRA_EXTRACT_CURRS + EXTRA_EXAMPLE,
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
