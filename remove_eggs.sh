rm -Rf data_pipeline_tooling.egg-info
rm -Rf build
rm -Rf dist
python -m pip uninstall -y data_pipeline_tooling

rm -Rf /Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/data_pipeline_tooling-0.11-py3.9.egg
rm -Rf /Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/data_pipeline_tooling-0.11-py3.10.egg
