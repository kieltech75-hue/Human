#!/usr/bin/env python3
"""
Setup configuration for Human Programming Language.
Install with: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


def read_version():
    here = Path(__file__).parent
    init = here / "human_language" / "__init__.py"
    text = init.read_text(encoding="utf-8")
    m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if not m:
        raise RuntimeError("Unable to find version in human_language/__init__.py")
    return m.group(1)

setup(
    name="human-language",
    version=read_version(),
    author="KielTech",
    author_email="info@kieltech.com",
    description="A custom programming language with plain English syntax",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kieltech75-hue/Human",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "human=human_language.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "human_language": ["*.py", "README.md", "LICENSE"],
    },
)
