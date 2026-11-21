from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "webnovel-short-studio"
SCRIPTS_DIR = SKILL_DIR / "scripts"


class WebnovelShortStudioTests(unittest.TestCase):
    def test_init_lint_and_export_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "short_proj"
            r_init = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "init_short_project.py"),
                    "--root",
                    str(root),
                    "--title",
                    "谎言额度",
                    "--mode",
                    "flash",
                    "--narrative",
                    "rules",
                    "--platform",
                    "zhihu",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(r_init.returncode, 0, r_init.stderr)
            self.assertTrue((root / "00_脑洞与节拍.md").exists())
            self.assertTrue((root / "01_轻量状态.md").exists())

            ch1 = root / "正文" / "第01节.md"
            ch1.write_text(
                "# 1. 额度的数字\n\n"
                "我能看见每个人头顶剩下的谎言次数。\n\n"
                "未婚夫把钻戒套进我无名指时，他头顶的数字跳了一下：\n\n"
                "「我这辈子只爱你一个人。」\n\n"
                "数字从【1】变成了【0】。\n\n"
                "我握着他的手笑出了声：「那你猜猜，你妈头顶现在是负数几？」\n",
                encoding="utf-8",
            )

            r_lint = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "lint_webnovel.py"),
                    "--file",
                    str(ch1),
                    "--narrative",
                    "rules",
                    "--first-chapter",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(r_lint.returncode, 0, r_lint.stderr)
            data = json.loads(r_lint.stdout)
            self.assertEqual(data["files_scanned"], 1)
            self.assertEqual(len(data["results"]), 1)

            out_docx = root / "交付" / "谎言额度.docx"
            out_txt = root / "交付" / "谎言额度.txt"
            r_exp = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "export_short.py"),
                    "--chapters-dir",
                    str(root / "正文"),
                    "--out-docx",
                    str(out_docx),
                    "--out-txt",
                    str(out_txt),
                    "--title",
                    "谎言额度",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(r_exp.returncode, 0, r_exp.stderr)
            self.assertTrue(out_docx.exists())
            self.assertTrue(out_txt.exists())
            self.assertIn("「我这辈子只爱你一个人。」", out_txt.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
