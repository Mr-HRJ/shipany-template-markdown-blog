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
    def test_heading_link_sanitizer_preserves_body_links_and_fenced_examples(self):
        body = (
            "## [工具指南](https://example.com/guide) https://example.com/tool\n"
            "正文 [保留链接](https://example.com/body) https://example.com/plain\n"
            "```markdown\n# [代码内链接](https://example.com/code)  \n```\n"
            "~~~text\n## https://example.com/tilde\n~~~\n"
            "### 已处理 `https://example.com/already`\n"
        )
        expected = (
            "## 工具指南 `https://example.com/tool`\n"
            "正文 [保留链接](https://example.com/body) https://example.com/plain\n"
            "```markdown\n# [代码内链接](https://example.com/code)  \n```\n"
            "~~~text\n## https://example.com/tilde\n~~~\n"
            "### 已处理 `https://example.com/already`\n"
        )
        self.assertEqual(scraper._normalize_sea_markdown(body), expected)
        self.assertEqual(scraper._normalize_sea_markdown(expected), expected)

    def test_url_hard_breaks_use_explicit_autolinks_without_changing_code(self):
        body = (
            "   https://example.com/tool?a=1&b=2  \n说明\n"
            "<https://example.com/already-linked>  \n"
            "- [显式链接](https://example.com/existing)  \n"
            "```text\nhttps://example.com/code  \n```\n"
        )
        expected = (
            "   <https://example.com/tool?a=1&b=2>\\\n说明\n"
            "<https://example.com/already-linked>\\\n"
            "- [显式链接](https://example.com/existing)\\\n"
            "```text\nhttps://example.com/code  \n```\n"
        )
        for value in (body, body.replace("\n", "\r\n")):
            with self.subTest(line_endings=repr(value[:20])):
                normalized = scraper._normalize_sea_markdown(value)
                self.assertEqual(normalized, expected)
                self.assertEqual(scraper._normalize_sea_markdown(normalized), expected)

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


class SeaPinnedRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sea-pinned-route-test-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.docs = self.repo / "docs"
        self.title = "GEO：AI 搜索时代的新流量入口"
        self.old_url = "/sea/geo/old-article"
        self.new_url = "/sea/geo/new-article"
        self.old_path = self.docs / "geo" / "legacy-route.md"
        self.new_path = self.docs / "geo" / "geo-ai-search-door.md"
        self.categories = {
            "readme": ("must-read", "网站出海必读"),
            "geo": ("geo", "GEO"),
        }
        self.overrides = {
            self.old_url: "geo/legacy-route.md",
            self.new_url: "geo/geo-ai-search-door.md",
        }
        self.tree = [
            ("网站出海必读", "/sea/readme"),
            (self.title, self.old_url),
            (self.title, self.new_url),
        ]
        self.results = {
            "/sea/readme": {
                "body": "完整手册说明\n", "date": "2026-04-01", "updated": None,
            },
            self.old_url: {
                "body": "旧文章独立正文，保留已有路由。\n",
                "date": "2026-04-05", "updated": None,
            },
            self.new_url: {
                "body": f"新文章不同正文。[旧文章]({self.old_url})\n",
                "date": "2026-10-22", "updated": "2026-10-23",
            },
        }
        for folder, title in self.categories.values():
            directory = self.docs / folder
            directory.mkdir(parents=True)
            pages = ["readme"] if folder == "must-read" else [self.old_path.stem]
            (directory / "meta.json").write_text(
                json.dumps({"title": title, "pages": pages}, ensure_ascii=False,
                           indent=2) + "\n", encoding="utf-8",
            )
        self.old_text = self._render(self.title, self.old_url)
        self.old_path.write_text(self.old_text, encoding="utf-8")
        (self.docs / "must-read" / "readme.md").write_text(
            self._render("网站出海必读", "/sea/readme"), encoding="utf-8",
        )
        (self.docs / "meta.json").write_text(
            json.dumps({"title": "AI 出海手册", "pages": ["must-read", "geo"]},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        self.other_manual = self.docs / "unrelated-handbook" / "keep.mdx"
        self.other_manual.parent.mkdir()
        self.other_manual.write_text("---\ntitle: '无关手册'\n---\n保留内容\n", encoding="utf-8")
        self.other_text = self.other_manual.read_bytes()
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        for name, value in (
            ("REPO", self.repo), ("DOCS_ROOT", self.docs),
            ("SEA_CATEGORY_MAP", self.categories), ("SEA_ROUTE_OVERRIDES", self.overrides),
        ):
            self.patches.enter_context(patch.object(scraper, name, value))
        self.patches.enter_context(patch.object(scraper, "harvest_page_tree", return_value=self.tree))
        self.patches.enter_context(patch.object(scraper, "_load_r2_compare_config", return_value=None))

    def _render(self, title, url):
        result = self.results[url]
        return scraper._render_sea_doc(
            title, result["date"], result["updated"], result["body"],
        )

    def _snapshot(self):
        return {path: path.read_bytes() for path in self.docs.rglob("*") if path.is_file()}

    def _run(self):
        with patch.object(scraper, "_fetch_sea_article",
                          side_effect=lambda item: self.results[item["source_path"]]):
            scraper.process_sea()

    def _assert_failure_without_writes(self, message, failed_source=None):
        before = self._snapshot()

        def fetch(item):
            if item["source_path"] == failed_source:
                raise RuntimeError("pinned article unavailable")
            return self.results[item["source_path"]]

        with patch.object(scraper, "_fetch_sea_article", side_effect=fetch) as fetch_article, \
                patch.object(Path, "mkdir") as mkdir, \
                patch.object(Path, "write_text") as write_text, \
                patch.object(Path, "unlink") as unlink:
            with self.assertRaisesRegex(RuntimeError, message):
                scraper.process_sea()
        mkdir.assert_not_called()
        write_text.assert_not_called()
        unlink.assert_not_called()
        self.assertEqual(self._snapshot(), before)
        return fetch_article

    def _assert_idempotent(self):
        before = self._snapshot()
        with patch.object(Path, "mkdir") as mkdir, \
                patch.object(Path, "write_text") as write_text, \
                patch.object(Path, "unlink") as unlink:
            self._run()
        mkdir.assert_not_called()
        write_text.assert_not_called()
        unlink.assert_not_called()
        self.assertEqual(self._snapshot(), before)

    def _geo_pages(self):
        return json.loads((self.docs / "geo" / "meta.json").read_text(encoding="utf-8"))["pages"]

    def test_same_title_routes_keep_identity_source_order_and_idempotence(self):
        self._run()
        self.assertEqual(self.old_path.read_text(encoding="utf-8"), self.old_text)
        expected_new = self._render(self.title, self.new_url).replace(
            f"]({self.old_url})", "](/docs/geo/legacy-route)",
        )
        self.assertEqual(self.new_path.read_text(encoding="utf-8"), expected_new)
        self.assertEqual(self._geo_pages(), [self.old_path.stem, self.new_path.stem])
        self.assertEqual(set((self.docs / "geo").glob("*.md")), {self.old_path, self.new_path})
        self._assert_idempotent()

        self.tree[1:] = list(reversed(self.tree[1:]))
        self._run()
        self.assertEqual(self._geo_pages(), [self.new_path.stem, self.old_path.stem])
        self.assertEqual(self.old_path.read_text(encoding="utf-8"), self.old_text)
        self.assertEqual(self.new_path.read_text(encoding="utf-8"), expected_new)
        self.assertEqual(self.other_manual.read_bytes(), self.other_text)
        self._assert_idempotent()

    def test_same_source_urls_keep_routes_after_both_titles_change(self):
        self._run()
        renamed = {self.old_url: "旧文大幅改名", self.new_url: "新文另一个标题"}
        self.tree[1:] = [(renamed[url], url) for _, url in self.tree[1:]]
        self._run()
        self.assertEqual(scraper._read_local_title(self.old_path), renamed[self.old_url])
        self.assertEqual(scraper._read_local_title(self.new_path), renamed[self.new_url])
        self.assertIn(self.results[self.old_url]["body"], self.old_path.read_text(encoding="utf-8"))
        self.assertIn("新文章不同正文", self.new_path.read_text(encoding="utf-8"))
        self.assertEqual(self._geo_pages(), [self.old_path.stem, self.new_path.stem])
        self.assertEqual(set((self.docs / "geo").glob("*.md")), {self.old_path, self.new_path})
        self._assert_idempotent()

    def test_unbound_third_source_with_same_title_fails_before_fetch(self):
        self.tree.append((self.title, "/sea/geo/unverified-third"))
        self._assert_failure_without_writes("duplicate source title").assert_not_called()

    def test_stray_local_same_title_is_rejected_before_or_after_pinned_file(self):
        for filename in ("aaa-stray.md", "zzz-stray.md"):
            with self.subTest(filename=filename):
                stray = self.docs / "geo" / filename
                stray.write_text(self.old_text, encoding="utf-8")
                try:
                    self._assert_failure_without_writes("duplicate local title").assert_not_called()
                finally:
                    stray.unlink()

    def test_override_routes_must_be_distinct_including_md_mdx_same_stem(self):
        for new_route in ("geo/legacy-route.md", "geo/legacy-route.mdx"):
            with self.subTest(new_route=new_route):
                self.overrides[self.new_url] = new_route
                self._assert_failure_without_writes("duplicate /sea route override").assert_not_called()

    def test_override_scope_traversal_and_extension_are_rejected(self):
        invalid_routes = (
            "seo/new.md", "../new.md", "geo/../../outside.md",
            "geo/nested/new.md", "geo/new.txt", str(self.repo / "outside.md"),
        )
        for new_route in invalid_routes:
            with self.subTest(new_route=new_route):
                self.overrides[self.new_url] = new_route
                self._assert_failure_without_writes("invalid /sea route override").assert_not_called()

    def test_missing_pinned_source_preserves_existing_file(self):
        self._run()
        complete_tree = list(self.tree)
        for missing_url in (self.old_url, self.new_url):
            with self.subTest(missing_url=missing_url):
                self.tree[:] = [item for item in complete_tree if item[1] != missing_url]
                self._assert_failure_without_writes("pinned /sea source missing").assert_not_called()
        self.tree[:] = complete_tree

    def test_fetch_failure_with_valid_pins_has_no_partial_writes(self):
        fetched = self._assert_failure_without_writes(
            "pinned article unavailable", failed_source=self.new_url,
        )
        self.assertEqual(fetched.call_count, len(self.tree))
        self.assertFalse(self.new_path.exists())

    def test_new_pinned_route_is_reserved_before_earlier_automatic_slug(self):
        earlier_url = "/sea/geo/earlier-unpinned"
        earlier_title = self.new_path.stem
        self.tree.insert(1, (earlier_title, earlier_url))
        self.results[earlier_url] = {
            "body": "较早出现但不是绑定文章。\n", "date": "2026-10-23", "updated": None,
        }
        self._run()
        automatic = self.new_path.with_name(self.new_path.stem + "-2.md")
        self.assertEqual(automatic.read_text(encoding="utf-8"), self._render(earlier_title, earlier_url))
        self.assertEqual(scraper._read_local_title(self.new_path), self.title)
        self.assertEqual(self.old_path.read_text(encoding="utf-8"), self.old_text)
        self.assertEqual(self._geo_pages(), [automatic.stem, self.old_path.stem, self.new_path.stem])
        self._assert_idempotent()

    def test_existing_mdx_cannot_occupy_new_pinned_md_route(self):
        conflicting = self.new_path.with_suffix(".mdx")
        conflicting.write_text(
            scraper._render_sea_doc("另一篇本地文章", "2026-10-01", None, "不得覆盖\n"),
            encoding="utf-8",
        )
        self._assert_failure_without_writes("pinned /sea route already occupied").assert_not_called()


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
