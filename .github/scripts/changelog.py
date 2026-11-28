#!/usr/bin/env python3
"""Generate the changelog section of a chart release from conventional commits.

Usage: changelog.py <chart-dir> <version> [<ref>...]

Collects the non-merge commits since the previous release tag of the chart
(<chart>-<x.y.z>) that touch <chart-dir>, groups them by conventional commit
type and writes them into the section "## [<version>]" of
<chart-dir>/CHANGELOG.md, between the markers below. Text outside the markers
is kept, so manual notes in the section survive a regeneration.

Commits are taken from HEAD and from every additional <ref>. The release pull
requests use this module through release_pr.py.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

START = "<!-- generated:start -->"
END = "<!-- generated:end -->"

# (group title, predicate on (type, scope)) in output order
GROUPS = [
    ("Features", lambda t, s: t == "feat"),
    ("Bug Fixes", lambda t, s: t == "fix" and s != "deps"),
    ("Security", lambda t, s: t == "security"),
    ("Performance", lambda t, s: t == "perf"),
    ("Dependencies", lambda t, s: s == "deps"),
    ("Refactoring", lambda t, s: t == "refactor"),
    ("Documentation", lambda t, s: t == "docs"),
    ("CI", lambda t, s: t == "ci"),
    ("Build", lambda t, s: t == "build"),
    ("Tests", lambda t, s: t == "test"),
    ("Chores", lambda t, s: t in ("chore", "style", "revert")),
]
SUBJECT = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?: (?P<desc>.+)$")
# Renovate: "update <dep> docker tag to <version>" -> keep only the newest
# update per dependency and major line (e.g. pg16 and pg18 are kept apart)
DEP_UPDATE = re.compile(r"^(?P<dep>update .+?) to v?(?P<line>\D*\d+)\S*$")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def chart_name(chart_dir: Path) -> str:
    for line in (chart_dir / "Chart.yaml").read_text().splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    sys.exit(f"no name in {chart_dir}/Chart.yaml")


def version_key(v: str) -> tuple:
    return tuple(int(x) for x in v.split("."))


def previous_tag(name: str, version: str) -> str | None:
    # "tenant-*" also matches "tenant-access-*", so match the full pattern.
    pattern = re.compile(rf"^{re.escape(name)}-(\d+\.\d+\.\d+)$")
    versions = [m.group(1) for t in git("tag", "-l").split() if (m := pattern.match(t))]
    older = [v for v in versions if version_key(v) < version_key(version)]
    return f"{name}-{max(older, key=version_key)}" if older else None


def commits(chart_dir: Path, name: str, since: str | None, refs: list[str]) -> list[str]:
    revs = ["HEAD", *refs] + ([f"^{since}"] if since else [])
    subjects = git("log", "--no-merges", "--format=%s", *revs, "--", str(chart_dir)).splitlines()
    # Skip the release bump itself and changelog commits of this workflow.
    skip = re.compile(rf"^(chore|docs)(\({re.escape(name)}\))?: (release|update changelog)\b")
    return [s for s in subjects if s.strip() and not skip.match(s)]


def render(subjects: list[str], name: str) -> str:
    groups: dict[str, list[str]] = {}
    breaking: list[str] = []
    other: list[str] = []
    seen_deps: set[str] = set()
    for subject in subjects:  # newest first
        m = SUBJECT.match(subject)
        if not m:
            other.append(subject)
            continue
        ctype, scope, desc = m["type"], m["scope"] or "", m["desc"]
        if scope == "deps" and (d := DEP_UPDATE.match(desc)):
            key = (d["dep"], d["line"])
            if key in seen_deps:
                continue  # an older update of the same dependency and line
            seen_deps.add(key)
        entry = desc if scope in ("", name, "deps") else f"**{scope}:** {desc}"
        if m["bang"]:
            breaking.append(entry)
            continue
        title = next((g for g, pred in GROUPS if pred(ctype, scope)), None)
        if title is None:
            other.append(subject)
        else:
            groups.setdefault(title, []).append(entry)

    sections = []
    if breaking:
        sections.append(("Breaking Changes", breaking))
    sections += [(g, groups[g]) for g, _ in GROUPS if g in groups]
    if other:
        sections.append(("Other", other))
    body = "\n\n".join(f"### {t}\n\n" + "\n".join(f"- {e}" for e in items) for t, items in sections)
    return f"{START}\n{body}\n{END}" if body else f"{START}\n{END}"


def write(changelog: Path, version: str, block: str) -> None:
    text = changelog.read_text() if changelog.exists() else "# Changelog\n"
    lines = text.splitlines()
    heading = f"## [{version}]"
    if heading not in lines:
        # New section above the newest existing one (or at the end).
        first = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
        new = [heading, "", block, ""]
        lines = lines[:first] + new + lines[first:]
        if first == len(lines) - len(new) and lines[first - 1].strip():
            lines.insert(first, "")
    else:
        start = lines.index(heading)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        section = lines[start:end]
        if START in section and END in section:
            s, e = section.index(START), section.index(END)
            section = section[:s] + block.splitlines() + section[e + 1:]
        else:
            while section and not section[-1].strip():
                section.pop()
            section += ["", *block.splitlines(), ""]
        lines = lines[:start] + section + lines[end:]
    changelog.write_text("\n".join(lines).rstrip("\n") + "\n")


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    chart_dir, version, refs = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
    name = chart_name(chart_dir)
    since = previous_tag(name, version)
    subjects = commits(chart_dir, name, since, refs)
    print(f"{name} {version}: {len(subjects)} commit(s) since {since or 'the beginning'}", file=sys.stderr)
    write(chart_dir / "CHANGELOG.md", version, render(subjects, name))


if __name__ == "__main__":
    main()
