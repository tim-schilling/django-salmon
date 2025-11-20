# Contributing

This defines the standards for contributing to the project.

## Contributing code

This project enforces several style guidelines via [pre-commit](https://pre-commit.com/#installation) which will need to be installed.

```bash
pre-commit install
```

### Utilizing LLM/AI in project code

LLM/AI generated code is accepted as long as it's been reviewed and vetted. It should be noted in the commit message with a ``Co-Authored-By`` attribution.

## Running the tests

The tests can be run using tox:

```bash
uv run tox -e py312-django52
```

To see all environments, run:

```bash
uv run tox -l
```

## Running the example app

There is an example app that can be run to experiment with the project:

```bash
uv run python example_project/manage.py runserver --settings example.settings
```
