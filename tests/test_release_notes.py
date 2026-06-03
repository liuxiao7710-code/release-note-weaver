from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from release_note_weaver.cli import parse_commit, parse_commits, prepend_to_changelog, render_release_notes


class ReleaseNoteWeaverTests(unittest.TestCase):
    def test_parse_conventional_commit(self) -> None:
        commit = parse_commit("feat(cli): add json output")

        self.assertIsNotNone(commit)
        assert commit is not None
        self.assertEqual(commit.type, "feat")
        self.assertEqual(commit.scope, "cli")
        self.assertFalse(commit.breaking)

    def test_render_groups_breaking_changes(self) -> None:
        commits = parse_commits([
            "feat!: remove old config",
            "fix(parser): ignore blanks",
            "docs: update readme",
        ])

        notes = render_release_notes(commits, "0.2.0", "2026-06-03")

        self.assertIn("## 0.2.0 - 2026-06-03", notes)
        self.assertIn("### Breaking Changes", notes)
        self.assertIn("- remove old config", notes)
        self.assertIn("### Bug Fixes", notes)
        self.assertIn("- **parser:** ignore blanks", notes)

    def test_prepend_to_changelog(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            changelog = Path(temp_dir) / "CHANGELOG.md"
            changelog.write_text("# Changelog\n\n## 0.1.0 - 2026-01-01\n", encoding="utf-8")

            prepend_to_changelog(changelog, "## 0.2.0 - 2026-06-03\n")

            text = changelog.read_text(encoding="utf-8")
            self.assertLess(text.index("0.2.0"), text.index("0.1.0"))

    def test_cli_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            commits = Path(temp_dir) / "commits.txt"
            commits.write_text("feat: add thing\nfix: repair thing\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, "-m", "release_note_weaver", "--from-file", str(commits), "--version", "1.0.0", "--date", "2026-06-03"],
                cwd=Path(__file__).resolve().parents[1],
                env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("Features", completed.stdout)
            self.assertIn("Bug Fixes", completed.stdout)


if __name__ == "__main__":
    unittest.main()
