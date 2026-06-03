# Contributing

Thanks for helping improve `release-note-weaver`.

## Local setup

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## Good first contributions

- Add output templates for different changelog styles.
- Support more commit metadata.
- Improve git range handling.
- Add fixtures from real release workflows.

## Pull request checklist

- Keep generated notes stable and easy to diff.
- Add tests for parser and rendering changes.
- Update examples when CLI behavior changes.
- Avoid adding hosted-service dependencies.
