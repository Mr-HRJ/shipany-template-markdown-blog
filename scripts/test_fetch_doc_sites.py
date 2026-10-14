"""Regression tests for complete, source-ordered Next.js sidebar inventories.

Run with: python3 -m unittest discover -s scripts -p 'test_fetch_doc_sites.py'
"""

import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_doc_sites as scraper
from page_order import PAGE_ORDER


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


class SeaCategoryMetadataTests(unittest.TestCase):
    def test_category_labels_match_source_order_catalog(self):
        self.assertEqual(
            [title for _, title in scraper.SEA_CATEGORY_MAP.values()],
            list(PAGE_ORDER),
        )


class SeaNewCategoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sea-new-category-test-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.docs = self.repo / "docs"
        self.categories = {
            "readme": ("must-read", "网站出海必读"),
            "seo": ("seo", "Seo"),
            "saas-seo": ("saas-seo", "AI 工具站 SEO 小册子"),
        }
        self.tree = [
            ("网站出海必读", "/sea/readme"),
            ("既有 SEO 文章", "/sea/seo/existing"),
            ("新增工具站文章", "/sea/saas-seo/new"),
        ]
        self.results = {
            url: {"body": f"{title}正文\n", "date": "2026-10-14", "updated": None}
            for title, url in self.tree
        }
        self.new_folder = self.docs / "saas-seo"
        for folder, title in list(self.categories.values())[:2]:
            directory = self.docs / folder
            directory.mkdir(parents=True)
            (directory / "meta.json").write_text(
                json.dumps({"title": title, "pages": ["stable-route"]}, ensure_ascii=False,
                           indent=2) + "\n",
                encoding="utf-8",
            )
        self.original_docs = {}
        for (title, url), folder in zip(self.tree, ("must-read", "seo")):
            result = self.results[url]
            path = self.docs / folder / "stable-route.md"
            text = scraper._render_sea_doc(title, result["date"], None, result["body"])
            path.write_text(text, encoding="utf-8")
            self.original_docs[path] = text
        (self.docs / "meta.json").write_text(
            json.dumps({"title": "AI 出海手册", "pages": ["must-read", "seo"]},
                       ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        for name, value in (
            ("REPO", self.repo), ("DOCS_ROOT", self.docs),
            ("SEA_CATEGORY_MAP", self.categories),
        ):
            self.patches.enter_context(patch.object(scraper, name, value))
        self.patches.enter_context(patch.object(scraper, "harvest_page_tree", return_value=self.tree))
        self.patches.enter_context(patch.object(scraper, "_load_r2_compare_config", return_value=None))

    def test_missing_new_category_is_created_only_after_all_fetches(self):
        def fetch(item):
            self.assertFalse(self.new_folder.exists())
            return self.results[item["source_path"]]

        with patch.object(scraper, "_fetch_sea_article", side_effect=fetch) as fetch_article:
            scraper.process_sea()
        self.assertEqual(fetch_article.call_count, len(self.tree))
        new_doc = self.new_folder / "新增工具站文章.md"
        self.assertEqual(
            new_doc.read_text(encoding="utf-8"),
            scraper._render_sea_doc("新增工具站文章", "2026-10-14", None, "新增工具站文章正文\n"),
        )
        self.assertEqual(
            json.loads((self.new_folder / "meta.json").read_text(encoding="utf-8")),
            {"title": "AI 工具站 SEO 小册子", "pages": ["新增工具站文章"]},
        )
        self.assertEqual(
            json.loads((self.docs / "meta.json").read_text(encoding="utf-8"))["pages"],
            ["must-read", "seo", "saas-seo"],
        )
        for path, original in self.original_docs.items():
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(path.parent.glob("*.md")), [path])

    def test_source_failure_does_not_create_new_category_or_change_existing_files(self):
        before = {path: path.read_bytes() for path in self.docs.rglob("*") if path.is_file()}

        def fetch(item):
            if item["source_path"] == "/sea/saas-seo/new":
                raise RuntimeError("new source page unavailable")
            return self.results[item["source_path"]]

        with patch.object(scraper, "_fetch_sea_article", side_effect=fetch), \
                patch.object(Path, "mkdir") as mkdir, \
                patch.object(Path, "write_text") as write_text, \
                patch.object(Path, "unlink") as unlink:
            with self.assertRaisesRegex(RuntimeError, "new source page unavailable"):
                scraper.process_sea()
        mkdir.assert_not_called()
        write_text.assert_not_called()
        unlink.assert_not_called()
        self.assertFalse(self.new_folder.exists())
        self.assertEqual(
            {path: path.read_bytes() for path in self.docs.rglob("*") if path.is_file()},
            before,
        )

    def test_other_directory_errors_are_not_treated_as_empty(self):
        original_iterdir = Path.iterdir

        def iterdir(path):
            if path == self.new_folder:
                raise PermissionError("category directory inaccessible")
            return original_iterdir(path)

        with patch.object(Path, "iterdir", iterdir), \
                patch.object(scraper, "_fetch_sea_article") as fetch_article:
            with self.assertRaisesRegex(PermissionError, "category directory inaccessible"):
                scraper.process_sea()
        fetch_article.assert_not_called()
        self.assertFalse(self.new_folder.exists())


class SeaInternalLinkTests(unittest.TestCase):
    def test_legacy_payment_link_resolves_to_existing_handbook(self):
        target = "/docs/shipany-two/payment/how-china-person-pay"
        cases = {
            "[payment](/payment/how-china-person-pay)": f"[payment]({target})",
            "[payment](/payment/how-china-person-pay#shop)": f"[payment]({target}#shop)",
            f'<a href="{scraper.BASE}/payment/how-china-person-pay">pay</a>':
                f'<a href="{target}">pay</a>',
            "[other](/payment/how-china-person-pay-other)":
                "[other](/payment/how-china-person-pay-other)",
            "[external](https://example.com/payment/how-china-person-pay)":
                "[external](https://example.com/payment/how-china-person-pay)",
        }
        for original, expected in cases.items():
            with self.subTest(original=original):
                self.assertEqual(scraper._rewrite_sea_internal_links(original, {}), expected)


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
