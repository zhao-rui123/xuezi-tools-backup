#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.unified_indexer import UnifiedIndexer


class TestUnifiedIndexerImprovements(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.tmp.name) / "memory"
        self.index_dir = Path(self.tmp.name) / "index"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _indexer(self):
        return UnifiedIndexer(unified_dir=str(self.index_dir), memory_dir=str(self.memory_dir))

    def test_stale_term_removed_after_reindex(self):
        f = self.memory_dir / "a.md"
        f.write_text("韩国服务器 Claude Code", encoding="utf-8")
        idx = self._indexer()
        idx.build_index(force=True)

        word_file = self.index_dir / "chinese" / "韩国服务器.json"
        self.assertTrue(word_file.exists())

        time.sleep(1.1)
        f.write_text("Claude Code", encoding="utf-8")
        os.utime(f, None)
        idx.build_index(force=False)

        if word_file.exists():
            data = json.loads(word_file.read_text(encoding="utf-8"))
            self.assertEqual(data, [])
        else:
            self.assertFalse(word_file.exists())

    def test_phrase_boost_and_snippet(self):
        a = self.memory_dir / "a.md"
        b = self.memory_dir / "b.md"
        a.write_text("这里记录 Claude Code 和韩国服务器的联调方法。", encoding="utf-8")
        b.write_text("这里分别提到 Claude 和服务器，但是不连续。", encoding="utf-8")
        idx = self._indexer()
        idx.build_index(force=True)

        results = idx.search("Claude Code 韩国服务器", limit=5)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(Path(results[0]["path"]).name, "a.md")
        self.assertIn("Claude Code", results[0]["snippet"])


if __name__ == "__main__":
    unittest.main()
