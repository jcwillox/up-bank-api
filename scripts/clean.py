import shutil
from glob import glob

shutil.rmtree("dist/", ignore_errors=True)
shutil.rmtree("build/", ignore_errors=True)
shutil.rmtree(".pytest_cache/", ignore_errors=True)

for path in glob("*.egg-info"):
    shutil.rmtree(path, ignore_errors=True)

for path in glob("**/__pycache__/", recursive=True):
    shutil.rmtree(path, ignore_errors=True)
