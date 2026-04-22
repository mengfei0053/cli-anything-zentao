"""Setup script for cli-anything-zentao.

PEP 420 namespace package under the shared cli_anything namespace.
"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-zentao",
    version="1.0.0",
    description="CLI interface for ZenTao project management system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="CLI-Anything Contributors",
    license="MIT",
    # PEP 420 namespace packages — find all packages under cli_anything.*
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0",
    ],
    extras_require={
        "repl": ["prompt_toolkit>=3.0"],
        "test": ["pytest>=7.0"],
        "dev": ["prompt_toolkit>=3.0", "pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-zentao=cli_anything.zentao.zentao_cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Project Management",
    ],
)
