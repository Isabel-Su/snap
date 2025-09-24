"""
Setup configuration for pulse-mock package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pulse-mock",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for creating mock API clients using VCR cassettes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pulse-mock",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=5.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
    },
    keywords="mock api testing vcr cassettes development",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pulse-mock/issues",
        "Source": "https://github.com/yourusername/pulse-mock",
    },
)
