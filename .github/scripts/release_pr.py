#!/usr/bin/env python3
"""Prepare the release pull request of a chart in the current checkout of main.

Usage: release_pr.py <chart-dir> <body-file> [<release-branch-ref>]

Looks at the commits since the release of the version in <chart-dir>/Chart.yaml
that touch the chart. If there are any, it sets the next version in Chart.yaml,
writes its changelog section, writes the pull request body to <body-file> and
prints the version. If there are none, it prints nothing.

The next version follows the commit types: breaking changes (`type!:`) bump the
major version (the minor version before 1.0.0), `feat` bumps the minor version
and everything else the patch version.

<release-branch-ref> is the existing release branch. Two manual edits made
there are kept:
- a higher `version` in Chart.yaml (e.g. to release a major version by hand)
- notes in the changelog section outside the generated block

Exits with 3 if the current version has no tag yet (its release is pending or
failed), so the release pull request is left alone.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from changelog import END, START, SUBJECT, chart_name, commits, render, version_key, write  # noqa: E402

VERSION_LINE = re.compile(r"^version:[ \t]*['\"]?([^'\"\s]+)['\"]?[ \t]*$", re.M)


def chart_version(chart_yaml: str) -> str:
    m = VERSION_LINE.search(chart_yaml)
    if not m:
        sys.exit("no version in Chart.yaml")
    return m.group(1)


def tag_exists(tag: str) -> bool:
    return subprocess.run(["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"], capture_output=True).returncode == 0


def show(ref: str, path: Path) -> str | None:
    result = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def next_version(version: str, subjects: list[str]) -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    matches = [m for s in subjects if (m := SUBJECT.match(s))]
    if any(m["bang"] for m in matches):
        return f"{major}.{minor + 1}.0" if major == 0 else f"{major + 1}.0.0"
    if any(m["type"] == "feat" for m in matches):
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def section(changelog: str, version: str) -> list[str]:
    lines = changelog.splitlines()
    heading = f"## [{version}]"
    if heading not in lines:
        return []
    start = lines.index(heading) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def strip_blank(lines: list[str]) -> list[str]:
    text = "\n".join(lines).strip("\n")
    return text.splitlines() if text.strip() else []


def manual_notes(changelog: str | None, version: str) -> tuple[list[str], list[str]]:
    """Notes above and below the generated block of a changelog section."""
    lines = section(changelog or "", version)
    if START not in lines or END not in lines:
        return [], []
    s, e = lines.index(START), lines.index(END)
    return strip_blank(lines[:s]), strip_blank(lines[e + 1:])


def main() -> None:
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    chart_dir, body_file = Path(sys.argv[1]), Path(sys.argv[2])
    branch = sys.argv[3] if len(sys.argv) == 4 else None
    chart_yaml_path, changelog_path = chart_dir / "Chart.yaml", chart_dir / "CHANGELOG.md"

    name = chart_name(chart_dir)
    chart_yaml = chart_yaml_path.read_text()
    current = chart_version(chart_yaml)
    tag = f"{name}-{current}"
    if not tag_exists(tag):
        print(f"{tag} is not released yet, leaving the release pull request alone", file=sys.stderr)
        sys.exit(3)

    subjects = commits(chart_dir, name, tag, [])
    if not subjects:
        print(f"{name}: nothing to release since {tag}", file=sys.stderr)
        return

    version = next_version(current, subjects)
    branch_changelog = None
    if branch:
        branch_version = chart_version(show(branch, chart_yaml_path) or chart_yaml)
        if version_key(branch_version) > version_key(version):
            version = branch_version  # bumped by hand in the release pull request
        branch_changelog = show(branch, changelog_path)
        notes = manual_notes(branch_changelog, branch_version)
    else:
        notes = ([], [])
    if tag_exists(f"{name}-{version}"):
        sys.exit(f"{name}-{version} is already released, but Chart.yaml says {current}")

    chart_yaml_path.write_text(VERSION_LINE.sub(f"version: {version}", chart_yaml, count=1))
    before, after = notes
    block = render(subjects, name)
    write(changelog_path, version, "\n\n".join("\n".join(p) for p in (before, [block], after) if p))

    notes_text = "\n".join(strip_blank([l for l in section(changelog_path.read_text(), version) if l not in (START, END)]))
    body_file.write_text(
        f"Merging this pull request releases **{name} {version}** "
        f"({len(subjects)} change(s) since `{tag}`).\n\n"
        "It is rebuilt from `main` on every push, so it always lists everything that is not released yet. "
        "Edits that are kept:\n"
        f"- a higher `version` in `{chart_yaml_path}`\n"
        f"- notes in `{changelog_path}` above `{START}` or below `{END}`\n\n"
        f"---\n\n{notes_text}\n"
    )
    print(f"{name} {current} -> {version}: {len(subjects)} commit(s)", file=sys.stderr)
    print(version)


if __name__ == "__main__":
    main()
