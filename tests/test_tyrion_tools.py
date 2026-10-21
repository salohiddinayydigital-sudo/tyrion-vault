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

import contextlib
import io
import importlib

_CLI_MOD_CACHE: dict[str, object] = {}

def _run_tool_inproc(script_name: str, *args: str) -> subprocess.CompletedProcess:
    mod_name = script_name[:-3] if script_name.endswith(".py") else script_name
    if mod_name not in _CLI_MOD_CACHE:
        _CLI_MOD_CACHE[mod_name] = importlib.import_module(mod_name)
    mod = _CLI_MOD_CACHE[mod_name]
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    old_argv = sys.argv[:]
    sys.argv = [script_name, *args]
    rc = 0
    try:
        with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
            main_fn = getattr(mod, "main")
            import inspect
            sig = inspect.signature(main_fn)
            if len(sig.parameters) >= 1:
                res = main_fn(list(args))
            else:
                res = main_fn()
            rc = int(res) if res is not None else 0
    except SystemExit as exc:
        rc = int(exc.code) if isinstance(exc.code, int) else (1 if exc.code else 0)
    finally:
        sys.argv = old_argv
    return subprocess.CompletedProcess(args=[script_name, *args], returncode=rc, stdout=out_buf.getvalue(), stderr=err_buf.getvalue())



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
        before = catalog.MANIFEST.read_bytes() if catalog.MANIFEST.is_file() else None
        try:
            self.assertEqual(catalog.cmd_build(_ns()), 0)
            self.assertEqual(catalog.cmd_check(_ns()), 0)
        finally:
            if before is None and catalog.MANIFEST.is_file():
                catalog.MANIFEST.unlink()
            elif before is not None:
                catalog.MANIFEST.write_bytes(before)

    def test_check_detects_stale_manifest(self) -> None:
        """Katalog eskirsa `check` xato qaytarishi kerak (jim qolmasligi)."""
        original_bytes = catalog.MANIFEST.read_bytes()
        try:
            data = json.loads(original_bytes.decode("utf-8"))
            data["counts"]["wiki"] = -1
            catalog.MANIFEST.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertNotEqual(catalog.cmd_check(_ns()), 0, "eskirgan katalog sezilmadi")
        finally:
            catalog.MANIFEST.write_bytes(original_bytes)

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
        proc = _run_tool_inproc("doctor.py", "--quick", "--json")
        self.assertIn(proc.returncode, (0, 1), f"kutilmagan kod: {proc.returncode}\n{proc.stderr}")
        payload = json.loads(proc.stdout)
        self.assertIn("checks", payload)
        self.assertGreater(len(payload["checks"]), 5)


class BrainSearchTests(unittest.TestCase):
    """brain-search — LLM'siz (deterministik) qidiruv, token tejamkor."""

    def _run(self, *args):
        return _run_tool_inproc("brain-search.py", *args)

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
        return _run_tool_inproc("skill-search.py", *args)

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
        return _run_tool_inproc("skill-attach.py", *args)

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
        return _run_tool_inproc("video-run.py", *args)

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
        g_json = VAULT / "graphify-out" / "graph.json"
        g_rep = VAULT / "graphify-out" / "GRAPH_REPORT.md"
        before_json = g_json.read_bytes() if g_json.is_file() else None
        before_rep = g_rep.read_bytes() if g_rep.is_file() else None
        try:
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
        finally:
            if before_json is not None:
                g_json.write_bytes(before_json)
            if before_rep is not None:
                g_rep.write_bytes(before_rep)

    def test_graph_has_nodes_and_links(self) -> None:
        graph = VAULT / "graphify-out" / "graph.json"
        self.assertTrue(graph.is_file(), "graph.json yo'q")
        data = json.loads(graph.read_text(encoding="utf-8"))
        self.assertGreater(data["stats"]["nodes"], 50)
        self.assertGreater(data["stats"]["links"], 50)
        self.assertIn("community", data["nodes"][0])


class VaultAuditTests(unittest.TestCase):
    def test_vault_audit_runs(self) -> None:
        proc = _run_tool_inproc("vault-audit.py", str(VAULT))
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
        g_json = VAULT / "graphify-out" / "graph.json"
        g_rep = VAULT / "graphify-out" / "GRAPH_REPORT.md"
        c_json = catalog.MANIFEST
        saved = {
            f: f.read_bytes() for f in (g_json, g_rep, c_json) if f.is_file()
        }
        try:
            cases = {
                "brief": [],
                "ingest": ["--warn-only", "--quiet"],
            }
            for mode, flags in cases.items():
                proc = subprocess.run(
                    [sys.executable, str(VAULT / "hooks" / "tyrion-hook.py"), mode, *flags],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
                )
                self.assertEqual(proc.returncode, 0, f"{mode}: {proc.stderr[-300:]}")
        finally:
            for f, raw in saved.items():
                f.write_bytes(raw)



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
        return _run_tool_inproc("instincts.py", *args)

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
        proc = _run_tool_inproc("tyrion-shield.py", "scan", "--json")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["summary"]["errors"], 0, payload)
        self.assertEqual(payload["summary"]["warnings"], 0, payload)
        self.assertEqual(payload["summary"]["ok"], 6, payload)


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
        proc = _run_tool_inproc("vault-audit.py", str(VAULT), "--gate")
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
        self.assertIn("TYRION v5.0.0", proc.stdout)
        self.assertIn("Single-Root ECC v5.0.0", proc.stdout)


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
        proc = _run_tool_inproc("vault-audit.py", str(VAULT))
        self.assertIn("[ORPHAN QAYD] 0", proc.stdout)
        self.assertIn("JAMI MUAMMO (bilim qatlami): 0", proc.stdout)

    def test_no_hardcoded_windows_drive_paths_in_skills_or_commands(self) -> None:
        for folder in ("skills", "commands", "rules", "contexts", "playbooks"):
            for md in (VAULT / folder).rglob("*.md"):
                txt = md.read_text(encoding="utf-8")
                self.assertNotIn("D:\tyrion", txt, f"Hardcoded D:\tyrion in {md}")
                self.assertNotIn(r"D:\projects", txt, f"Hardcoded D:\\projects in {md}")


class ProductionHardeningTests(unittest.TestCase):
    """Tyrion v4.1 — Atomic I/O, Secret Redaction, NaN/Inf Guards, Path Traversal & JSON-RPC Edge Cases."""

    def setUp(self) -> None:
        import importlib
        self.tcore = importlib.import_module("tyrion_core")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def test_redact_secrets_masks_meta_openai_and_telegram_tokens(self) -> None:
        raw = "Failed with token " + "EAA" + "bcdefghijklmnopqrstuvwxyz0123456789" + " and " + "sk-" + "proj1234567890abcdefghijkl"
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


