## clean up
pip uninstall -y data_pipeline_tooling
rm -rf dist/*.whl

## build and install in local environment
python -m build --wheel
pip install dist/*.whl
