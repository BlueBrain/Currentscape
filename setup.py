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
    install_requires=["numpy", "matplotlib", "scipy"],
    packages=find_packages(),
    python_requires=">=3.6",
    extras_require={"docs": ["sphinx", "sphinx-bluebrain-theme"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
