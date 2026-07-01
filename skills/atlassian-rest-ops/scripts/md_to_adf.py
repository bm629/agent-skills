#!/usr/bin/env python3
"""Convert Markdown to Atlassian Document Format (ADF).

Jira comment/description bodies are ADF (a JSON node tree), not Markdown — a raw
Markdown string renders its ``##`` / ``**`` / ``| |`` literally. Pipe your Markdown
through this to post it as a native ADF comment:

    python3 scripts/md_to_adf.py < comment.md            # -> ADF JSON on stdout
    ADF=$(python3 scripts/md_to_adf.py < comment.md)
    # then POST it as the comment body:
    #   {"body": <that ADF object>}   (Jira addComment / issue description)

Supports headings, paragraphs, bold, inline code, links, bullet/ordered lists,
fenced code blocks, and GFM tables. stdlib only — no dependency.
"""

import json
import re
import sys

_HEADING = re.compile(r"(#{1,6})\s+(.*)")
_BULLET = re.compile(r"\s*[-*]\s+")
_ORDERED = re.compile(r"\s*\d+\.\s+")
_INLINE = re.compile(r"(\*\*(.+?)\*\*)|(`([^`]+)`)|(\[([^\]]+)\]\(([^)]+)\))")


def md_to_adf(markdown):
    """Convert ``markdown`` (str) to an ADF ``doc`` node (dict)."""
    lines = markdown.splitlines()
    content = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.strip().startswith("```"):
            block, i = _take_code_block(lines, i)
            content.append(block)
        elif _is_table_row(line) and i + 1 < n and _is_delim_row(lines[i + 1]):
            block, i = _take_table(lines, i)
            content.append(block)
        elif _HEADING.fullmatch(line):
            m = _HEADING.fullmatch(line)
            content.append(
                {
                    "type": "heading",
                    "attrs": {"level": len(m.group(1))},
                    "content": _inline(m.group(2).strip()),
                }
            )
            i += 1
        elif _BULLET.match(line):
            block, i = _take_list(lines, i, _BULLET, "bulletList")
            content.append(block)
        elif _ORDERED.match(line):
            block, i = _take_list(lines, i, _ORDERED, "orderedList")
            content.append(block)
        else:
            block, i = _take_paragraph(lines, i)
            content.append(block)
    return {"version": 1, "type": "doc", "content": content}


def _starts_block(line):
    s = line.strip()
    return (
        not s
        or s.startswith("```")
        or bool(_HEADING.fullmatch(line))
        or bool(_BULLET.match(line))
        or bool(_ORDERED.match(line))
        or _is_table_row(line)
    )


def _take_paragraph(lines, i):
    buf = []
    while i < len(lines) and lines[i].strip() and not _starts_block(lines[i]):
        buf.append(lines[i].strip())
        i += 1
    return {"type": "paragraph", "content": _inline(" ".join(buf))}, i


def _take_code_block(lines, i):
    lang = lines[i].strip()[3:].strip()
    j, buf = i + 1, []
    while j < len(lines) and not lines[j].strip().startswith("```"):
        buf.append(lines[j])
        j += 1
    node = {"type": "codeBlock"}
    if lang:
        node["attrs"] = {"language": lang}
    text = "\n".join(buf)
    node["content"] = [{"type": "text", "text": text}] if text else []
    return node, j + 1


def _take_list(lines, i, marker, kind):
    items = []
    while i < len(lines) and marker.match(lines[i]):
        text = marker.sub("", lines[i], count=1)
        items.append(
            {"type": "listItem", "content": [{"type": "paragraph", "content": _inline(text)}]}
        )
        i += 1
    return {"type": kind, "content": items}, i


def _take_table(lines, i):
    header = _split_row(lines[i])
    rows, j = [], i + 2
    while j < len(lines) and _is_table_row(lines[j]):
        rows.append(_split_row(lines[j]))
        j += 1
    content = [_table_row(header, "tableHeader")]
    content += [_table_row(r, "tableCell") for r in rows]
    return {"type": "table", "content": content}, j


def _table_row(cells, cell_type):
    return {
        "type": "tableRow",
        "content": [
            {"type": cell_type, "content": [{"type": "paragraph", "content": _inline(c)}]}
            for c in cells
        ],
    }


def _is_table_row(line):
    return bool(re.fullmatch(r"\s*\|.*\|\s*", line))


def _is_delim_row(line):
    return bool(re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", line)) and "-" in line


def _split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _inline(text):
    nodes = []
    pos = 0
    for m in _INLINE.finditer(text):
        if m.start() > pos:
            nodes.append(_text(text[pos : m.start()]))
        if m.group(1):
            nodes.append(_text(m.group(2), [{"type": "strong"}]))
        elif m.group(3):
            nodes.append(_text(m.group(4), [{"type": "code"}]))
        else:
            nodes.append(_text(m.group(6), [{"type": "link", "attrs": {"href": m.group(7)}}]))
        pos = m.end()
    if pos < len(text):
        nodes.append(_text(text[pos:]))
    return [node for node in nodes if node["text"]]


def _text(value, marks=None):
    node = {"type": "text", "text": value}
    if marks:
        node["marks"] = marks
    return node


if __name__ == "__main__":
    print(json.dumps(md_to_adf(sys.stdin.read())))