class TyrionV5CalibratedAuditTests(unittest.TestCase):
    """Tyrion v5.0 — 8 ta texnik audit kamchiligini yopuvchi maxsus regressiya testlari."""

    def setUp(self) -> None:
        import importlib
        self.ma = importlib.import_module("meta-audience")
        self.cu = importlib.import_module("capi-utm-builder")
        self.mis = importlib.import_module("meta-insights-sync")
        self.shield = importlib.import_module("tyrion-shield")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def test_audit_1_saturation_confidence_intervals_and_model_disclosure(self) -> None:
        sat_heur = self.ma.calc_saturation(audience_size=200000, daily_budget=80.0, cpm=3.2, days=14, active_reach_ratio=0.55)
        self.assertEqual(sat_heur["active_reach_ratio"], 0.55)
        self.assertEqual(sat_heur["estimated_reachable_pool"], 110000)
        win = sat_heur["estimated_fatigue_window_days"]
        self.assertLess(win["conservative_early_fatigue_day"], win["baseline_fatigue_day"])
        self.assertGreater(win["optimistic_late_fatigue_day"], win["baseline_fatigue_day"])
        self.assertEqual(sat_heur["model_disclosure"]["data_source_type"], "HEURISTIC_PRIOR_MODEL")

        sat_meas = self.ma.calc_saturation(audience_size=200000, daily_budget=80.0, cpm=3.2, days=14, measured_freq_7d=1.75)
        self.assertEqual(sat_meas["model_disclosure"]["data_source_type"], "MEASURED_ACCOUNT_DATA")
        self.assertIn("MODERATE_CALIBRATED_LINEAR_PROJECTION", sat_meas["model_disclosure"]["confidence_level"])
        self.assertAlmostEqual(sat_meas["projected_frequency"], 3.5, places=2)

    def test_audit_2_overlap_unified_20pct_threshold_and_auction_disclaimer(self) -> None:
        healthy = self.ma.calc_overlap(size_a=100000, size_b=100000, shared=19000)
        self.assertEqual(healthy["status"], "HEALTHY_ISOLATION")
        self.assertEqual(healthy["threshold_policy_pct"], 20.0)
        self.assertEqual(healthy["metric_type"], "STATIC_AUDIENCE_POOL_INTERSECTION")
        self.assertIn("Static Pool Overlap", healthy["auction_competition_disclaimer"])

        moderate = self.ma.calc_overlap(size_a=100000, size_b=100000, shared=21000)
        self.assertEqual(moderate["status"], "MODERATE_OVERLAP")

        critical = self.ma.calc_overlap(size_a=100000, size_b=100000, shared=31000)
        self.assertEqual(critical["status"], "CRITICAL_COLLISION")

    def test_audit_3_live_meta_insights_sync_and_mcp_integration(self) -> None:
        raw_file = VAULT / "examples" / "demo-brand" / "assets" / "meta_graph_insights_raw.json"
        res = self.mis.sync_and_analyze(from_raw_json=raw_file, target_cpa=15.0, breakeven_roas=2.0)
        self.assertEqual(res["graph_api_version"], "v26.0")
        self.assertEqual(res["normalized_rows_count"], 3)
        self.assertEqual(res["audit_report"]["summary"]["total_conversions"], 33)
        verdicts = {d["name"]: d["verdict"] for d in res["audit_report"]["decisions"]}
        self.assertEqual(verdicts["L1_Broad_UZ_22_54"], "SCALE (+20% / 48h)")
        self.assertEqual(verdicts["L2_Narrow_Luxury_Stack"], "KILL_ZERO_CONV")

        mcp_resp = self.mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 501,
            "method": "tools/call",
            "params": {
                "name": "tyrion_meta_live_insights",
                "arguments": {"from_raw_json": "examples/demo-brand/assets/meta_graph_insights_raw.json", "target_cpa": 15.0},
            },
        })
        payload = json.loads(mcp_resp["result"]["content"][0]["text"])
        self.assertEqual(payload["normalized_rows_count"], 3)

    def test_audit_4_unit_economics_cpa_and_lookalike_readiness_disclosure(self) -> None:
        econ_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=80.0, margin_pct=35.0)
        self.assertEqual(econ_arch["evidence_and_assumptions"]["cpa_source"], "UNIT_ECONOMICS_DERIVED")
        self.assertEqual(econ_arch["estimated_target_cpa_usd"], 18.2)

        fallback_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0)
        self.assertEqual(fallback_arch["evidence_and_assumptions"]["cpa_source"], "PROVISIONAL_HEURISTIC_FALLBACK")

        lal = self.ma.calc_lookalike(seed_size=500, seed_type="qualified_leads", country="UZ")
        self.assertIn("heuristic_seed_readiness_score_100", lal)
        self.assertFalse(lal["model_disclosure"]["is_meta_internal_score"])

    def test_audit_5_retargeting_no_telegram_bot_flag_and_zero_pool_honesty(self) -> None:
        proc = subprocess.run(
            [
                sys.executable, str(TOOLS / "meta-audience.py"),
                "retargeting", "--aov", "100", "--daily-visitors", "0",
                "--ig-engagers", "0", "--video-viewers", "0", "--no-telegram-bot", "--json",
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertFalse(data["has_telegram_bot"])
        self.assertEqual(data["total_retargetable_pool"], 0)
        self.assertEqual(data["recommended_retargeting_daily_budget_usd"], 0.0)
        self.assertEqual(data["retargeting_readiness"], "INSUFFICIENT_RETARGETING_POOL")
        for w in data["retargeting_windows"]:
            self.assertEqual(w["estimated_pool"], 0)
            self.assertFalse(w["window_viable"])
            self.assertNotIn("Telegram_Bot_Started_No_Contact_7d", w["sources"])

    def test_audit_5c_no_unreachable_dead_code_in_any_tool(self) -> None:
        status, detail, items = self.shield.scan_python_ast()
        self.assertEqual(status, "ok", f"Dead code or AST error found: {items}")
        self.assertEqual(items, [])

    def test_audit_6_tyrion_shield_scans_tests_and_discloses_scope(self) -> None:
        self.assertNotIn("tests", self.shield.SKIP_DIRS)
        res = self.shield.run_all()
        self.assertEqual(res["summary"]["errors"], 0)
        self.assertTrue(res["scope_and_limitations"]["tests_directory_scanned"])
        self.assertGreaterEqual(len(res["scope_and_limitations"]["non_covered_risks"]), 2)

    def test_audit_7_version_and_inventory_parity_across_all_manifests_and_docs(self) -> None:
        counts = catalog.scan()["counts"]
        self.assertEqual(counts["agents"], 36)
        self.assertEqual(counts["skills"], 62)
        self.assertEqual(counts["commands"], 18)
        self.assertEqual(counts["wiki"], 100)

        for jpath in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "package.json"):
            jdata = json.loads((VAULT / jpath).read_text(encoding="utf-8"))
            self.assertEqual(jdata["version"], "5.0.0", f"Version drift in {jpath}")

        mp = json.loads((VAULT / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(mp["metadata"]["version"], "5.0.0")
        self.assertEqual(mp["plugins"][0]["version"], "5.0.0")
        self.assertIn("36 specialist agents", mp["metadata"]["description"])

        sec_txt = (VAULT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("36 agents", sec_txt)
        self.assertIn("62 skills", sec_txt)

    def test_audit_8_graph_api_defaults_to_v26_and_interpolates_dynamically(self) -> None:
        info_default = self.ma.get_interests("ecom")
        self.assertEqual(info_default["graph_api_version"], "v26.0")
        self.assertIn("/v26.0/search", info_default["graph_api_readonly_endpoint"])

        old_env = os.environ.get("META_GRAPH_API_VERSION")
        try:
            os.environ["META_GRAPH_API_VERSION"] = "v27.0"
            info_custom = self.ma.get_interests("ecom")
            self.assertEqual(info_custom["graph_api_version"], "v27.0")
            self.assertIn("/v27.0/search", info_custom["graph_api_readonly_endpoint"])
            self.assertNotIn("v22.0", info_custom["graph_api_readonly_endpoint"])

            capi_custom = self.cu.build_capi_payload("Lead", phone="+998901234567")
            self.assertEqual(capi_custom["graph_api_version"], "v27.0")
            self.assertIn("/v27.0/", capi_custom["capi_endpoint_template"])
        finally:
            if old_env is None:
                os.environ.pop("META_GRAPH_API_VERSION", None)
            else:
                os.environ["META_GRAPH_API_VERSION"] = old_env

    def test_audit_9_retargeting_has_telegram_bot_false_string_arg(self) -> None:
        proc = subprocess.run(
            [
                sys.executable, str(TOOLS / "meta-audience.py"),
                "retargeting", "--has-telegram-bot=false", "--daily-visitors", "500", "--json",
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertFalse(data["has_telegram_bot"])
        self.assertEqual(data["retargeting_readiness"], "READY_FOR_RETARGETING")

    def test_audit_10_live_insights_rejects_invalid_account_id(self) -> None:
        with self.assertRaises(ValueError):
            self.mis.normalize_account_id("invalid_acct_abc")
        self.assertEqual(self.mis.normalize_account_id("123456789"), "act_123456789")


class TyrionV51AuditTests(unittest.TestCase):
    """Tyrion v5.1 — Ikkinchi auditdagi 4 ta asosiy kamchilik va real HTTP server integratsiyasi testlari."""

    def setUp(self) -> None:
        self.ma = importlib.import_module("meta-audience")
        self.mis = importlib.import_module("meta-insights-sync")
        self.ae = importlib.import_module("ad-export-analyzer")

    def test_v51_1_live_http_pagination_account_currency_and_ssrf_guard(self) -> None:
        import http.server
        import threading

        received_auth_headers: list[str] = []

        class MockMetaGraphHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass

            def do_GET(self) -> None:
                received_auth_headers.append(self.headers.get("Authorization", ""))
                base_url = f"http://127.0.0.1:{self.server.server_port}"
                if self.path.startswith("/v26.0/act_777888999?"):
                    body = {
                        "id": "act_777888999",
                        "name": "Tashkent Ecom UZS Account",
                        "account_status": 1,
                        "currency": "UZS",
                        "timezone_name": "Asia/Tashkent",
                    }
                elif "after=cursor_page_2" in self.path:
                    body = {
                        "data": [
                            {
                                "adset_id": "adset_p2",
                                "adset_name": "Page2_Broad_Tashkent",
                                "account_currency": "UZS",
                                "spend": "1800000",
                                "impressions": "45000",
                                "reach": "30000",
                                "frequency": "1.50",
                                "actions": [{"action_type": "purchase", "value": "18"}],
                                "action_values": [{"action_type": "purchase", "value": "7200000"}],
                            }
                        ],
                        "paging": {"next": f"{base_url}/v26.0/act_777888999/insights?after=cursor_page_3"},
                    }
                elif "after=cursor_page_3" in self.path:
                    body = {
                        "data": [
                            {
                                "adset_id": "adset_p3",
                                "adset_name": "Page3_ZeroConv_Bleeder",
                                "account_currency": "UZS",
                                "spend": "950000",
                                "impressions": "15000",
                                "reach": "5000",
                                "frequency": "3.00",
                                "actions": [],
                                "action_values": [],
                            }
                        ],
                        "paging": {},
                    }
                else:
                    body = {
                        "data": [
                            {
                                "adset_id": "adset_p1",
                                "adset_name": "Page1_Winner_Set",
                                "account_currency": "UZS",
                                "spend": "2000000",
                                "impressions": "60000",
                                "reach": "40000",
                                "frequency": "1.50",
                                "actions": [{"action_type": "purchase", "value": "25"}],
                                "action_values": [{"action_type": "purchase", "value": "9000000"}],
                            }
                        ],
                        "paging": {"next": f"{base_url}/v26.0/act_777888999/insights?after=cursor_page_2"},
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), MockMetaGraphHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{server.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "test_live_bearer_token_v51"

            ver = self.mis.verify_live_connection("777888999")
            self.assertTrue(ver["authenticated"])
            self.assertEqual(ver["account_currency"], "UZS")

            synced = self.mis.sync_and_analyze(
                account_id="act_777888999",
                level="adset",
                date_preset="last_7d",
                target_cpa=120000.0,
                breakeven_roas=2.0,
                max_pages=10,
            )
            self.assertEqual(synced["data_source_type"], "LIVE_META_GRAPH_API")
            self.assertEqual(synced["pagination"]["pages_fetched"], 3)
            self.assertFalse(synced["pagination"]["is_truncated"])
            self.assertEqual(synced["normalized_rows_count"], 3)
            self.assertEqual(synced["account_currency"], "UZS")
            self.assertEqual(synced["currency_source"], "META_ACCOUNT_CURRENCY")
            self.assertEqual(synced["audit_report"]["currency"], "UZS")
            self.assertEqual(synced["audit_report"]["summary"]["total_conversions"], 43)
            self.assertTrue(all(h == "Bearer test_live_bearer_token_v51" for h in received_auth_headers))

            with self.assertRaises(PermissionError):
                self.mis._validate_same_origin("https://evil.attacker.com/v26.0/steal", "https://graph.facebook.com")
        finally:
            server.shutdown()
            server.server_close()
            if old_base is None:
                os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else:
                os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None:
                os.environ.pop("META_ACCESS_TOKEN", None)
            else:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_v51_2_mixed_conversion_families_never_silently_blended(self) -> None:
        raw_mixed = [
            {
                "adset_id": "1",
                "adset_name": "Ecom_Purchase_Set",
                "account_currency": "USD",
                "spend": "200.0",
                "impressions": "20000",
                "reach": "10000",
                "actions": [{"action_type": "purchase", "value": "10"}],
                "action_values": [{"action_type": "purchase", "value": "600.0"}],
            },
            {
                "adset_id": "2",
                "adset_name": "B2B_LeadGen_Set",
                "account_currency": "USD",
                "spend": "150.0",
                "impressions": "15000",
                "reach": "8000",
                "actions": [{"action_type": "lead", "value": "30"}],
                "action_values": [],
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "mixed_insights.json"
            p.write_text(json.dumps({"account_id": "act_111", "data": raw_mixed}), encoding="utf-8")

            res_auto = self.mis.sync_and_analyze(from_raw_json=p, target_cpa=15.0, primary_conversion="auto")
            rep_auto = res_auto["audit_report"]
            self.assertTrue(rep_auto["mixed_conversion_types_detected"])
            self.assertEqual(rep_auto["active_conversion_families"], ["LEAD", "PURCHASE"])
            self.assertIsNone(rep_auto["summary"]["blended_cpa"])
            self.assertIsNone(rep_auto["summary"]["total_conversions"])
            self.assertEqual(rep_auto["summary_by_conversion_family"]["PURCHASE"]["cpa"], 20.0)
            self.assertEqual(rep_auto["summary_by_conversion_family"]["LEAD"]["cpa"], 5.0)

            res_purch = self.mis.sync_and_analyze(from_raw_json=p, target_cpa=15.0, primary_conversion="purchase")
            rep_purch = res_purch["audit_report"]
            self.assertFalse(rep_purch["mixed_conversion_types_detected"])
            self.assertEqual(rep_purch["summary"]["total_conversions"], 10)
            self.assertEqual(rep_purch["summary"]["blended_cpa"], 35.0)

    def test_v51_3_saturation_scenario_sensitivity_band_not_statistical_ci(self) -> None:
        sat = self.ma.calc_saturation(audience_size=200000, daily_budget=80.0, measured_freq_7d=1.75)
        win = sat["scenario_sensitivity_window_days"]
        self.assertFalse(win["is_statistical_confidence_interval"])
        self.assertIn("NOT_A_STATISTICAL_CONFIDENCE_INTERVAL", sat["model_disclosure"]["interval_methodology"])
        self.assertIn("MODERATE_CALIBRATED_LINEAR_PROJECTION", sat["model_disclosure"]["confidence_level"])
        self.assertNotEqual(sat["model_disclosure"]["confidence_level"], "HIGH")

    def test_v51_4_unit_economics_bounds_and_unverified_target_cpa_label(self) -> None:
        with self.assertRaises(ValueError):
            self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=100.0, margin_pct=150.0)
        with self.assertRaises(ValueError):
            self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=100.0, margin_pct=40.0, lead_to_sale_cvr=250.0)
        with self.assertRaises(ValueError):
            self.ma.build_architecture(niche="ecom", daily_budget=150.0, aov=100.0)

        goal_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0, target_cpa=15.0)
        self.assertEqual(goal_arch["evidence_and_assumptions"]["cpa_source"], "USER_SPECIFIED_TARGET_GOAL")
        self.assertEqual(goal_arch["evidence_and_assumptions"]["confidence_level"], "UNVERIFIED_USER_TARGET")

        meas_arch = self.ma.build_architecture(niche="ecom", daily_budget=150.0, measured_cpa=14.2)
        self.assertEqual(meas_arch["evidence_and_assumptions"]["cpa_source"], "MEASURED_HISTORICAL_CPA")
        self.assertEqual(meas_arch["evidence_and_assumptions"]["confidence_level"], "MODERATE_HISTORICAL_BASELINE")


class DetailedTargetingAccuracyTests(unittest.TestCase):
    """Tyrion v5.0 — Detailed Targeting Accuracy Engine uchun 12 ta majburiy avtomatlashtirilgan test."""

    def setUp(self) -> None:
        self.mte = importlib.import_module("meta-targeting-engine")
        self.ma = importlib.import_module("meta-audience")
        self.mcp = importlib.import_module("tyrion-mcp-server")

    def _with_mock_server(self, handler_cls):
        import http.server
        import threading
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server

    def test_dt_01_official_api_exact_match_preserves_original_name_and_id(self) -> None:
        import http.server

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                if "targetingvalidation" in self.path:
                    body = {"data": [{"id": "6003107902433", "name": "Online shopping", "valid": True}]}
                else:
                    body = {
                        "data": [
                            {
                                "id": "6003107902433",
                                "name": "Online shopping",
                                "type": "interests",
                                "path": ["Interests", "Shopping and fashion", "Online shopping"],
                                "audience_size_lower_bound": 450000,
                                "audience_size_upper_bound": 520000,
                            }
                        ]
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(Handler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "valid_test_token_12345"
            rep = self.mte.search_and_validate_targeting(
                queries=["Online shopping"], ad_account_id="act_123456", limit_per_query=5
            )
            self.assertEqual(len(rep["verified_targeting_options"]), 1)
            item = rep["verified_targeting_options"][0]
            self.assertEqual(item["id"], "6003107902433")
            self.assertEqual(item["name"], "Online shopping")
            self.assertEqual(item["validation_status"], "VERIFIED_AVAILABLE")
            self.assertEqual(item["audience_size_lower_bound"], 450000)
            self.assertEqual(item["audience_size_upper_bound"], 520000)
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_02_empty_api_response_never_hallucinates_interests(self) -> None:
        import http.server

        class EmptyHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                raw = json.dumps({"data": []}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(EmptyHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "valid_test_token_12345"
            rep = self.mte.search_and_validate_targeting(queries=["nonexistent_xyz_interest_999"], niche="ecom")
            self.assertEqual(rep["verified_targeting_options"], [])
            self.assertEqual(rep["recommended_audience_combinations"]["status"], "NO_VERIFIED_OPTIONS_AVAILABLE")
            self.assertEqual(rep["recommended_audience_combinations"]["combinations"], [])
            self.assertTrue(any(q["validation_status"] == "NOT_FOUND" for q in rep["not_found_queries"]))
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_03_missing_token_never_marks_static_names_verified(self) -> None:
        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            rep = self.mte.search_and_validate_targeting(product="Kiyim do'koni", niche="ecom")
            self.assertFalse(rep["live_check_status"]["executed"])
            self.assertEqual(rep["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(rep["verified_targeting_options"], [])
            self.assertTrue(all(x["validation_status"] == "RELATED_UNVERIFIED" for x in rep["related_unverified_ideas"]))
            self.assertTrue(all(x["is_verified_meta_option"] is False for x in rep["related_unverified_ideas"]))
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_04_http_401_and_403_handled_as_api_unavailable(self) -> None:
        import http.server

        for code, expected_cat in ((401, "AUTH_401"), (403, "PERMISSION_403")):
            class AuthErrHandler(http.server.BaseHTTPRequestHandler):
                def log_message(self, format: str, *args: object) -> None:
                    pass
                def do_GET(self) -> None:
                    raw = json.dumps({"error": {"message": "OAuthException", "code": 190}}).encode("utf-8")
                    self.send_response(code)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(raw)

            srv = self._with_mock_server(AuthErrHandler)
            old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
            try:
                os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
                os.environ["META_ACCESS_TOKEN"] = "expired_token_test"
                rep = self.mte.search_and_validate_targeting(queries=["Real estate"], niche="real-estate")
                self.assertEqual(rep["live_check_status"]["status"], "API_UNAVAILABLE")
                self.assertEqual(rep["live_check_status"]["error_category"], expected_cat)
                self.assertEqual(rep["verified_targeting_options"], [])
            finally:
                srv.shutdown()
                srv.server_close()
                if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
                else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
                if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
                else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_05_http_429_and_5xx_retry_backoff_and_recovery(self) -> None:
        import http.server
        attempts = {"count": 0}

        class FlakyHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                attempts["count"] += 1
                if attempts["count"] == 1:
                    self.send_response(429)
                    self.send_header("Retry-After", "0.05")
                    self.end_headers()
                    self.wfile.write(b'{"error": "rate limit"}')
                elif attempts["count"] == 2:
                    self.send_response(503)
                    self.end_headers()
                    self.wfile.write(b'{"error": "server busy"}')
                else:
                    raw = json.dumps({"data": [{"id": "777", "name": "Dentistry", "type": "adinterest"}]}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(raw)

        srv = self._with_mock_server(FlakyHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_retry_test"
            rep = self.mte.search_and_validate_targeting(queries=["Dentistry"], niche="medical", validate_results=False)
            self.assertGreaterEqual(attempts["count"], 3)
            self.assertEqual(len(rep["verified_targeting_options"]), 1)
            self.assertEqual(rep["verified_targeting_options"][0]["validation_status"], "FOUND_NOT_VALIDATED")
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_06_consolidated_or_invalid_interest_status_and_replacement_link(self) -> None:
        import http.server

        class ConsolidatedHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                if "targetingvalidation" in self.path:
                    body = {
                        "data": [
                            {
                                "id": "111_old",
                                "name": "Boutique",
                                "valid": False,
                                "status": "CONSOLIDATED",
                                "replacements": [{"id": "222_new", "name": "Shopping and fashion", "type": "interests"}],
                            },
                            {
                                "id": "222_new",
                                "name": "Shopping and fashion",
                                "valid": True,
                            },
                        ]
                    }
                else:
                    body = {
                        "data": [
                            {"id": "111_old", "name": "Boutique", "type": "interests"},
                            {"id": "222_new", "name": "Shopping and fashion", "type": "interests"},
                        ]
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(ConsolidatedHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_cons_test"
            rep = self.mte.search_and_validate_targeting(queries=["Boutique"], ad_account_id="act_555")
            self.assertEqual(len(rep["verified_targeting_options"]), 1)
            self.assertEqual(rep["verified_targeting_options"][0]["id"], "222_new")
            self.assertEqual(len(rep["unavailable_or_consolidated_options"]), 1)
            old_it = rep["unavailable_or_consolidated_options"][0]
            self.assertEqual(old_it["validation_status"], "UNAVAILABLE_OR_CONSOLIDATED")
            self.assertEqual(old_it["validation_details"]["consolidated_into"]["id"], "222_new")
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_07_same_name_different_ids_preserved_without_collision(self) -> None:
        import http.server

        class HomonymHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                body = {
                    "data": [
                        {"id": "600111", "name": "Real estate", "type": "interests"},
                        {"id": "600222", "name": "Real estate", "type": "interests"},
                    ]
                }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(HomonymHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_homonym"
            rep = self.mte.search_and_validate_targeting(queries=["Real estate"], validate_results=False)
            ids = [x["id"] for x in rep["verified_targeting_options"] if x["name"] == "Real estate"]
            self.assertEqual(ids, ["600111", "600222"])
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_08_pagination_collects_all_pages(self) -> None:
        import http.server

        class PaginatedSearchHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                base = f"http://127.0.0.1:{self.server.server_port}"
                if "page=2" in self.path:
                    body = {"data": [{"id": "p2_id", "name": "Luxury real estate", "type": "adinterest"}], "paging": {}}
                else:
                    body = {
                        "data": [{"id": "p1_id", "name": "Property investment", "type": "adinterest"}],
                        "paging": {"next": f"{base}/v26.0/search?type=adinterest&q=Property&page=2"},
                    }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(raw)

        srv = self._with_mock_server(PaginatedSearchHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_page"
            rep = self.mte.search_and_validate_targeting(queries=["Property"], max_pages_per_query=3, validate_results=False)
            ids = {x["id"] for x in rep["verified_targeting_options"]}
            self.assertIn("p1_id", ids)
            self.assertIn("p2_id", ids)
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_09_multilingual_queries_uz_latin_cyrillic_ru_en(self) -> None:
        self.assertEqual(self.mte.detect_query_language("Toshkentda ko'chmas mulk va xonadon"), "uz_latin")
        self.assertEqual(self.mte.detect_query_language("Тошкентда кўчмас мулк ва хонадон"), "uz_cyrillic")
        self.assertEqual(self.mte.detect_query_language("Недвижимость и квартира в Ташкенте"), "ru")
        self.assertEqual(self.mte.detect_query_language("Luxury real estate investment"), "en")

        for phrase in ("ko'chmas mulk", "кўчмас мулк", "недвижимость"):
            expanded = self.mte.expand_search_queries(product=phrase, niche="real-estate")
            q_strings = [x["query"] for x in expanded]
            self.assertIn("Real estate", q_strings)
            self.assertTrue(all(x["role"] == "SEARCH_QUERY_ONLY_NOT_VERIFIED_INTEREST" for x in expanded))

    def test_dt_10_malformed_json_empty_fields_and_unexpected_shapes_never_crash(self) -> None:
        import http.server
        mode = {"state": "bad_json"}

        class WeirdHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                if mode["state"] == "bad_json":
                    self.wfile.write(b"{not valid json")
                else:
                    body = {"data": [{"id": "", "name": ""}, {"id": "901", "name": "IELTS"}]}
                    self.wfile.write(json.dumps(body).encode("utf-8"))

        srv = self._with_mock_server(WeirdHandler)
        old_base, old_tok = os.environ.get("META_GRAPH_API_BASE_URL"), os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = f"http://127.0.0.1:{srv.server_port}"
            os.environ["META_ACCESS_TOKEN"] = "token_weird"
            rep_bad = self.mte.search_and_validate_targeting(queries=["IELTS"], validate_results=False)
            self.assertEqual(rep_bad["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(rep_bad["live_check_status"]["error_category"], "INVALID_JSON")

            mode["state"] = "partial_empty"
            rep_ok = self.mte.search_and_validate_targeting(queries=["IELTS"], validate_results=False)
            self.assertEqual(len(rep_ok["verified_targeting_options"]), 1)
            it = rep_ok["verified_targeting_options"][0]
            self.assertEqual(it["id"], "901")
            self.assertIsNone(it["audience_size_lower_bound"])
            self.assertIsNone(it["audience_size_upper_bound"])
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_11_mcp_tool_preserves_statuses_and_provenance(self) -> None:
        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            resp = self.mcp.handle_request({
                "jsonrpc": "2.0",
                "id": 77,
                "method": "tools/call",
                "params": {
                    "name": "tyrion_meta_detailed_targeting",
                    "arguments": {"product": "Стоматология", "niche": "medical", "special_ad_category": "NONE"},
                },
            })
            payload = json.loads(resp["result"]["content"][0]["text"])
            self.assertEqual(payload["schema"], "tyrion.detailed_targeting_accuracy/v5")
            self.assertEqual(payload["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(payload["verified_targeting_options"], [])
            self.assertTrue(len(payload["related_unverified_ideas"]) > 0)
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_dt_12_relevance_reason_and_expired_cache_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfile = Path(tmp) / "targeting_cache.json"
            expired_data = {
                "schema": "tyrion.targeting_cache/v5",
                "entries": {
                    "test_key": {
                        "api_version": "v26.0",
                        "fetched_at_utc": "2026-01-01T00:00:00Z",
                        "fetched_epoch": 1000.0,
                        "ttl_seconds": 60,
                        "query_params": {},
                        "payload": {"fake": True},
                    }
                },
            }
            cfile.write_text(json.dumps(expired_data), encoding="utf-8")
            loaded, cstat, warn = self.mte._load_valid_cache(cfile, "test_key", {"api_version": "v26.0"}, 60)
            self.assertIsNone(loaded)
            self.assertEqual(cstat, "EXPIRED")
            self.assertIn("Kesh muddati tugagan", warn)

            loaded_ver, cstat_ver, warn_ver = self.mte._load_valid_cache(cfile, "test_key", {"api_version": "v25.0"}, 60)
            self.assertIsNone(loaded_ver)
            self.assertEqual(cstat_ver, "VERSION_MISMATCH")
            self.assertIn("Kesh versiyasi eskirgan", warn_ver)


@unittest.skipUnless(
    os.environ.get("TYRION_RUN_LIVE_META_SMOKE") == "1" and os.environ.get("META_ACCESS_TOKEN"),
    "Ixtiyoriy live Meta API smoke testi: faqat TYRION_RUN_LIVE_META_SMOKE=1 va META_ACCESS_TOKEN berilganda ishlaydi.",
)
class LiveMetaSmokeTests(unittest.TestCase):
    def test_live_meta_targeting_smoke(self) -> None:
        mte = importlib.import_module("meta-targeting-engine")
        rep = mte.search_and_validate_targeting(queries=["Online shopping"], limit_per_query=5)
        self.assertTrue(rep["live_check_status"]["executed"])
        self.assertGreater(len(rep["verified_targeting_options"]), 0)


class PostImplementationFixTests(unittest.TestCase):
    """Part 1 Post-Implementation Verification: CRLF resilience, Pagination/Truncation, Malformed vs NOT_FOUND, Cache Isolation, CLI Docs."""

    def setUp(self) -> None:
        self.mte = importlib.import_module("meta-targeting-engine")
        self.ss = importlib.import_module("skill-search")

    def test_p1_crlf_vs_lf_sha256_and_bytes_resilience(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f_lf = Path(tmp) / "sample_lf.md"
            f_crlf = Path(tmp) / "sample_crlf.md"
            content_lf = b"---\nname: test\ndescription: hello\n---\n\nLine 1\nLine 2\n"
            content_crlf = content_lf.replace(b"\n", b"\r\n")
            f_lf.write_bytes(content_lf)
            f_crlf.write_bytes(content_crlf)

            self.assertEqual(catalog._sha256(f_lf), catalog._sha256(f_crlf))
            self.assertEqual(len(catalog._normalized_bytes(f_lf)), len(catalog._normalized_bytes(f_crlf)))

    def _start_server(self, handler_cls):
        import http.server
        import threading
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        return srv, f"http://127.0.0.1:{srv.server_address[1]}"

    def test_p2_pagination_truncation_reported_and_not_marked_complete(self) -> None:
        import http.server
        holder = {"base": ""}

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                body = {
                    "data": [{"id": "600111", "name": "Real estate", "type": "adinterest"}],
                    "paging": {"next": f"{holder['base']}/v26.0/search?type=adinterest&q=Real+estate&after=cursor_p2"},
                }
                raw = json.dumps(body).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv, base_url = self._start_server(Handler)
        holder["base"] = base_url
        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = base_url
            os.environ["META_ACCESS_TOKEN"] = "mock_tok_trunc"
            with tempfile.TemporaryDirectory() as tmp:
                cfile = Path(tmp) / "trunc_cache.json"
                rep = self.mte.search_and_validate_targeting(
                    queries=["Real estate"],
                    niche="real-estate",
                    max_pages_per_query=1,
                    cache_path=cfile,
                )
                lcs = rep["live_check_status"]
                self.assertTrue(lcs["is_truncated"])
                self.assertFalse(lcs["is_complete"])
                self.assertIn("TRUNCATED", lcs["status"])
                first_diag = rep["query_diagnostics"][0]
                self.assertEqual(first_diag["pages_fetched"], 1)
                self.assertTrue(first_diag["is_truncated"])
                self.assertEqual(first_diag["results_count"], 1)
                self.assertTrue(any("Pagination Truncated" in lim for lim in rep["limitations_and_disclosures"]))
                self.assertFalse(cfile.is_file())
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_p3_malformed_or_empty_shape_payload_never_classified_as_not_found(self) -> None:
        import http.server

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                raw = json.dumps({"data": [{"id": "", "name": ""}, {"foo": "bar"}]}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv, base_url = self._start_server(Handler)
        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = base_url
            os.environ["META_ACCESS_TOKEN"] = "mock_tok_malformed"
            rep = self.mte.search_and_validate_targeting(queries=["BrokenQuery"], niche="ecom")
            self.assertEqual(rep["live_check_status"]["status"], "API_UNAVAILABLE")
            self.assertEqual(rep["live_check_status"]["error_category"], "MALFORMED_ITEM_PAYLOAD")
            self.assertEqual(rep["not_found_queries"], [])
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_p4_cache_key_isolation_across_special_ad_category_country_objective_locale_and_corrupted_states(self) -> None:
        import http.server

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass
            def do_GET(self) -> None:
                raw = json.dumps({"data": [{"id": "600999", "name": "Mortgage loan", "type": "adinterest"}]}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv, base_url = self._start_server(Handler)
        old_base = os.environ.get("META_GRAPH_API_BASE_URL")
        old_tok = os.environ.get("META_ACCESS_TOKEN")
        try:
            os.environ["META_GRAPH_API_BASE_URL"] = base_url
            os.environ["META_ACCESS_TOKEN"] = "mock_tok_cache"
            with tempfile.TemporaryDirectory() as tmp:
                cfile = Path(tmp) / "isolated_cache.json"

                # 1. Cache miss on non-existent file
                r_none = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="NONE",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertFalse(r_none["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_none["live_check_status"]["cache_status"], "MISS_NO_FILE")

                # 2. Exact same context -> HIT_VALID
                r_hit = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="NONE",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertTrue(r_hit["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_hit["live_check_status"]["cache_status"], "HIT_VALID")

                # 3. Different special_ad_category (HOUSING) -> CONTEXT_MISMATCH, must NOT serve NONE cache and MUST include HOUSING warning
                r_housing = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="HOUSING",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertFalse(r_housing["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_housing["live_check_status"]["cache_status"], "CONTEXT_MISMATCH")
                self.assertNotEqual(r_none["query_context"]["cache_key"], r_housing["query_context"]["cache_key"])
                self.assertTrue(any("Special Ad Category = HOUSING" in lim for lim in r_housing["limitations_and_disclosures"]))

                # 4. Different country / objective / locale -> CONTEXT_MISMATCH
                r_kz = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="HOUSING",
                    country="KZ", objective="SALES", locale="ru_RU", cache_path=cfile,
                )
                self.assertFalse(r_kz["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_kz["live_check_status"]["cache_status"], "CONTEXT_MISMATCH")

                # 5. Corrupted cache file -> CORRUPTED
                cfile.write_text("{corrupted_json", encoding="utf-8")
                r_corrupt = self.mte.search_and_validate_targeting(
                    product="Ipoteka", niche="real-estate", special_ad_category="NONE",
                    country="UZ", objective="LEADS", locale="en_US", cache_path=cfile,
                )
                self.assertFalse(r_corrupt["live_check_status"]["served_from_valid_cache"])
                self.assertEqual(r_corrupt["live_check_status"]["cache_status"], "CORRUPTED")
        finally:
            srv.shutdown()
            srv.server_close()
            if old_base is None: os.environ.pop("META_GRAPH_API_BASE_URL", None)
            else: os.environ["META_GRAPH_API_BASE_URL"] = old_base
            if old_tok is None: os.environ.pop("META_ACCESS_TOKEN", None)
            else: os.environ["META_ACCESS_TOKEN"] = old_tok

    def test_p5_readme_and_docs_cli_examples_parse_and_smoke_test(self) -> None:
        old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
        try:
            # Verify README.md command: python3 tools/meta-targeting-engine.py search --niche real-estate --query "interyer" --query "новостройки" --account-id act_123456789
            proc1 = _run_tool_inproc(
                "meta-targeting-engine.py", "search",
                "--niche", "real-estate", "--query", "interyer", "--query", "новостройки",
                "--account-id", "act_123456789", "--json",
            )
            self.assertEqual(proc1.returncode, 0, proc1.stderr)
            data1 = json.loads(proc1.stdout)
            self.assertEqual(data1["query_context"]["ad_account_id"], "act_123456789")

            # Verify --ad-account-id alias and implicit search subcommand also work
            proc2 = _run_tool_inproc(
                "meta-targeting-engine.py",
                "--niche", "real-estate", "--query", "interyer", "--ad-account-id", "act_123456789", "--json",
            )
            self.assertEqual(proc2.returncode, 0, proc2.stderr)

            # Verify README.md universal router command: python3 tools/tyrion.py route "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top"
            proc3 = _run_tool_inproc(
                "skill-search.py", "route", "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top", "--json",
            )
            self.assertEqual(proc3.returncode, 0, proc3.stderr)
            route_data = json.loads(proc3.stdout)
            self.assertEqual(route_data["primary_agent"], "audit-meta")
        finally:
            if old_tok is not None:
                os.environ["META_ACCESS_TOKEN"] = old_tok


class UniversalAutoRouterTests(unittest.TestCase):
    """Part 2: 18 Mandatory Automated Tests for Universal Auto-Router & Autonomous Agent Orchestration."""

    def setUp(self) -> None:
        self.ss = importlib.import_module("skill-search")
        self.mcp = importlib.import_module("tyrion-mcp-server")
        self.ss.SESSION_CACHE.reset()

    def test_01_simple_task_selects_single_agent_and_skill_automatically(self) -> None:
        plan = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True)
        self.assertEqual(plan["primary_agent"], "tracking-specialist")
        self.assertEqual(plan["supporting_agents"], [])
        self.assertEqual(plan["required_skills"], ["ads-server-side-tracking"])
        self.assertEqual(plan["intent_analysis"]["complexity"], "single_step")

    def test_02_multistep_marketing_task_selects_complementary_skills_and_supporting_agents(self) -> None:
        plan = self.ss.route_task("Yangi mijoz uchun to'liq marketing strategiyasi tuz.", load=True)
        self.assertEqual(plan["primary_agent"], "launch-planner")
        self.assertEqual(plan["intent_analysis"]["complexity"], "multi_step")
        self.assertGreaterEqual(len(plan["required_skills"]), 2)
        self.assertIn("ads-plan", plan["required_skills"])
        self.assertGreaterEqual(len(plan["supporting_agents"]), 1)

    def test_03_global_registry_fallback_when_agent_hint_skills_insufficient(self) -> None:
        # Hinting `video-editor` for a CAPI server-side tracking query must automatically discover `ads-server-side-tracking` from the global registry
        plan = self.ss.route_task("Meta CAPI va event_id deduplikatsiya xatolarini tekshir", agent_hint="video-editor", load=True)
        self.assertTrue(plan["global_registry_fallback_used"])
        self.assertIn("ads-server-side-tracking", plan["required_skills"])
        self.assertEqual(plan["primary_agent"], "tracking-specialist")

    def test_04_multilingual_tasks_uz_latin_uz_cyrillic_ru_en_routed_accurately(self) -> None:
        cases = [
            ("Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top", "uz_latin", "audit-meta", "ads-meta"),
            ("Мета рекламада CAPI ишлашини текшир ва пиксель хатоларини топ", "uz_cyrillic", "tracking-specialist", "ads-server-side-tracking"),
            ("Подбери детальный таргетинг и интересы в Мета для недвижимости", "ru", "meta-audience-architect", "ads-meta-audience"),
            ("Audit my Google Ads Performance Max and search terms negative keywords", "en", "audit-google", "ads-google"),
        ]
        for query, exp_lang, exp_agent, exp_skill in cases:
            with self.subTest(lang=exp_lang):
                plan = self.ss.route_task(query, load=True)
                self.assertEqual(plan["intent_analysis"]["detected_language"], exp_lang)
                self.assertEqual(plan["primary_agent"], exp_agent)
                self.assertIn(exp_skill, plan["required_skills"])

    def test_05_generic_common_words_do_not_trigger_wrong_specialist_agent(self) -> None:
        plan = self.ss.route_task("iltimos menga hozir tez yordam qilib ber", load=True)
        self.assertEqual(plan["status"], "fallback_ready")
        self.assertTrue(plan["fallback_plan"]["triggered"])
        self.assertNotIn(plan["primary_agent"], ("audit-amazon", "audit-apple", "video-editor"))

    def test_06_universal_fallback_works_when_no_skill_matches(self) -> None:
        plan = self.ss.route_task("zzz qqq unknown holographic billboard telemetry xyz", load=True)
        self.assertEqual(plan["status"], "fallback_ready")
        self.assertTrue(plan["fallback_plan"]["triggered"])
        self.assertEqual(plan["fallback_plan"]["conductor"], "ads")
        self.assertIn("ads", plan["required_skills"])
        self.assertGreaterEqual(len(plan["fallback_plan"]["steps"]), 2)

    def test_07_only_dangerous_or_missing_critical_input_blocks_execution(self) -> None:
        safe_plan = self.ss.route_task("Instagram uchun bir oylik kontent reja tayyorla", load=True)
        self.assertEqual(safe_plan["status"], "ready")
        self.assertFalse(safe_plan["mutation_gate"]["blocked"])

        dangerous_plan = self.ss.route_task("Meta kampaniyamda byudjetni 300% oshir va reklamalarni hoziroq o'chir", load=True)
        self.assertEqual(dangerous_plan["status"], "blocked_mutation_approval")
        self.assertTrue(dangerous_plan["mutation_gate"]["blocked"])
        self.assertTrue(len(dangerous_plan["missing_inputs"]) > 0)

    def test_08_mid_task_dynamic_rerouting_adds_specialist_skill_and_agent(self) -> None:
        initial = self.ss.route_task("Instagram uchun bir oylik kontent reja tayyorla", load=True)
        self.assertEqual(initial["primary_agent"], "social-content-writer")
        self.assertNotIn("tracking-specialist", [initial["primary_agent"]] + initial["supporting_agents"])

        rerouted = self.ss.reroute_task(initial, "CAPI ishlashini tekshir va event_id deduplikatsiya xatolarini top", load=True)
        self.assertTrue(rerouted.get("rerouted"))
        self.assertIn("tracking-specialist", rerouted["supporting_agents"])
        self.assertIn("ads-server-side-tracking", rerouted["supporting_skills"] + rerouted["required_skills"])
        self.assertIn("ads-server-side-tracking", rerouted["loaded_context"]["loaded_skill_names"])

    def test_09_skill_references_loaded_selectively_only_when_needed(self) -> None:
        plan = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True)
        refs = plan["references_to_load"]
        self.assertIn("skills/ads/references/conversion-tracking.md", refs)
        self.assertLessEqual(len(refs), 4, "Should never dump all 39 references into context")
        for r in refs:
            self.assertTrue((VAULT / r).is_file(), f"Reference does not exist: {r}")

    def test_10_no_duplicate_or_redundant_agents_selected(self) -> None:
        for q in (
            "Yangi mijoz uchun to'liq marketing strategiyasi tuz",
            "Raqobatchilarimni o'rganib, menga reklama strategiyasi tuz",
            "Saytimni SEO va konversiya bo'yicha yaxshila",
        ):
            plan = self.ss.route_task(q, load=True)
            all_agents = [plan["primary_agent"]] + plan["supporting_agents"]
            self.assertEqual(len(all_agents), len(set(all_agents)), f"Duplicate agent in {all_agents}")
            all_skills = plan["required_skills"] + plan["supporting_skills"]
            self.assertEqual(len(all_skills), len(set(all_skills)), f"Duplicate skill in {all_skills}")

    def test_11_validator_detects_broken_reference_links_in_skill_metadata(self) -> None:
        skills = self.ss.load_skills()
        agents = self.ss.load_agents()
        tampered = [dict(s) for s in skills]
        tampered[0]["declared_references"] = ["skills/non_existent_broken_ref_xyz.md"]
        problems, _warnings = self.ss.validate_registry(tampered, agents)
        self.assertTrue(any("non_existent_broken_ref_xyz.md" in p for p in problems))

    def test_12_bidirectional_skill_agent_links_100pct_consistent(self) -> None:
        problems, _warnings = self.ss.validate_registry()
        self.assertEqual(problems, [], f"Registry validation problems found: {problems}")

    def test_13_conductor_and_worker_packets_comply_with_contract_schema(self) -> None:
        plan = self.ss.route_task("Raqobatchilarimni o'rganib, menga reklama strategiyasi tuz.", load=True)
        self.assertGreaterEqual(len(plan["worker_packets"]), 1)
        required_packet_keys = {
            "step", "role", "agent", "goal", "scope_boundary", "assigned_skills",
            "references_to_load", "input_data", "expected_output_format",
            "evidence_requirements", "safety_constraints", "verification_criteria",
        }
        for wp in plan["worker_packets"]:
            self.assertTrue(required_packet_keys.issubset(set(wp.keys())))

    def test_14_existing_slash_commands_audit_auditoriya_kreativ_budget_hisobot_intact(self) -> None:
        for cmd_name in ("audit", "auditoriya", "kreativ", "budget", "hisobot", "tracking", "voronka", "mijoz"):
            cmd_path = VAULT / "commands" / f"{cmd_name}.md"
            mirror_path = VAULT / ".claude" / "commands" / f"{cmd_name}.md"
            self.assertTrue(cmd_path.is_file(), f"Missing command: {cmd_path}")
            self.assertTrue(mirror_path.is_file(), f"Missing command mirror: {mirror_path}")
            self.assertEqual(
                cmd_path.read_bytes().replace(b"\r\n", b"\n"),
                mirror_path.read_bytes().replace(b"\r\n", b"\n"),
            )

    def test_15_router_never_asks_user_to_choose_skill_or_agent_name(self) -> None:
        for q in (
            "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top",
            "zzz qqq unknown holographic billboard telemetry xyz",
            "Meta kampaniyamda byudjetni 300% oshir",
        ):
            plan = self.ss.route_task(q, load=True)
            self.assertFalse(plan["asks_user_for_skill_or_agent"])
            for msg in plan["missing_inputs"]:
                self.assertNotIn("skill tanlang", msg.lower())
                self.assertNotIn("agent tanlang", msg.lower())

    def test_16_mcp_and_cli_router_share_identical_agent_and_skill_metadata(self) -> None:
        query = "Saytimni SEO va konversiya bo'yicha yaxshila."
        cli_plan = self.ss.route_task(query, load=True)
        mcp_resp = self.mcp.handle_request({
            "jsonrpc": "2.0",
            "id": 901,
            "method": "tools/call",
            "params": {"name": "tyrion_universal_router", "arguments": {"query": query, "load": True}},
        })
        mcp_plan = json.loads(mcp_resp["result"]["content"][0]["text"])
        self.assertEqual(cli_plan["primary_agent"], mcp_plan["primary_agent"])
        self.assertEqual(cli_plan["required_skills"], mcp_plan["required_skills"])
        self.assertEqual(cli_plan["supporting_skills"], mcp_plan["supporting_skills"])
        self.assertEqual(cli_plan["rules_to_load"], mcp_plan["rules_to_load"])

    def test_17_router_never_claims_unloaded_skill_was_loaded_or_applied(self) -> None:
        plan_no_load = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=False)
        self.assertFalse(plan_no_load["loaded_context"]["actually_loaded"])
        self.assertEqual(plan_no_load["loaded_context"]["loaded_skill_names"], [])
        self.assertEqual(plan_no_load["loaded_context"]["loaded_skills"], [])

        # When load=True, verify every claimed loaded skill was read from disk and session cache works on 2nd read
        cache = self.ss.SessionContextCache()
        plan_loaded_1 = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True, session_cache=cache)
        self.assertTrue(plan_loaded_1["loaded_context"]["actually_loaded"])
        self.assertIn("ads-server-side-tracking", plan_loaded_1["loaded_context"]["loaded_skill_names"])
        self.assertFalse(plan_loaded_1["loaded_context"]["loaded_skills"][0]["from_session_cache"])

        plan_loaded_2 = self.ss.route_task("CAPI ishlashini tekshir, xatolarni top.", load=True, session_cache=cache)
        self.assertTrue(plan_loaded_2["loaded_context"]["loaded_skills"][0]["from_session_cache"])
        self.assertGreater(cache.hits, 0)

    def test_18_mutation_gate_blocks_unapproved_account_changes_until_approved(self) -> None:
        q = "Meta kampaniyamda byudjetni 50% oshir va reklamalarni hoziroq o'chir"
        blocked = self.ss.route_task(q, mutation_approved=False, load=True)
        self.assertEqual(blocked["status"], "blocked_mutation_approval")
        self.assertTrue(blocked["mutation_gate"]["blocked"])
        self.assertIn("rules/40-xavfsizlik-va-hisob.md", blocked["rules_to_load"])

        approved = self.ss.route_task(q, mutation_approved=True, load=True)
        self.assertEqual(approved["status"], "ready")
        self.assertFalse(approved["mutation_gate"]["blocked"])
        self.assertTrue(approved["mutation_gate"]["approved"])

