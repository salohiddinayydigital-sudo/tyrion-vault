#!/usr/bin/env python3
"""Tyrion asboblari uchun testlar (stdlib unittest — qo'shimcha o'rnatish kerak emas).

Ishlatish:
  py -3 -m unittest discover tests -v
"""

from __future__ import annotations

import ast
import os
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
VAULT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import catalog  # noqa: E402
import doctor  # noqa: E402


class CatalogTests(unittest.TestCase):
    """Katalog — tizimning yagona reestri."""

    def test_scan_returns_expected_shape(self) -> None:
        data = catalog.scan()
        self.assertEqual(data["schema"], catalog.SCHEMA)
        for key in ("counts", "items", "mirrors", "warnings"):
            self.assertIn(key, data)

    def test_counts_match_item_lists(self) -> None:
        data = catalog.scan()
        for layer in catalog.LAYERS:
            self.assertEqual(
                data["counts"][layer], len(data["items"][layer]),
                f"{layer}: sanoq ro'yxatga mos emas",
            )

    def test_knowledge_layer_is_populated(self) -> None:
        """Bilim va agent qatlami bo'sh bo'lsa — tizim sindirilgan."""
        counts = catalog.scan()["counts"]
        self.assertGreater(counts["wiki"], 0, "wiki/ bo'sh")
        self.assertGreater(counts["agents"], 0, "agents/ bo'sh")
        self.assertGreater(counts["skills"], 0, "skills/ bo'sh")

    def test_frontmatter_parsing(self) -> None:
        data = catalog.scan()
        notes = data["items"]["wiki"]
        self.assertTrue(notes, "wiki qayd yo'q")
        parsed = [n for n in notes if n.get("title")]
        self.assertGreater(len(parsed), 0, "hech bir qaydda name o'qilmadi")

    def test_frontmatter_catches_backslash_escape(self) -> None:
        """Qo'shtirnoq ichidagi backslash YAML'ni buzadi — katalog buni tutishi kerak."""
        backslash = chr(92)
        content = f'---\nname: x\nsource: "D:{backslash}tyrion{backslash}a.md"\n---\n\n# x\n'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.md"
            path.write_text(content, encoding="utf-8")
            fm = catalog.read_frontmatter(path)
            self.assertIn("_error", fm, "buzilgan YAML aniqlanmadi")

    def test_valid_frontmatter_has_no_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.md"
            path.write_text('---\nname: x\nsource: "vault/a.md"\n---\n\n# x\n', encoding="utf-8")
            fm = catalog.read_frontmatter(path)
            self.assertNotIn("_error", fm)

    def test_build_and_check_roundtrip(self) -> None:
        """build → check mos kelishi kerak (katalog haqiqatni aks ettiradi)."""
        before = catalog.MANIFEST.read_text(encoding="utf-8") if catalog.MANIFEST.is_file() else None
        try:
            self.assertEqual(catalog.cmd_build(_ns()), 0)
            self.assertEqual(catalog.cmd_check(_ns()), 0)
        finally:
            if before is None and catalog.MANIFEST.is_file():
                catalog.MANIFEST.unlink()

    def test_check_detects_stale_manifest(self) -> None:
        """Katalog eskirsa `check` xato qaytarishi kerak (jim qolmasligi)."""
        original = catalog.MANIFEST.read_text(encoding="utf-8")
        try:
            data = json.loads(original)
            data["counts"]["wiki"] = -1
            catalog.MANIFEST.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertNotEqual(catalog.cmd_check(_ns()), 0, "eskirgan katalog sezilmadi")
        finally:
            catalog.MANIFEST.write_text(original, encoding="utf-8")

    def test_mirror_status_classifies_pairs(self) -> None:
        items = {
            "commands": [{"name": "a", "path": "x", "sha256": "1"}, {"name": "b", "path": "y", "sha256": "2"}],
            "commands.mirror": [{"name": "a", "path": "x2", "sha256": "1"}, {"name": "b", "path": "y2", "sha256": "9"}],
        }
        statuses = {m["name"]: m["status"] for m in catalog.mirror_status(items)}
        self.assertEqual(statuses["a"], "identical")
        self.assertEqual(statuses["b"], "drifted")

    def test_human_claims_detects_mismatch(self) -> None:
        """Noto'g'ri sanoq berilsa, oddiy matndagi raqamlar mos emas deb topilsin."""
        claims = catalog.human_claims({"wiki": 999999})
        self.assertTrue(claims, "nazorat qilinadigan raqam yo'q")
        self.assertTrue(all(not c["ok"] for c in claims), claims)

    def test_human_claims_all_match_catalog(self) -> None:
        """INDEX.md/README.md/rules dagi raqamlar katalogdagi haqiqatga mos bo'lsin.

        Regressiya: bu sonlar bir vaqtda 41 bo'lib qolgan, wiki esa 42 edi —
        miya o'zi haqida yolg'on gapirardi.
        """
        claims = catalog.human_claims(catalog.scan()["counts"])
        self.assertTrue(claims, "claims registry bo'sh")
        for claim in claims:
            self.assertTrue(claim["ok"], f"{claim['file']}: {claim}")


