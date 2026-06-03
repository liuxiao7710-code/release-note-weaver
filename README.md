# release-note-weaver

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

Prepend the generated section to a changelog:

```bash
release-note-weaver --range v0.1.0..HEAD --version 0.2.0 --update CHANGELOG.md
```

## Development

```bash
python -m unittest discover -s tests
```

## License

MIT
