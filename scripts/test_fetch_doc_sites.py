"""Regression tests for complete, source-ordered Next.js sidebar inventories.

Run with: python3 -m unittest discover -s scripts -p 'test_fetch_doc_sites.py'
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_doc_sites as scraper


def flight_html(pages, extra_records=None, split_chunks=False):
    """Build real Flight-style records inside JSON-encoded Next push scripts."""
    tree = {"name": "Sea", "children": pages}
    records = {
        "a": ["$", "DocsLayout", None, {"tree": tree}],
        **(extra_records or {}),
    }
    payload = "".join(
        record_id + ":" + json.dumps(value, ensure_ascii=False) + "\n"
        for record_id, value in records.items()
    )
    chunks = [payload]
    if split_chunks:
        middle = len(payload) // 2
        chunks = [payload[:middle], payload[middle:]]
    return "<html>" + "".join(
        "<script>self.__next_f.push("
        + json.dumps([1, chunk], ensure_ascii=False, separators=(",", ":"))
        + ")</script>"
        for chunk in chunks
    ) + "</html>"


def page(name, url="/sea/need/example"):
    # The source need not serialize name immediately before url.
    return {"url": url, "type": "page", "external": False, "name": name}


def new_badge():
    return [
        "$",
        "span",
        "new-label-uuid",
        {"className": "rounded px-1 text-[10px]", "children": "New"},
    ]


class ExtractPageTreeTests(unittest.TestCase):
    def test_markdown_whitespace_preserves_hard_breaks_and_code(self):
        body = "第一行  \n第二行 \n# \n\n```text\ncode  \n```\n"
        expected = "第一行\\\n第二行\n#\n\n```text\ncode  \n```\n"
        for value in (body, body.replace("\n", "\r\n")):
            with self.subTest(line_endings=repr(value[:10])):
                self.assertEqual(scraper._normalize_sea_markdown(value), expected)

    def test_plain_titles_nested_order_and_source_filter(self):
        fixture = flight_html(
            [
                page("网站出海必读", "/sea/readme"),
                {
                    "type": "folder",
                    "name": "找需求",
                    "children": [
                        page("第二篇", "/sea/need/second"),
                        page("第一篇", "/sea/need/first"),
                        page("其他手册", "/joyflix/getting-started/readme"),
                    ],
                },
            ],
            split_chunks=True,
        )
        self.assertEqual(
            scraper.extract_page_tree(fixture, "sea"),
            [
                ("网站出海必读", "/sea/readme"),
                ("第二篇", "/sea/need/second"),
                ("第一篇", "/sea/need/first"),
            ],
        )

    def test_react_title_omits_new_and_hidden_badges(self):
        title = [
            "$",
            "span",
            None,
            {
                "children": [
                    "更新后的",
                    ["$", "strong", None, {"children": "完整标题"}],
                    new_badge(),
                    ["$", "span", None, {"aria-hidden": True, "children": "●"}],
                ]
            },
        ]
        self.assertEqual(
            scraper.extract_page_tree(flight_html([page(title)]), "sea"),
            [("更新后的完整标题", "/sea/need/example")],
        )

    def test_lazy_title_resolves_records_and_decodes_literal_dollar(self):
        fixture = flight_html(
            [page("$Lb")],
            extra_records={
                "b": [
                    "$",
                    "span",
                    None,
                    {"children": ["$$10k ", "$Lc", new_badge()]},
                ],
                "c": "MRR 的点子是怎么来的",
            },
        )
        self.assertEqual(
            scraper.extract_page_tree(fixture, "sea"),
            [("$10k MRR 的点子是怎么来的", "/sea/need/example")],
        )

    def test_missing_references_and_invalid_titles_fail_closed(self):
        invalid_names = ["$Lmissing", "", None, [], new_badge()]
        for name in invalid_names:
            with self.subTest(name=name):
                with self.assertRaises(RuntimeError):
                    scraper.extract_page_tree(flight_html([page(name)]), "sea")

    def test_missing_or_empty_source_tree_is_an_error(self):
        fixtures = [
            "<html>no Flight tree</html>",
            flight_html([]),
            flight_html([page("其他手册", "/joyflix/getting-started/readme")]),
        ]
        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                with self.assertRaises(RuntimeError):
                    scraper.extract_page_tree(fixture, "sea")


class HarvestPageTreeTests(unittest.TestCase):
    @patch.object(scraper.time, "sleep")
    @patch.object(scraper, "fetch_html")
    def test_stability_compares_titles_as_well_as_urls(self, fetch_html, sleep):
        before = flight_html([page("旧标题")])
        after = flight_html([page("新标题")])
        fetch_html.side_effect = [before, after, after]
        self.assertEqual(
            scraper.harvest_page_tree("sea"),
            [("新标题", "/sea/need/example")],
        )
        self.assertEqual(fetch_html.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        fetch_html.assert_called_with(scraper.BASE + "/sea")

    @patch.object(scraper.time, "sleep")
    @patch.object(scraper, "fetch_html")
    def test_four_inconsistent_inventories_never_return_largest_fallback(
        self, fetch_html, sleep
    ):
        fetch_html.side_effect = [
            flight_html([page("第一篇")]),
            flight_html([page("第一篇"), page("第二篇", "/sea/need/second")]),
            flight_html([page("已更新的第一篇")]),
            flight_html([page("仍在变化的第一篇")]),
        ]
        with self.assertRaises(RuntimeError):
            scraper.harvest_page_tree("sea")
        self.assertEqual(fetch_html.call_count, 4)
        self.assertEqual(sleep.call_count, 3)


if __name__ == "__main__":
    unittest.main()
