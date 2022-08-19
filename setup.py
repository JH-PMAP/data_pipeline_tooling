import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="data_pipeline_tooling",
    version="0.04",
    description="A library for databricks jobs api",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Eric Schles",
    author_email="eschles3@jh.edu",
    url="https://github.com/JH-PMAP/data_pipeline_tooling",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    packages=["data_pipeline_tooling"],
    include_package_data=True,
    install_requires=[
        "requests", "fire", "azure-storage-blob", "azure-storage-file-datalake", "azure-core"
    ],
    console_scripts=["scripts/orchestrator_cli"],
    scripts=["scripts/orchestrator_cli"],
)