class DoctorTests(unittest.TestCase):
    """Doctor — tizim sog'lig'i."""

    def test_required_files_exist(self) -> None:
        missing = [rel for rel in doctor.REQUIRED if not (VAULT / rel).is_file()]
        self.assertEqual(missing, [], f"majburiy fayllar yo'q: {missing}")

    def test_claim_marker_matches_catalog(self) -> None:
        """AGENTS.md dagi e'lon qilingan raqamlar katalogga mos bo'lishi shart."""
        data = catalog.scan()
        report = doctor.Report()
        doctor.check_claims(report, data)
        row = next(r for r in report.rows if r["check"].startswith("Raqamlar"))
        self.assertEqual(row["status"], doctor.OK, row["detail"])

    def test_all_claim_checks_are_ok(self) -> None:
        """Marker ham, oddiy matndagi raqamlar ham katalogga mos bo'lsin."""
        report = doctor.Report()
        doctor.check_claims(report, catalog.scan())
        rows = [r for r in report.rows if r["check"].startswith("Raqamlar")]
        self.assertGreaterEqual(len(rows), 2, "oddiy matn raqamlari tekshirilmadi")
        for row in rows:
            self.assertNotEqual(row["status"], doctor.FAIL, row["detail"])
            self.assertEqual(row["status"], doctor.OK, f"{row['check']}: {row['detail']}")

    def test_memory_within_limit(self) -> None:
        """memory.md o'zining ixchamlik shartini buzmasin (≤ 90 qator)."""
        report = doctor.Report()
        doctor.check_memory(report)
        row = next(r for r in report.rows if r["check"].startswith("Xotira"))
        self.assertEqual(row["status"], doctor.OK, row["detail"])

    def test_secret_scan_flags_fake_key(self) -> None:
        """Soxta kalit naqshi aniqlanishi kerak (kalit bo'laklab yasalgan — faylda sir yo'q)."""
        fake_key = "sk-" + "abcdefghijklmnopqrstuvwxyz" + "012345"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "leak.json"
            path.write_text('{"key": "%s"}' % fake_key, encoding="utf-8")
            text = path.read_text(encoding="utf-8")
            hits = [label for pattern, label in doctor.SECRET_PATTERNS if re.search(pattern, text)]
            self.assertTrue(hits, "soxta kalit aniqlanmadi")

    def test_run_returns_completed_process(self) -> None:
        proc = doctor.run([sys.executable, "-c", "print('ok')"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("ok", proc.stdout)

    def test_quick_doctor_exits_cleanly(self) -> None:
        """doctor --quick ishga tushishi va 0/1 qaytarishi kerak (2 emas)."""
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "doctor.py"), "--quick", "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertIn(proc.returncode, (0, 1), f"kutilmagan kod: {proc.returncode}\n{proc.stderr}")
        payload = json.loads(proc.stdout)
        self.assertIn("checks", payload)
        self.assertGreater(len(payload["checks"]), 5)


class BrainSearchTests(unittest.TestCase):
    """brain-search — LLM'siz (deterministik) qidiruv, token tejamkor."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "brain-search.py"), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_search_finds_known_note(self) -> None:
        proc = self._run("search", "meta katta byudjet scaling", "--top", "3")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("meta-katta-byudjet-scaling", proc.stdout)

    def test_stats_reports_no_orphans(self) -> None:
        proc = self._run("stats")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("orphan wiki: 0", proc.stdout)

    def test_show_unknown_returns_error(self) -> None:
        proc = self._run("show", "bu-qayd-mavjud-emas-xyz")
        self.assertEqual(proc.returncode, 1)

    def test_links_of_hub(self) -> None:
        proc = self._run("links", "sop-xarita")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("chiquvchi", proc.stdout)
        self.assertIn("kiruvchi", proc.stdout)


class SkillSearchTests(unittest.TestCase):
    """skill-search — skill reyestri va agentga ulash (0 token, LLM'siz)."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "skill-search.py"), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_check_reports_healthy_registry(self) -> None:
        proc = self._run("check")
        self.assertEqual(proc.returncode, 0, proc.stdout[-500:] + proc.stderr[-300:])
        self.assertIn("butun", proc.stdout)

    def test_agent_reports_attached_skills(self) -> None:
        proc = self._run("agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        self.assertIn("video-editing", proc.stdout)
        self.assertIn("video-motion-graphics", proc.stdout)

    def test_brief_routes_editing_task(self) -> None:
        proc = self._run("brief", "shu videoni montaj qilib ber", "--agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        self.assertIn("Tanlandi: video-editing", proc.stdout)
        self.assertIn("SKILL.md", proc.stdout)

    def test_routing_matrix(self) -> None:
        """Routing aniqligi: umumiy so'zlar ("reels", "ber") skillni chalkashtirmasin.

        Regressiya: "animatsion reels yasab ber" bir paytlar video-editing ga ketgan edi —
        IDF (so'z noyobligi) va stop-so'zlar tufayli endi to'g'ri taqsimlanadi.
        """
        cases = [
            ("animatsion reels yasab ber", "video-motion-graphics"),
            ("animatsion video kerak", "video-motion-graphics"),
            ("after effects uslubida logo animatsiya", "video-motion-graphics"),
            ("kinetik tipografiya bilan video", "video-motion-graphics"),
            ("motion graphics qilib ber", "video-motion-graphics"),
            ("mijoz videoni montaj qilib ber", "video-editing"),
            ("shu videoni kesib ber", "video-editing"),
            ("bergan videomni edit qilib ber", "video-editing"),
            ("reels qilib ber", "video-editing"),
            ("videoimga subtitr qo'sh", "video-editing"),
            ("materialimni tahrirla", "video-editing"),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                proc = self._run("brief", query, "--agent", "video-editor")
                self.assertEqual(proc.returncode, 0, proc.stdout[-300:])
                self.assertIn(f"Tanlandi: {expected}", proc.stdout)

    def test_brief_routes_animation_task(self) -> None:
        proc = self._run("brief", "kinetik tipografiya animatsion video after effects", "--agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        self.assertIn("Tanlandi: video-motion-graphics", proc.stdout)

    def test_brief_without_match_exits_one(self) -> None:
        proc = self._run("brief", "zzz qqq www", "--agent", "video-editor")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("mos skill topilmadi", proc.stdout)

    def test_unknown_agent_exits_two(self) -> None:
        proc = self._run("agent", "bunday-agent-yoq-xyz")
        self.assertEqual(proc.returncode, 2)

    def test_attached_skills_exist_on_disk(self) -> None:
        proc = self._run("agent", "video-editor")
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:])
        for rel in re.findall(r"(skills/\S+/SKILL\.md)", proc.stdout):
            self.assertTrue((VAULT / rel).is_file(), f"skill fayli yo'q: {rel}")


class SkillAttachTests(unittest.TestCase):
    """skill-attach — skill ↔ agent ulash (ikki tomonlama, idempotent, dry-run)."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "skill-attach.py"), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_list_shows_operator_skills(self) -> None:
        proc = self._run("list")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("video-editing", proc.stdout)
        self.assertRegex(proc.stdout, r"Operator skill: \d+")

    def test_dry_run_changes_nothing(self) -> None:
        skill = VAULT / "skills" / "copywriting" / "SKILL.md"
        before = skill.read_bytes()
        proc = self._run("set", "copywriting", "--agents", "copy-writer", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        self.assertIn("REJA (dry-run)", proc.stdout)
        self.assertEqual(skill.read_bytes(), before, "dry-run faylni o'zgartirmasligi shart")

    def test_set_is_idempotent(self) -> None:
        skill = VAULT / "skills" / "copywriting" / "SKILL.md"
        proc = self._run("set", "copywriting", "--agents", "copy-writer")
        self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
        after = skill.read_bytes()
        proc2 = self._run("set", "copywriting", "--agents", "copy-writer")
        self.assertEqual(proc2.returncode, 0, proc2.stderr[-300:])
        self.assertEqual(skill.read_bytes(), after, "qayta urinish faylni o'zgartirmasligi shart")

    def test_unknown_skill_exits_one(self) -> None:
        proc = self._run("set", "bunday-skill-yoq-xyz", "--agents", "copy-writer")
        self.assertEqual(proc.returncode, 1)

    def test_unknown_agent_exits_one(self) -> None:
        proc = self._run("set", "copywriting", "--agents", "bunday-agent-yoq-xyz")
        self.assertEqual(proc.returncode, 1)

    def test_missing_arguments_exit_two(self) -> None:
        proc = self._run("set", "copywriting")
        self.assertEqual(proc.returncode, 2)

    def test_agent_skills_are_bidirectional(self) -> None:
        """Har ulanish ikki tomonda ham yozilgan bo'lishi shart (check shuni tekshiradi)."""
        proc = self._run("list")
        names = re.findall(r"operator\s+(\S+)\s+→\s+(.+)", proc.stdout)
        listed = {name for name, state in names if state.strip() != "— ulanganmagan"}
        self.assertIn("video-editing", listed)
        check = subprocess.run(
            [sys.executable, str(TOOLS / "skill-search.py"), "check"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(check.returncode, 0, check.stdout[-400:])
        self.assertIn("butun", check.stdout)


class VideoRunTests(unittest.TestCase):
    """video-run — video ishi uchun ish maydoni (scaffold, dry-run, idempotent)."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "video-run.py"), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_dry_run_creates_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("new", "--client", "test", "--topic", "demo",
                             "--root", tmp, "--dry-run")
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            self.assertIn("REJA (dry-run)", proc.stdout)
            self.assertEqual(list(Path(tmp).rglob("*.py")), [], "dry-run fayl yozmasligi shart")
            self.assertEqual(list(Path(tmp).rglob("props.json")), [])

    def test_new_creates_standard_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("new", "--client", "dilobar", "--topic", "kuz aksiya", "--root", tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            base = Path(tmp) / f"{datetime.now():%Y-%m-%d}-dilobar-kuz-aksiya" / "workers" / "video-editor"
            for name in ("props.json", "build.py", "MANIFEST.md", "qa.md"):
                self.assertTrue((base / name).is_file(), f"yetishmayapti: {name}")
            self.assertTrue((base / "assets").is_dir())
            self.assertTrue((base / "renders").is_dir())
            props = json.loads((base / "props.json").read_text(encoding="utf-8"))
            self.assertEqual((props["output"]["width"], props["output"]["height"]), (1080, 1920))

    def test_generated_build_py_is_valid_python(self) -> None:
        """Skelet sintaksis xatosi bilan berilmasligi shart (BOM/escape tuzoqlari)."""
        with tempfile.TemporaryDirectory() as tmp:
            self._run("new", "--client", "test", "--topic", "sintaksis", "--root", tmp)
            build = next(Path(tmp).rglob("build.py"))
            raw = build.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), "build.py BOM'siz bo'lishi shart")
            ast.parse(raw.decode("utf-8"))  # xato bo'lsa test yiqiladi

    def test_existing_files_are_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._run("new", "--client", "test", "--topic", "takror", "--root", tmp)
            base = next(Path(tmp).rglob("build.py")).parent
            marker = base / "props.json"
            marker.write_text('{"custom": true}', encoding="utf-8")
            proc = self._run("new", "--client", "test", "--topic", "takror", "--root", tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            self.assertEqual(marker.read_text(encoding="utf-8"), '{"custom": true}',
                             "mavjud props.json tegilmasligi shart")

    def test_force_archives_old_skeletons(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._run("new", "--client", "test", "--topic", "force", "--root", tmp)
            base = next(Path(tmp).rglob("build.py")).parent
            marker = base / "props.json"
            marker.write_text('{"custom": true}', encoding="utf-8")
            proc = self._run("new", "--client", "test", "--topic", "force",
                             "--root", tmp, "--force")
            self.assertEqual(proc.returncode, 0, proc.stderr[-300:])
            self.assertTrue(list((base / "_archive").glob("build.py.*")), "eskisi arxivga olinmagan")
            self.assertEqual(marker.read_text(encoding="utf-8"), '{"custom": true}')

    def test_unknown_format_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("new", "--client", "t", "--topic", "t", "--root", tmp,
                             "--format", "21x9")
            self.assertEqual(proc.returncode, 2)

    def test_status_of_missing_run_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self._run("status", "yoq-run", "--root", tmp)
            self.assertEqual(proc.returncode, 1)


class BrainGraphTests(unittest.TestCase):
    """brain-graph — wikilinklardan deterministik graf (0 token, lahzali)."""

    def test_build_and_stats(self) -> None:
        build = subprocess.run(
            [sys.executable, str(TOOLS / "brain-graph.py"), "build"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(build.returncode, 0, build.stderr[-300:])
        self.assertIn("0 token", build.stdout)
        stats = subprocess.run(
            [sys.executable, str(TOOLS / "brain-graph.py"), "stats"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(stats.returncode, 0)
        self.assertIn("tugun", stats.stdout)

    def test_graph_has_nodes_and_links(self) -> None:
        graph = VAULT / "graphify-out" / "graph.json"
        self.assertTrue(graph.is_file(), "graph.json yo'q")
        data = json.loads(graph.read_text(encoding="utf-8"))
        self.assertGreater(data["stats"]["nodes"], 50)
        self.assertGreater(data["stats"]["links"], 50)
        self.assertIn("community", data["nodes"][0])


class VaultAuditTests(unittest.TestCase):
    def test_vault_audit_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "vault-audit.py"), str(VAULT)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("JAMI MUAMMO", proc.stdout)



class HookTests(unittest.TestCase):
    """Hook qatlami — deterministik nazorat."""

    def _module(self):
        sys.path.insert(0, str(TOOLS))
        import importlib
        return importlib.import_module("install-hooks")

    def test_vault_path_substitution_has_no_control_chars(self) -> None:
        """Yo'l almashtirilganda TAB kabi belgi paydo bo'lmasligi shart.

        Regressiya: xom JSON matnida almashtirilsa `vault\\tyrion` ichidagi `\\t`
        TAB belgisiga aylanib, hook umuman ishlamay qolardi (dry-run tutgan).
        """
        module = self._module()
        config = module.build_config(VAULT, VAULT)
        commands = [
            hook["command"]
            for group in config["hooks"].values()
            for hook in group[0]["hooks"]
        ]
        self.assertTrue(commands)
        for command in commands:
            self.assertNotIn("\t", command, f"TAB belgisi: {command!r}")
            self.assertIn(str(VAULT), command)

    def test_merge_is_idempotent(self) -> None:
        module = self._module()
        canonical = module.build_config(VAULT, VAULT)
        settings: dict = {}
        settings, first = module.merge(settings, canonical)
        self.assertTrue(first, "birinchi merge hech narsa qo'shmadi")
        _settings, second = module.merge(settings, canonical)
        self.assertEqual(second, [], "ikkinchi merge takror qo'shdi")

    def test_merge_preserves_existing_hooks(self) -> None:
        module = self._module()
        canonical = module.build_config(VAULT, VAULT)
        existing = {"hooks": {"SessionStart": [
            {"matcher": "", "hooks": [{"type": "command", "command": "echo boshqa-hook"}]}
        ]}}
        merged, _added = module.merge(existing, canonical)
        commands = [
            h["command"] for g in merged["hooks"]["SessionStart"] for h in g["hooks"]
        ]
        self.assertIn("echo boshqa-hook", commands, "mavjud hook o'chib ketdi")

    def test_command_sync_is_byte_exact_and_idempotent(self) -> None:
        """Buyruq nusxasi bayt-aniq bo'lishi va ikkinchi urinishda tegmasligi shart.

        Regressiya: `write_text` Windows'da satr oxirini o'zgartirib, nusxa
        "drift" bo'lib ko'rinardi.
        """
        module = self._module()
        module.sync_commands(VAULT, dry_run=False)
        source = VAULT / "commands"
        for path in sorted(source.glob("*.md")):
            mirror = VAULT / ".claude" / "commands" / path.name
            self.assertTrue(mirror.is_file(), f"nusxa yo'q: {path.name}")
            self.assertEqual(path.read_bytes(), mirror.read_bytes(), f"baytlar farqli: {path.name}")
        self.assertEqual(module.sync_commands(VAULT, dry_run=False), [],
                         "ikkinchi sinxronizatsiya keraksiz nusxa qildi")

    def test_brief_and_ingest_run(self) -> None:
        cases = {
            "brief": [],
            "ingest": ["--warn-only", "--quiet"],
            "dod": ["--warn-only"],
        }
        for mode, flags in cases.items():
            proc = subprocess.run(
                [sys.executable, str(VAULT / "hooks" / "tyrion-hook.py"), mode, *flags],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
            )
            self.assertEqual(proc.returncode, 0, f"{mode}: {proc.stderr[-300:]}")



class SpendGuardTests(unittest.TestCase):
    """Spend-Guard — Pullik media xavfsizlik nazorati va 6 ta darvoza."""

    def setUp(self) -> None:
        import importlib
        self.sg = importlib.import_module("spend-guard")

    def test_budget_hike_within_20_pct_passes(self) -> None:
        res = self.sg.check_budget_change(current_daily=100.0, proposed_daily=118.0, max_daily_cap=500.0)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["errors"]), 0)

    def test_budget_hike_over_20_pct_fails(self) -> None:
        res = self.sg.check_budget_change(current_daily=100.0, proposed_daily=135.0, max_daily_cap=500.0)
        self.assertFalse(res["passed"])
        self.assertTrue(any("20%" in e for e in res["errors"]))

    def test_budget_ceiling_exceeded_fails(self) -> None:
        res = self.sg.check_budget_change(current_daily=100.0, proposed_daily=110.0, max_daily_cap=105.0)
        self.assertFalse(res["passed"])
        self.assertTrue(any("limitdan" in e for e in res["errors"]))

    def test_telegram_copy_160_chars_and_emoji(self) -> None:
        # 160 belgidan oshishi xato berishi kerak
        long_text = "A" * 165
        res = self.sg.check_ad_copy(platform="telegram", text=long_text)
        self.assertFalse(res["passed"])
        self.assertTrue(any("160 belgidan" in e for e in res["errors"]))

        # 2 tadan ko'p emoji xato berishi kerak
        emoji_text = "Kanalga kiring! 🚀 🎉"
        res_emoji = self.sg.check_ad_copy(platform="telegram", text=emoji_text)
        self.assertFalse(res_emoji["passed"])
        self.assertTrue(any("ko'pi bilan 1 ta emoji" in e for e in res_emoji["errors"]))

    def test_telegram_copy_all_caps(self) -> None:
        caps_text = "TEZDA sotib oling va chegirma oling!"
        res = self.sg.check_ad_copy(platform="telegram", text=caps_text)
        self.assertFalse(res["passed"])
        self.assertTrue(any("ALL CAPS" in e for e in res["errors"]))

    def test_tracking_capi_without_event_id_fails(self) -> None:
        res = self.sg.check_tracking_setup(has_browser_pixel=True, has_server_capi=True, event_id_present=False)
        self.assertFalse(res["passed"])
        self.assertTrue(any("event_id" in e for e in res["errors"]))

    def test_change_packet_validation(self) -> None:
        valid_packet = "## Reja\nBoshlang'ich holat: CPA $15.\nXavf: past.\nTeskari qadam: qaytarish mumkin.\nStop-loss: CPA > $20 bo'lsa to'xtatish."
        res_valid = self.sg.check_change_packet(valid_packet)
        self.assertTrue(res_valid["passed"])

        invalid_packet = "## Reja\nByudjetni $500 ga oshiramiz."
        res_invalid = self.sg.check_change_packet(invalid_packet)
        self.assertFalse(res_invalid["passed"])
        self.assertTrue(any("Teskari qadam" in e for e in res_invalid["errors"]))


class CalculatorTests(unittest.TestCase):
    """Calculator — Media matematikasi (Meta, Google, Telegram)."""

    def setUp(self) -> None:
        import calculator
        self.calc = calculator

    def test_breakeven_math(self) -> None:
        res = self.calc.calc_breakeven(price=100.0, cogs=40.0, shipping=10.0, processing_fee_pct=2.0)
        self.assertEqual(res["price"], 100.0)
        self.assertEqual(res["cogs"], 40.0)
        self.assertEqual(res["shipping"], 10.0)
        self.assertEqual(res["processing_fee"], 2.0)
        self.assertEqual(res["gross_profit_per_unit"], 48.0)
        self.assertEqual(res["breakeven_cpa"], 48.0)
        self.assertAlmostEqual(res["breakeven_roas"], 2.08, places=2)

    def test_meta_155_allocations(self) -> None:
        res = self.calc.calc_meta_155(daily_budget=200.0, target_cpa=20.0)
        alloc = res["allocations"]
        self.assertEqual(alloc["broad_prospecting_70pct"], 140.0)
        self.assertEqual(alloc["advantage_plus_25pct"], 50.0)
        self.assertEqual(alloc["reserve_5pct"], 10.0)

    def test_google_sculpt_channel_split(self) -> None:
        res = self.calc.calc_google_sculpt(monthly_budget=3000.0, target_cpa=25.0, avg_cpc=1.8, irrelevant_query_waste_pct=20.0)
        split = res["channel_split"]
        self.assertEqual(split["search_coliseum_60pct"], 1800.0)
        self.assertEqual(split["pmax_demandgen_40pct"], 1200.0)
        neg = res["negative_keyword_optimization"]
        self.assertEqual(neg["projected_monthly_waste_saved"], 360.0)

    def test_telegram_funnel_math(self) -> None:
        res = self.calc.calc_telegram_funnel(budget=600.0, cpm=3.0, ctr_pct=1.0, bot_start_pct=50.0, lead_activation_pct=20.0, order_conversion_pct=10.0, aov=50.0)
        self.assertEqual(res["impressions"], 200000)
        self.assertEqual(res["clicks"], 2000)
        self.assertEqual(res["bot_starts"], 1000)
        self.assertEqual(res["qualified_leads"], 200)
        self.assertEqual(res["orders_closed"], 20)
        self.assertEqual(res["projected_revenue"], 1000.0)

    def test_ladder_phase_split(self) -> None:
        res = self.calc.calc_testing_ladder(total_budget=1000.0, breakeven_cpa=15.0)
        phases = res["phases"]
        self.assertEqual(phases["phase_1_sandbox"]["allocated_budget"], 150.0)
        self.assertEqual(phases["phase_2_validation"]["allocated_budget"], 350.0)
        self.assertEqual(phases["phase_3_scale"]["allocated_budget"], 500.0)


def _ns():
    import argparse
    return argparse.Namespace()


if __name__ == "__main__":
    unittest.main(verbosity=2)


class InstinctsTests(unittest.TestCase):
    """instincts — ECC continuous learning va marketing instinktlari reestri."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "instincts.py"), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_check_passes(self) -> None:
        proc = self._run("check")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("butun", proc.stdout)

    def test_list_by_domain(self) -> None:
        proc = self._run("list", "--domain", "meta")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("meta-asc-existing-cap-25", proc.stdout)

    def test_add_dry_run_changes_nothing(self) -> None:
        manifest = VAULT / "manifests" / "instincts.json"
        before = manifest.read_bytes()
        proc = self._run(
            "add", "--id", "test-instinct-dry", "--domain", "meta",
            "--trigger", "Sinov holati", "--action", "Sinov qoidasi",
            "--evidence", "wiki/learning-phase-qoidalari.md", "--confidence", "4", "--dry-run"
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(manifest.read_bytes(), before)

    def test_promote_dry_run(self) -> None:
        proc = self._run("promote", "kreativ-ftir-fatigue-radar", "--dry-run")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("REJA (dry-run)", proc.stdout)


class TyrionShieldTests(unittest.TestCase):
    """tyrion-shield — ECC AgentShield xavfsizlik va governance skaneri."""

    def test_shield_scan_passes_with_zero_errors(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "tyrion-shield.py"), "scan", "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["summary"]["errors"], 0, payload)
        self.assertEqual(payload["summary"]["warnings"], 0, payload)
        self.assertEqual(payload["summary"]["ok"], 5, payload)


class CharterBaselineAndGateTests(unittest.TestCase):
    """70-charter-baseline, vault-audit --gate va hook pre:guard."""

    def test_charter_baseline_rule_exists(self) -> None:
        rule = VAULT / "rules" / "70-charter-baseline.md"
        self.assertTrue(rule.is_file())
        text = rule.read_text(encoding="utf-8")
        self.assertIn("Prompt Defense Baseline", text)
        self.assertIn("Zero Findings", text)

    def test_all_35_agents_have_skills_attached(self) -> None:
        import importlib
        ss = importlib.import_module("skill-search")
        agents = ss.load_agents()
        self.assertEqual(len(agents), 36)
        unattached = [name for name, a in agents.items() if not a["skills"]]
        self.assertEqual(unattached, [], f"Skillsiz qolgan agentlar: {unattached}")

    def test_vault_audit_gate_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "vault-audit.py"), str(VAULT), "--gate"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("JAMI MUAMMO (bilim qatlami): 0", proc.stdout)

    def test_hook_guard_protects_generated_catalog(self) -> None:
        env = dict(**os.environ, TYRION_HOOK_PROFILE="strict")
        proc = subprocess.run(
            [sys.executable, str(VAULT / "hooks" / "tyrion-hook.py"), "guard", "--target", "manifests/catalog.json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("HIMOYA (pre:guard)", proc.stdout)


class MetaAudienceTests(unittest.TestCase):
    """meta-audience — Meta Ads Andromeda 2 auditoriya arxitekturasi, overlap va saturation."""

    def setUp(self) -> None:
        import importlib
        self.ma = importlib.import_module("meta-audience")

    def test_architect_builds_4_layers_and_exclusions(self) -> None:
        res = self.ma.build_architecture(
            niche="ecom", daily_budget=150.0, geo="tashkent", has_pixel=True, has_crm=True
        )
        self.assertEqual(len(res["audience_layers"]), 4)
        self.assertEqual(len(res["exclusion_matrix"]), 4)
        self.assertIn("Purchase_180d", res["audience_layers"][0]["exclusions"])

    def test_overlap_detects_collision_and_healthy_isolation(self) -> None:
        high = self.ma.calc_overlap(size_a=180000, size_b=120000, shared=45000)
        self.assertEqual(high["status"], "CRITICAL_COLLISION")
        self.assertAlmostEqual(high["overlap_of_smaller_pct"], 37.5, places=1)

        low = self.ma.calc_overlap(size_a=200000, size_b=150000, shared=15000)
        self.assertEqual(low["status"], "HEALTHY_ISOLATION")
        self.assertEqual(low["overlap_of_smaller_pct"], 10.0)

    def test_saturation_calculates_fatigue_day(self) -> None:
        sat = self.ma.calc_saturation(audience_size=250000, daily_budget=80.0, cpm=3.2, days=14)
        self.assertEqual(sat["status"], "HEALTHY_CAPACITY")
        self.assertGreater(sat["estimated_fatigue_day"], 14.0)

        oversat = self.ma.calc_saturation(audience_size=30000, daily_budget=150.0, cpm=4.0, days=14)
        self.assertEqual(oversat["status"], "OVERSATURATED_HIGH_RISK")

    def test_interests_returns_curated_taxonomy(self) -> None:
        info = self.ma.get_interests(niche="real-estate")
        self.assertIn("Real estate", info["core_interest_clusters"])
        self.assertTrue(info["uzbekistan_solventnost_filters"])

    def test_retargeting_builds_4_windows(self) -> None:
        res = self.ma.calc_retargeting(aov=250.0, daily_visitors=400, ig_engagers_30d=12000, video_viewers_14d=18000)
        self.assertEqual(len(res["retargeting_windows"]), 4)
        self.assertGreater(res["recommended_retargeting_daily_budget_usd"], 0)

    def test_lookalike_scores_seed_quality(self) -> None:
        strong = self.ma.calc_lookalike(seed_size=1200, seed_type="purchase_ltv", country="UZ")
        self.assertEqual(strong["seed_quality_score_100"], 100)
        self.assertEqual(len(strong["lal_tiers"]), 4)

        weak = self.ma.calc_lookalike(seed_size=80, seed_type="ig_engagers", country="UZ")
        self.assertLess(weak["seed_quality_score_100"], 40)

    def test_diagnose_identifies_hook_and_lp_bottlenecks(self) -> None:
        diag = self.ma.diagnose_metrics(cpm=3.5, ctr=0.6, cpc=0.58, lp_cvr=12.0, lead_to_sale=10.0)
        self.assertEqual(diag["overall_health"], "CRITICAL_BOTTLENECK_FOUND")
        self.assertTrue(any(b["stage"] == "HOOK_AND_CREATIVE_STOP_RATE" for b in diag["bottlenecks"]))


class CreativeMatrixAndWorkspaceTests(unittest.TestCase):
    """Tyrion v3.0 — creative-matrix.py, client-workspace.py va tyrion.py master CLI testlari."""

    def test_creative_matrix_builds_9_cells(self) -> None:
        import importlib
        cm = importlib.import_module("creative-matrix")
        res = cm.build_matrix(niche="ecom", product="Kostyum", price=150.0)
        self.assertEqual(len(res["matrix_3x3"]), 9)

    def test_creative_hooks_generates_3_languages(self) -> None:
        import importlib
        cm = importlib.import_module("creative-matrix")
        res = cm.generate_hooks(niche="edtech", offer="IELTS 7.0 3 oyda")
        for lang in ("uz_latin", "uz_cyrillic", "ru"):
            self.assertIn(lang, res["hooks_by_language"])
            self.assertGreaterEqual(len(res["hooks_by_language"][lang]), 3)

    def test_creative_fatigue_detects_weak_hook(self) -> None:
        import importlib
        cm = importlib.import_module("creative-matrix")
        res = cm.analyze_fatigue(hook_rate=18.0, hold_rate=15.0, ctr_drop_pct=10.0, frequency=1.5, ftir=70.0)
        self.assertEqual(res["status"], "WEAK_3S_HOOK")

    def test_client_workspace_scaffolds_5_files(self) -> None:
        import importlib
        cw = importlib.import_module("client-workspace")
        with tempfile.TemporaryDirectory() as tmp:
            res = cw.scaffold_client(
                client="Test Brand", niche="real-estate", monthly_budget=3000.0,
                aov=45000.0, margin_pct=25.0, geo="tashkent", root=Path(tmp), dry_run=False
            )
            cdir = Path(res["workspace_dir"])
            for fname in ("BRIEF.md", "AUDIENCE-MAP.md", "CREATIVE-MATRIX.md", "TRACKING-CHECKLIST.md", "journal.md"):
                self.assertTrue((cdir / fname).is_file(), f"Yaratilmadi: {fname}")

    def test_tyrion_master_cli_status(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "tyrion.py"), "status"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("TYRION v4.0", proc.stdout)
        self.assertIn("Single-Root ECC v4.0", proc.stdout)


class TyrionV4EnginesTests(unittest.TestCase):
    """Tyrion v4.0 — Ad Export & Breakdown Effect, CAPI v22 & UTM, MCP Server, Multi-Harness Exporter va Eval Suite testlari."""

    def test_breakdown_effect_detects_marginal_cpa_trap(self) -> None:
        import importlib
        ae = importlib.import_module("ad-export-analyzer")
        trap = ae.analyze_breakdown_effect("IG Reels", 750.0, 50, "FB Feed", 150.0, 12)
        self.assertTrue(trap["breakdown_effect_trap_detected"])
        self.assertGreater(trap["projected_cpa_if_dominant_paused_usd"], trap["blended_cpa_usd"])

        balanced = ae.analyze_breakdown_effect("IG Reels", 400.0, 25, "FB Feed", 380.0, 24)
        self.assertFalse(balanced["breakdown_effect_trap_detected"])

    def test_ad_export_analyzer_parses_demo_json(self) -> None:
        import importlib
        ae = importlib.import_module("ad-export-analyzer")
        demo_file = VAULT / "examples" / "demo-brand" / "assets" / "meta_performance.json"
        res = ae.analyze_export(demo_file, target_cpa=15.0, breakeven_roas=2.0)
        self.assertGreater(res["total_items"], 0)
        self.assertIn("blended_cpa_usd", res["summary"])
        self.assertTrue(all("verdict" in d for d in res["decisions"]))

    def test_capi_v22_payload_hashes_pii_and_scores_emq(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        res = cu.build_capi_payload("Lead", phone="+998 (90) 123-45-67", email="Test@Brand.uz", city="Tashkent", value=200.0, order_id="ORD_55")
        self.assertGreaterEqual(res["estimated_emq_score_10"], 8.0)
        ud = res["capi_v22_payload"]["data"][0]["user_data"]
        # SHA-256 hex digest is 64 chars, never plaintext phone/email
        self.assertEqual(len(ud["ph"][0]), 64)
        self.assertEqual(len(ud["em"][0]), 64)
        self.assertNotIn("1234567", ud["ph"][0])

    def test_telegram_bot_utm_enforces_64_char_limit(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        res = cu.build_utm_links("https://brand.uz/offer", "meta", "very_long_campaign_name_exceeding_normal_limits_2026_test", "my_brand_bot")
        tg = res["telegram_bot_tracking"]
        self.assertTrue(tg["within_64_char_limit"])
        self.assertLessEqual(tg["payload_length"], 64)
        self.assertIn("{{campaign.name}}", res["full_tracked_url"])

    def test_mcp_server_jsonrpc_initialize_and_tool_call(self) -> None:
        import importlib
        mcp = importlib.import_module("tyrion-mcp-server")
        init_resp = mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(init_resp["result"]["serverInfo"]["name"], "tyrion-mcp-server")

        list_resp = mcp.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertGreaterEqual(len(list_resp["result"]["tools"]), 7)

        call_resp = mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "tyrion_media_calculator", "arguments": {"price": 120, "cogs": 50, "shipping": 10}},
        })
        payload = json.loads(call_resp["result"]["content"][0]["text"])
        self.assertAlmostEqual(payload["breakeven_roas"], 2.08, places=2)

    def test_harness_exporter_dry_run_and_cursor_mdc(self) -> None:
        import importlib
        he = importlib.import_module("harness-export")
        with tempfile.TemporaryDirectory() as tmp:
            files = he.export_cursor(Path(tmp), dry_run=False)
            self.assertEqual(len(files), 8)
            sample = (Path(tmp) / files[0]).read_text(encoding="utf-8")
            self.assertIn("alwaysApply: true", sample)

    def test_skill_eval_suite_passes_100_pct(self) -> None:
        import importlib
        se = importlib.import_module("skill-eval")
        summary = se.run_evals()
        self.assertEqual(summary["failed"], 0, summary)
        self.assertEqual(summary["pass_rate_pct"], 100.0)

    def test_visual_studio_html_exists_and_has_5_tabs(self) -> None:
        studio = TOOLS / "tyrion-studio.html"
        self.assertTrue(studio.is_file())
        html = studio.read_text(encoding="utf-8")
        for tab_id in ("aud", "bd", "econ", "creo", "utm"):
            self.assertIn(f'id="{tab_id}"', html)

    def test_mcp_json_has_tyrion_core_server(self) -> None:
        mcp_cfg = json.loads((VAULT / ".mcp.json").read_text(encoding="utf-8"))
        self.assertIn("tyrion-core", mcp_cfg.get("mcpServers", {}))
        self.assertIn("meta-ads", mcp_cfg.get("mcpServers", {}))
        self.assertIn("google-ads", mcp_cfg.get("mcpServers", {}))

    def test_windsurf_export_creates_windsurfrules(self) -> None:
        import importlib
        he = importlib.import_module("harness-export")
        with tempfile.TemporaryDirectory() as tmp:
            files = he.export_windsurf(Path(tmp), dry_run=False)
            self.assertEqual(files, [".windsurfrules"])
            self.assertTrue((Path(tmp) / ".windsurfrules").is_file())

    def test_capi_phone_normalization_uzbekistan(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        self.assertEqual(cu.normalize_phone("90 123-45-67"), "998901234567")
        self.assertEqual(cu.normalize_phone("+998 (97) 700-11-22"), "998977001122")

    def test_google_utm_uses_value_track_macros(self) -> None:
        import importlib
        cu = importlib.import_module("capi-utm-builder")
        res = cu.build_utm_links("https://brand.uz", "google", "search_coliseum")
        self.assertIn("{campaignid}", res["full_tracked_url"])
        self.assertIn("{keyword}", res["full_tracked_url"])

    def test_ad_export_wasted_spend_detection(self) -> None:
        import importlib
        ae = importlib.import_module("ad-export-analyzer")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "export.json"
            p.write_text(json.dumps([
                {"name": "Bleeder_Set", "spend": 60.0, "conversions": 0, "revenue": 0},
                {"name": "Winner_Set", "spend": 100.0, "conversions": 20, "revenue": 500.0},
            ]), encoding="utf-8")
            res = ae.analyze_export(p, target_cpa=15.0, breakeven_roas=2.0)
            self.assertEqual(res["summary"]["estimated_wasted_spend_usd"], 60.0)
            self.assertEqual(res["decisions"][0]["verdict"], "KILL_ZERO_CONV")

    def test_all_100_wiki_notes_have_zero_orphans(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "vault-audit.py"), str(VAULT)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertIn("[ORPHAN QAYD] 0", proc.stdout)
        self.assertIn("JAMI MUAMMO (bilim qatlami): 0", proc.stdout)

    def test_no_hardcoded_windows_drive_paths_in_skills_or_commands(self) -> None:
        for folder in ("skills", "commands", "rules", "contexts", "playbooks"):
            for md in (VAULT / folder).rglob("*.md"):
                txt = md.read_text(encoding="utf-8")
                self.assertNotIn("D:\tyrion", txt, f"Hardcoded D:\tyrion in {md}")
                self.assertNotIn("D:\projects", txt, f"Hardcoded D:\projects in {md}")


class ProductionHardeningTests(unittest.TestCase):
    """Tyrion v4.1 — Atomic I/O, Secret Redaction, NaN/Inf Guards, Path Traversal & JSON-RPC Edge Cases."""

    def setUp(self) -> None:
        import importlib
        self.tcore = importlib.import_module("tyrion_core")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def test_redact_secrets_masks_meta_openai_and_telegram_tokens(self) -> None:
        raw = "Failed with token EAAbcdefghijklmnopqrstuvwxyz0123456789 and sk-proj1234567890abcdefghijkl"
        cleaned = self.tcore.redact_secrets(raw)
        self.assertNotIn("EAAbcdef", cleaned)
        self.assertNotIn("sk-proj", cleaned)
        self.assertIn("[REDACTED_SECRET]", cleaned)

    def test_safe_float_rejects_nan_infinity_and_negative_bounds(self) -> None:
        self.assertEqual(self.tcore.safe_float("nan", default=12.5), 12.5)
        self.assertEqual(self.tcore.safe_float("inf", default=5.0), 5.0)
        self.assertEqual(self.tcore.safe_float("$1,250.50"), 1250.50)
        with self.assertRaises(ValueError):
            self.tcore.safe_float(-5.0, min_val=0.0, field_name="budget")

    def test_safe_slug_prevents_empty_and_path_traversal(self) -> None:
        self.assertEqual(self.tcore.safe_slug("../../../etc/passwd"), "etc-passwd")
        self.assertEqual(self.tcore.safe_slug("---", fallback="default-client"), "default-client")

    def test_validate_safe_path_blocks_directory_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            safe = self.tcore.validate_safe_path(root / "client-a", allowed_root=root)
            self.assertTrue(str(safe).startswith(str(root.resolve())))
            with self.assertRaises(PermissionError):
                self.tcore.validate_safe_path(root / ".." / "escaped", allowed_root=root)

    def test_sanitize_url_blocks_javascript_and_data_uris(self) -> None:
        with self.assertRaises(ValueError):
            self.tcore.sanitize_url("javascript:alert(1)")
        with self.assertRaises(ValueError):
            self.tcore.sanitize_url("data:text/html,<script>alert(1)</script>")
        self.assertEqual(self.tcore.sanitize_url("https://brand.uz/offer\r\n"), "https://brand.uz/offer")

    def test_atomic_write_json_rejects_nan_and_writes_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "state.json"
            self.tcore.atomic_write_json(target, {"status": "ok", "count": 42})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["count"], 42)
            with self.assertRaises(ValueError):
                self.tcore.atomic_write_json(target, {"bad": float("nan")})

    def test_mcp_server_returns_32700_on_malformed_json(self) -> None:
        resp = self.mcp.process_raw_line("{invalid json")
        self.assertEqual(resp["error"]["code"], -32700)

    def test_mcp_server_returns_32601_on_unknown_method(self) -> None:
        resp = self.mcp.handle_request({"jsonrpc": "2.0", "id": 99, "method": "unknown/method"})
        self.assertEqual(resp["error"]["code"], -32601)

    def test_mcp_server_returns_32602_on_negative_budget(self) -> None:
        resp = self.mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {"name": "tyrion_meta_audience", "arguments": {"niche": "ecom", "daily_budget": -50}},
        })
        self.assertEqual(resp["error"]["code"], -32602)

