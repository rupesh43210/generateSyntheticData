from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pii-generator",
    version="1.0.0",
    author="PII Generator Team",
    author_email="team@pii-generator.com",
    description="High-performance synthetic PII data generator for Azure SQL Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pii-generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pii-gen=pii_generator.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "pii_generator": ["data/*.json", "data/*.csv", "configs/*.yaml"],
    },
)