# Notes for developers

## Setting up the python environment

It is recommended a new environment be set up for development. The easiest way
is using
[`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation)
or
[`mamba`](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html):

```
conda create -n classla python=3.13 -y
conda activate classla
```
This creates a new environment named `classla` with python3.13, pip, and some
other essentials, and activates it.


## Installing dev dependencies

Dev tools can be installed with the `[dev]` option:

```
git clone https://github.com/clarinsi/classla.git
cd classla
pip install -e .[dev]
```

This installs pytest (used for testing), build and twine (building and uploading
to pypi).

## Running tests

Invoke pytest in directory `tests_classla`:

```
cd tests_classla
pytest
```

Expected output looks something like this:

```
=============================================== test session starts ================================================
platform linux -- Python 3.13.3, pytest-8.3.5, pluggy-1.5.0
rootdir: /cache/peterr/classla
configfile: pyproject.toml
collected 33 items

test_downloads.py .                                                                                          [  3%]
test_lemmatizer.py .....                                                                                     [ 18%]
test_ner.py ..                                                                                               [ 24%]
test_parser.py ..                                                                                            [ 30%]
test_readme_examples.py ............                                                                         [ 66%]
test_slovenian_pipeline.py .....                                                                             [ 81%]
test_srl.py ..                                                                                               [ 87%]
test_tagger.py ..                                                                                            [ 93%]
test_tokenizer.py ..                                                                                         [100%]

================================================= warnings summary =================================================
tests_classla/test_ner.py::test_ner_trainer
  /home/peterr/mambaforge/envs/classla/lib/python3.13/site-packages/torch/optim/lr_scheduler.py:62: UserWarning: The
  verbose parameter is deprecated. Please use get_last_lr() to access the learning rate.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==================================== 33 passed, 1 warning in 676.20s (0:11:16) =====================================
```


## Bumping versions

When a new version is ready to be uploaded, the version in `classla/_version.py`
should be manually updated.

## Building

Test the validity of the package by running

```python -m build```

and check that the build succeeds and that the versions were propagated
correctly:

```
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling >= 0.8
* Getting build dependencies for sdist...
* Building sdist...
* Building wheel from sdist
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling >= 0.8
* Getting build dependencies for wheel...
* Building wheel...
Successfully built classla-2.2.1.tar.gz and classla-2.2.1-py3-none-any.whl
```
The built files reside in the `dist` directory. Ideally it will contain only the
currently relevant build files, if there are previous versions in it already,
delete them and rebuild.

## Uploading the new version to GitHub

Once the files test OK and build OK, we will push them on GH with a version tag:

```
git add ... # Add the files you want to commit
git commit
git tag -a "v2.1.1" # Tag the latest commit with the version
git push origin --tags
```

On GitHub, create a new release from the tag.

## Uploading the new version to pypi

After creating a new GitHub release, assert that you only have relevant build
files in dist/ directory. Then run

```
python3 -m twine upload dist/*
```
to upload the package to pypi. You will be prompted for an API token. Use the
token value, including the pypi- prefix.