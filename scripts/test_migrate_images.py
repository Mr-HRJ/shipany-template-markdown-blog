"""Read-only image discovery scope tests; no credentials or uploads are used."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import migrate_images


class CollectUrlsScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="image-scope-test-")
        self.addCleanup(self.temp.cleanup)
        self.docs = Path(self.temp.name) / "docs"
        self.selected = self.docs / "selected"
        self.nested = self.selected / "nested"
        self.nested.mkdir(parents=True)
        self.other = self.docs / "other"
        self.other.mkdir()
        self.first = self.selected / "page.md"
        self.second = self.nested / "page.mdx"
        self.outside = self.other / "page.md"
        self.shared_url = "https://images.example/shared.jpg"
        self.selected_url = "https://images.example/selected.png"
        self.r2_url = "https://existing-bucket.r2.dev/docs/photo.webp"
        self.outside_url = "https://images.example/outside.gif"
        self.first.write_text(
            f"![image]({self.shared_url})\n"
            f"![duplicate]({self.shared_url})\n"
            f'<img alt="selected" src="{self.selected_url}" />\n',
            encoding="utf-8",
        )
        self.second.write_text(
            f"![image]({self.shared_url})\n![R2]({self.r2_url})\n",
            encoding="utf-8",
        )
        self.outside.write_text(
            f"![outside]({self.outside_url})\n", encoding="utf-8"
        )

    def test_only_selected_root_is_scanned(self):
        urls, files = migrate_images.collect_urls(roots=[self.selected])
        self.assertEqual(
            set(urls), {self.shared_url, self.selected_url, self.r2_url}
        )
        self.assertNotIn(self.outside_url, files)
        self.assertEqual(set(files[self.shared_url]), {self.first, self.second})
        self.assertEqual(files[self.selected_url], [self.first])
        self.assertEqual(files[self.r2_url], [self.second])

    def test_default_scans_all_docs_for_backward_compatibility(self):
        with patch.object(migrate_images, "DOCS", self.docs):
            urls, files = migrate_images.collect_urls()
        self.assertEqual(
            set(urls),
            {self.shared_url, self.selected_url, self.r2_url, self.outside_url},
        )
        self.assertEqual(files[self.outside_url], [self.outside])

    def test_overlapping_and_repeated_roots_do_not_duplicate_files(self):
        expected_urls, expected_files = migrate_images.collect_urls(
            roots=[self.selected]
        )
        urls, files = migrate_images.collect_urls(
            roots=[self.selected, self.nested, self.selected]
        )
        self.assertEqual(set(urls), set(expected_urls))
        self.assertEqual(files, expected_files)
        for paths in files.values():
            self.assertEqual(len(paths), len(set(paths)))

    def test_skip_host_remains_effective_with_selected_roots(self):
        urls, files = migrate_images.collect_urls(
            skip_host="existing-bucket.r2.dev", roots=[self.selected]
        )
        self.assertEqual(set(urls), {self.shared_url, self.selected_url})
        self.assertNotIn(self.r2_url, files)
        self.assertNotIn(self.outside_url, files)


if __name__ == "__main__":
    unittest.main()
