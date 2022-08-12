import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="databricks_tooling",
    version="0.01",
    description="A library for databricks jobs api",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=["databricks_tooling"],
    include_package_data=True,
    install_requires=["requests", "fire"],
    console_scripts=["scripts/orchestrator_cli"],
    scripts=["scripts/orchestrator_cli"],
)
