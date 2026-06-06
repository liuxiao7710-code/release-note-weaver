# release-note-weaver

[![CI](https://github.com/liuxiao7710-code/release-note-weaver/actions/workflows/ci.yml/badge.svg)](https://github.com/liuxiao7710-code/release-note-weaver/actions/workflows/ci.yml)

`release-note-weaver` turns commit subjects into clean Markdown release notes. It is designed for small open source projects that want predictable changelogs without signing up for a hosted release service.

It understands Conventional Commit subjects such as:

```text
feat(cli): add json output
fix(parser): handle empty scopes
docs: refresh quickstart
feat!: drop Python 3.9 support
```

## Install

```bash
python -m pip install .
```

## Usage

Generate notes from a text file:

```bash
release-note-weaver --from-file examples/commits.txt --version 0.2.0
```

Generate notes from git:

```bash
release-note-weaver --range v0.1.0..HEAD --version 0.2.0
```

Exclude noisy commit types:

```bash
release-note-weaver --range v0.1.0..HEAD --version 0.2.0 --exclude-type chore
```

Prepend the generated section to a changelog:

```bash
release-note-weaver --range v0.1.0..HEAD --version 0.2.0 --update CHANGELOG.md
```

Example output from `examples/commits.txt`:

```markdown
## 0.2.0 - 2026-06-04

### Breaking Changes

- remove deprecated config format

### Features

- **cli:** add markdown output

### Bug Fixes

- **parser:** ignore blank commit lines

### Documentation

- add quickstart

### Maintenance

- update packaging metadata
```

## Maintenance roadmap

- Add release templates for compact and detailed changelog styles.
- Support optional commit hashes and contributor names.
- Add a GitHub Actions example that drafts a release body.
- Add more parser fixtures for non-Conventional Commit fallbacks.

## Development

```bash
python -m unittest discover -s tests
```

## License

MIT
