"""Regression checks for development tooling, including host isolation/redaction."""

import contextlib
import copy
import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE = importlib.util.spec_from_file_location("detect_agent_check", ROOT / "scripts" / "check.py")
check = importlib.util.module_from_spec(MODULE)
MODULE.loader.exec_module(check)


class CheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.markdown = (ROOT / "detect-agent.md").read_text(encoding="utf-8")
        cls.spec = check.Specification(cls.markdown)
        cls.fixtures = json.loads((ROOT / "conformance" / "cases.json").read_text(encoding="utf-8"))
        cls.match_fixtures = json.loads(
            (ROOT / "conformance" / "matches.json").read_text(encoding="utf-8")
        )

    def test_all_fixtures_are_isolated_from_host(self):
        class NoHostEnvironment:
            def get(self, key):
                raise AssertionError("Conformance touched host environment")

        with (
            mock.patch.object(check.os, "environ", NoHostEnvironment()),
            mock.patch.object(check, "live_capabilities", side_effect=AssertionError("live probe")),
            mock.patch.object(check.os, "pathsep", ";"),
        ):
            output, code = check.conformance(self.spec)
        self.assertEqual(code, 0)
        self.assertEqual(output["status"], "passed")
        self.assertEqual(output["cases"], len(self.fixtures["cases"]))
        self.assertEqual(output["match_cases"], len(self.match_fixtures["cases"]))
        self.assertFalse(output["missing_match_coverage"])

    def test_missing_fixture_capabilities_stay_unavailable(self):
        cases = [
            ({}, None),
            ({"TERM_PROGRAM": "kiro"}, None),
            ({"TERM_PROGRAM": "kiro"}, False),
        ]
        self.assertEqual(check.run_case(self.spec, {"env": cases[0][0]})["evidence"], "none")
        self.assertEqual(check.run_case(self.spec, {"env": cases[1][0]})["evidence"], "none")
        self.assertEqual(
            check.run_case(self.spec, {"env": cases[2][0], "stdout_is_tty": False})["evidence"],
            "context-hint",
        )

    def test_unknown_grammar_and_table_loss_fail_closed(self):
        bad_documents = [
            self.markdown.replace("non-empty `CRUSH`", "prefix `CRUSH`", 1),
            self.markdown.replace(
                "non-empty `CRUSH`", "non-empty `CRUSH` XOR non-empty `OTHER`", 1
            ),
            self.markdown.replace("`CRUSH` | registry", "`CRUSH` OR | registry", 1),
            self.markdown.replace(
                "| Order | Canonical ID | Match condition and meaning |",
                "| Order | Product | Predicate |",
            ),
            self.markdown.replace(".pi/agents` does not match", ".pi/agents` also matches", 1),
            self.markdown.replace(
                "non-empty `GOOSE_PROVIDER`. This may be persistent provider configuration.",
                "non-empty `GOOSE_PROVIDER`. Require `GOOSE_ACTIVE` to equal `1` too.",
            ),
            self.markdown.replace(
                "This identifies a Replit workspace.",
                "This identifies a Replit workspace. Only match when `ACTIVE` is non-empty.",
            ),
        ]
        for document in bad_documents:
            with self.subTest(index=bad_documents.index(document)):
                with self.assertRaises(check.CheckError):
                    check.Specification(document)

    def test_rules_and_catalog_come_from_markdown(self):
        document = self.markdown.replace("`crush`", "`synthetic-agent`").replace(
            "non-empty `CRUSH`", "non-empty `SYNTHETIC_MARKER`"
        )
        spec = check.Specification(document)
        self.assertIn("synthetic-agent", spec.catalog)
        self.assertNotIn("crush", spec.catalog)
        self.assertEqual(
            spec.detect({"SYNTHETIC_MARKER": "synthetic"}.get),
            {"agent_id": "synthetic-agent", "evidence": "runtime-marker"},
        )

    def metadata_row(self, agent_id="codex"):
        header = (
            "| Canonical ID | Product | Description (en) | Description (zh-CN) | Official source |"
        )
        self.assertIn(header, self.markdown)
        body = self.markdown.split(header, 1)[1].split("\n\n", 1)[0]
        return next(line for line in body.splitlines() if line.startswith(f"| `{agent_id}` |"))

    def test_product_metadata_is_complete_and_read_from_the_specification(self):
        reviewed_at = self.spec.agent_metadata["codex"]["reviewed_at"]
        date_line = f"Product metadata reviewed: **{reviewed_at}**"
        synthetic_date = "2000-01-01" if reviewed_at != "2000-01-01" else "2000-01-02"
        self.assertIn(date_line, self.markdown)
        replacement = (
            "| `codex` | Synthetic Codex | Synthetic English description. | 合成中文描述。 | "
            "[Documentation](https://example.com/codex) |"
        )
        document = self.markdown.replace(self.metadata_row(), replacement, 1).replace(
            date_line, f"Product metadata reviewed: **{synthetic_date}**"
        )
        spec = check.Specification(document)
        self.assertEqual(set(spec.agent_metadata), spec.catalog)
        self.assertEqual(
            spec.agent_info("codex"),
            {
                "agent_id": "codex",
                "name": "Synthetic Codex",
                "descriptions": {"en": "Synthetic English description.", "zh-CN": "合成中文描述。"},
                "source": {"type": "documentation", "url": "https://example.com/codex"},
                "reviewed_at": synthetic_date,
            },
        )
        for label, source_type in (
            ("GitHub About", "github-about"),
            ("Website", "website"),
            ("Documentation", "documentation"),
            ("Company announcement", "company-announcement"),
            ("Official repository", "official-repository"),
        ):
            with self.subTest(source_type=source_type):
                source_document = document.replace(
                    "[Documentation](https://example.com/codex)",
                    f"[{label}](https://example.com/codex)",
                )
                source_spec = check.Specification(source_document)
                self.assertEqual(source_spec.agent_info("codex")["source"]["type"], source_type)

    def test_product_metadata_lookup_accepts_only_exact_canonical_ids(self):
        for agent_id in self.spec.catalog:
            with self.subTest(agent_id=agent_id):
                self.assertEqual(self.spec.agent_info(agent_id)["agent_id"], agent_id)
        unknown_ids = (
            None,
            "",
            "unknown-private-agent",
            "codex_cli",
            "CODEX",
            " codex ",
            "codex@1",
        )
        for agent_id in unknown_ids:
            with self.subTest(agent_id=agent_id):
                self.assertIsNone(self.spec.agent_info(agent_id))

    def test_malformed_product_metadata_fails_closed(self):
        row = self.metadata_row()
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        replacements = [
            "",
            row + "\n" + row,
            row + "\n" + row.replace("`codex`", "`extra-agent`", 1),
        ]
        for index in (1, 2, 3):
            empty = list(cells)
            empty[index] = " "
            replacements.append("| " + " | ".join(empty) + " |")
        for source in (
            "[Third-party](https://example.com/product)",
            "[Website](javascript:synthetic)",
            "https://example.com/product",
        ):
            changed = list(cells)
            changed[4] = source
            replacements.append("| " + " | ".join(changed) + " |")
        documents = [self.markdown.replace(row, replacement, 1) for replacement in replacements]
        reviewed_at = self.spec.agent_metadata["codex"]["reviewed_at"]
        date_line = f"Product metadata reviewed: **{reviewed_at}**"
        self.assertIn(date_line, self.markdown)
        for replacement in (
            "",
            "Product metadata reviewed: **2026-02-30**",
            "Product metadata reviewed: **20261103**",
            date_line + "\n" + date_line,
        ):
            documents.append(self.markdown.replace(date_line, replacement, 1))
        documents.append(
            self.markdown.replace(
                "| Description (en) | Description (zh-CN) |", "| English | Chinese |", 1
            )
        )
        for index, document in enumerate(documents):
            with self.subTest(index=index):
                self.assertNotEqual(document, self.markdown)
                with self.assertRaises(check.CheckError):
                    check.Specification(document)

    def test_product_metadata_records_are_independent_copies(self):
        original = copy.deepcopy(self.spec.agent_metadata["codex"])
        record = self.spec.agent_info("codex")
        record["agent_id"] = "changed"
        record["descriptions"]["en"] = "changed"
        record["descriptions"]["zh-CN"] = "已修改"
        record["source"]["url"] = "https://example.com/changed"
        self.assertEqual(self.spec.agent_info("codex"), original)
        self.assertEqual(self.spec.agent_metadata["codex"], original)

    def test_product_metadata_edits_do_not_change_detection(self):
        replacement = (
            "| `codex` | Synthetic Product | Synthetic English description. | 合成介绍。 | "
            "[Website](https://example.com/product) |"
        )
        spec = check.Specification(self.markdown.replace(self.metadata_row(), replacement, 1))
        self.assertEqual(spec.keys, self.spec.keys)
        for case in self.fixtures["cases"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(check.run_case(spec, case), case["expected"])
        for case in self.match_fixtures["cases"]:
            with self.subTest(match_case=case["name"]):
                self.assertEqual(check.run_match_case(spec, case), case["expected"])

    def test_product_metadata_cli_is_offline_and_exports_sorted_complete_records(self):
        class NoHostEnvironment:
            def get(self, key):
                raise AssertionError("Metadata command touched host environment")

            __getitem__ = get

            def __iter__(self):
                raise AssertionError("Metadata command enumerated host environment")

        commands = [
            (["agent-info", "--id", "codex"], self.spec.agent_info("codex")),
            (["agent-info", "--id", "private-unregistered"], None),
            (["agent-info", "--id", "codex_cli"], None),
            (
                ["export-metadata"],
                {
                    "spec_version": self.spec.version,
                    "agents": [
                        self.spec.agent_info(agent_id) for agent_id in sorted(self.spec.catalog)
                    ],
                },
            ),
        ]
        for argv, expected in commands:
            with (
                self.subTest(command=argv[0]),
                mock.patch.object(check.os, "environ", NoHostEnvironment()),
                mock.patch.object(
                    check, "live_capabilities", side_effect=AssertionError("live probe")
                ),
                mock.patch.object(
                    check.Specification, "detect", side_effect=AssertionError("detect")
                ),
                mock.patch.object(
                    check.Specification, "matches", side_effect=AssertionError("matches")
                ),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
            ):
                code = check.main(argv)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout.getvalue()), expected)
            self.assertNotIn("private-unregistered", stdout.getvalue())

    def test_product_metadata_cli_rejects_bad_arguments_and_redacts_load_errors(self):
        commands = [
            ["agent-info"],
            ["agent-info", "--id"],
            ["agent-info", "--unknown", "private-argument"],
            ["agent-info", "--id", "codex", "private-argument"],
            ["export-metadata", "private-argument"],
        ]
        for argv in commands:
            with self.subTest(argv=argv), contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(check.main(argv), 2)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "error")
            self.assertNotIn("private-argument", stdout.getvalue())
        for argv in (["agent-info", "--id", "codex"], ["export-metadata"]):
            with (
                mock.patch.object(check, "load_spec", side_effect=OSError("private-source-path")),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
            ):
                self.assertEqual(check.main(argv), 2)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "error")
            self.assertNotIn("private-source-path", stdout.getvalue())

    def test_indented_table_rows_do_not_silently_drop_rules(self):
        document = "\n".join(
            " " + line + " " if line.startswith("|") else line
            for line in self.markdown.splitlines()
        )
        spec = check.Specification(document)
        self.assertEqual(spec.runtime, self.spec.runtime)
        self.assertEqual(spec.contexts, self.spec.contexts)
        self.assertEqual(spec.catalog, self.spec.catalog)
        self.assertEqual(spec.aliases, self.spec.aliases)
        self.assertEqual(
            spec.detect({"AGENT": "grok"}.get), {"agent_id": "grok-build", "evidence": "declared"}
        )

    def test_optional_outer_table_pipes_do_not_silently_drop_rules(self):
        for leading, trailing in ((False, True), (True, False), (False, False)):
            with self.subTest(leading=leading, trailing=trailing):
                lines = []
                for line in self.markdown.splitlines():
                    # Change only body rows; the known headers remain intact.
                    if line.startswith("| ") and line.split("|")[1].strip()[:1] in "`0123456789":
                        if not leading:
                            line = line[1:]
                        if not trailing:
                            line = line[:-1]
                    lines.append(line)
                spec = check.Specification("\n".join(lines))
                self.assertEqual(spec.runtime, self.spec.runtime)
                self.assertEqual(spec.contexts, self.spec.contexts)
                self.assertEqual(spec.catalog, self.spec.catalog)
                self.assertEqual(spec.aliases, self.spec.aliases)
                self.assertEqual(
                    spec.detect({"AGENT": "grok"}.get),
                    {"agent_id": "grok-build", "evidence": "declared"},
                )

    def test_fixture_schema_rejects_collisions_unknown_fields_and_duplicates(self):
        mutations = []
        duplicate = copy.deepcopy(self.fixtures)
        duplicate["cases"].append(duplicate["cases"][0])
        mutations.append(duplicate)
        unknown = copy.deepcopy(self.fixtures)
        unknown["cases"][0]["locale"] = "tr"
        mutations.append(unknown)
        collision = copy.deepcopy(self.fixtures)
        collision["cases"][0].update(
            env={"CRUSH": "1", "crush": "2"}, env_name_case="ascii-insensitive"
        )
        mutations.append(collision)
        missing_version = copy.deepcopy(self.fixtures)
        missing_version["spec_version"] = "0.0.0"
        mutations.append(missing_version)
        wrong_tty = copy.deepcopy(self.fixtures)
        wrong_tty["cases"][0]["stdout_is_tty"] = 0
        mutations.append(wrong_tty)
        for document in mutations:
            with self.subTest(index=mutations.index(document)):
                with self.assertRaises(check.CheckError):
                    check.validate_fixtures(document, self.spec)

    def test_declarations_do_not_make_automatic_detection_pass(self):
        observations = [
            ({"CODEX_THREAD_ID": "secret-thread"}, "detected", 0),
            ({"AI_AGENT": "codex"}, "declared-only", 1),
            ({"AI_AGENT": "codex", "CODEX_THREAD_ID": "secret-thread"}, "declaration-masked", 1),
            (
                {"AI_AGENT": "unknown-secret", "CODEX_THREAD_ID": "secret-thread"},
                "declaration-masked",
                1,
            ),
            ({"AI_AGENT": "manus", "CODEX_THREAD_ID": "secret-thread"}, "declaration-masked", 1),
            ({"ZED_TERM": "secret-editor"}, "mismatch", 1),
            ({}, "unrecognized", 1),
        ]
        for env, status, expected_code in observations:
            with self.subTest(status=status, declared=bool(env.get("AI_AGENT"))):
                original = dict(env)
                output, code = check.self_check(self.spec, "codex", environment=env)
                self.assertEqual((output["status"], code), (status, expected_code))
                self.assertEqual(env, original)
                self.assertNotIn("secret", json.dumps(output))
        output, code = check.self_check(self.spec, "zed", environment={"ZED_TERM": "secret"})
        self.assertEqual((output["status"], code), ("context-only", 1))

    def test_versioned_declarations_share_literal_normalization_and_precedence(self):
        examples = [
            (" codex@V1.2+BUILD-3 ", "codex"),
            ("GEMINI_CLI@preview-1", "gemini-cli"),
            ("claude_code", "claude-code"),
            ("CLAUDE-CODE_2-1-205_AGENT", "claude-code"),
            ("claude-code_00-01-002_harness", "claude-code"),
            ("unknown-test-agent@1.0", None),
            ("codex@", None),
            ("codex@.1", None),
            ("codex@-1", None),
            ("codex@+1", None),
            ("codex@1_2", None),
            ("codex@1/2", None),
            ("codex@1@2", None),
            ("codex@1\nextra", None),
            ("codex@\u0661", None),
            ("\u00a0codex@1\u00a0", None),
            ("claude_code_2-1-205_agent", None),
            ("claude-code_2-1_agent", None),
            ("claude-code_2-1-205_unknown", None),
            ("claude-code_2-1-205_agent_extra", None),
            ("claude-code_2-1-205_agent@1", None),
        ]
        for key in ("AI_AGENT", "AGENT"):
            for value, agent_id in examples:
                with self.subTest(key=key, value=value):
                    env = {key: value, "CRUSH": "synthetic-runtime"}
                    if key == "AI_AGENT":
                        env["AGENT"] = "manus"
                    self.assertEqual(
                        self.spec.detect(env.get),
                        {"agent_id": agent_id, "evidence": "declared"},
                    )

    def test_declaration_patterns_and_capture_are_read_from_the_specification(self):
        original = "| name-at-version | `([a-z][a-z0-9_-]*)@([a-z0-9][a-z0-9.+-]*)` | 1 |"
        changed = self.markdown.replace(original, "| name-at-version | `(codex):[0-9]+` | 1 |")
        self.assertNotEqual(changed, self.markdown)
        spec = check.Specification(changed)
        self.assertEqual(
            spec.detect({"AI_AGENT": "codex:7"}.get),
            {"agent_id": "codex", "evidence": "declared"},
        )
        self.assertEqual(
            spec.detect({"AI_AGENT": "codex@7"}.get),
            {"agent_id": None, "evidence": "declared"},
        )
        changed_capture = self.markdown.replace(original, original.replace(" | 1 |", " | 2 |"))
        spec = check.Specification(changed_capture)
        self.assertEqual(
            spec.detect({"AI_AGENT": "codex@hi"}.get),
            {"agent_id": "hi", "evidence": "declared"},
        )

    def test_literal_alias_wins_before_declaration_format_parsing(self):
        document = self.markdown.replace(
            "| `grok` | `grok-build` |",
            "| `grok` | `grok-build` |\n| `claude-code_2-1-205_agent` | `hi` |",
        )
        spec = check.Specification(document)
        self.assertEqual(
            spec.detect({"AI_AGENT": "claude-code_2-1-205_agent"}.get),
            {"agent_id": "hi", "evidence": "declared"},
        )

    def test_malformed_declaration_format_tables_fail_closed(self):
        original = "| name-at-version | `([a-z][a-z0-9_-]*)@([a-z0-9][a-z0-9.+-]*)` | 1 |"
        replacements = [
            "| name-at-version | `(` | 1 |",
            "| name-at-version | `(codex)` | 0 |",
            "| name-at-version | `(codex)` | 2 |",
            "| name-at-version | `(codex)` | 1.0 |",
            "| name-at-version | (codex) | 1 |",
            original + "\n" + original,
        ]
        for replacement in replacements:
            with self.subTest(replacement=replacement):
                with self.assertRaises(check.CheckError):
                    check.Specification(self.markdown.replace(original, replacement))
        with self.assertRaises(check.CheckError):
            check.Specification(
                self.markdown.replace(
                    "| Declaration format | Full-string pattern | Name capture |",
                    "| Unsupported declaration table | Pattern | Capture |",
                )
            )

    def test_all_match_diagnostics_preserve_order_stages_and_redaction(self):
        env = {
            "AI_AGENT": "unknown-secret@1.0",
            "AGENT": "manus",
            "CLAUDE_CODE_IS_COWORK": "secret-cowork",
            "CLAUDECODE": "secret-claude",
            "CODEX_THREAD_ID": "secret-thread",
            "COPILOT_CLI": "secret-cli",
            "COPILOT_AGENT_SESSION_ID": "secret-session",
            "COPILOT_MODEL": "secret-model",
            "ZED_TERM": "secret-editor",
        }
        expected = [
            {"agent_id": "codex", "evidence": "runtime-marker"},
            {"agent_id": "cowork", "evidence": "runtime-marker"},
            {"agent_id": "claude-code", "evidence": "runtime-marker"},
            {"agent_id": "github-copilot", "evidence": "runtime-marker"},
            {"agent_id": "github-copilot", "evidence": "context-hint"},
            {"agent_id": "zed", "evidence": "context-hint"},
        ]
        original = dict(env)
        output, code = check.self_check(self.spec, environment=env)
        self.assertEqual(code, 0)
        self.assertEqual(output["result"], {"agent_id": None, "evidence": "declared"})
        self.assertEqual(output["matches"], expected)
        self.assertEqual(output["automatic_result"], expected[0])
        self.assertEqual(env, original)
        self.assertNotIn("secret", json.dumps(output))
        self.assertEqual(self.spec.matches({}.get), [])

    def test_all_match_capabilities_stay_explicit_and_synthetic(self):
        env = {"TERM_PROGRAM": "kiro", "PATH": "C:\\synthetic\\.pi\\agent\\bin;C:\\other"}
        case = {"env": env, "path_separator": ";"}
        self.assertEqual(
            check.run_match_case(self.spec, case),
            [{"agent_id": "pi", "evidence": "context-hint"}],
        )
        case.update(stdout_is_tty=False, files=["/opt/.devin"])
        self.assertEqual(
            check.run_match_case(self.spec, case),
            [
                {"agent_id": "pi", "evidence": "context-hint"},
                {"agent_id": "kiro", "evidence": "context-hint"},
                {"agent_id": "devin", "evidence": "context-hint"},
            ],
        )
        self.assertEqual(
            check.run_match_case(
                self.spec,
                {"env": {"codex_thread_id": "synthetic"}, "env_name_case": "ascii-insensitive"},
            ),
            [{"agent_id": "codex", "evidence": "runtime-marker"}],
        )

    def test_core_detection_stops_before_unneeded_lookups_and_file_probes(self):
        def named_lookup(key):
            if key not in ("AI_AGENT", "AGENT", "CRUSH"):
                raise AssertionError("First-match detection evaluated a later rule")
            return "synthetic" if key == "CRUSH" else None

        class UnavailableFiles:
            def __contains__(self, path):
                raise AssertionError("First-match detection probed optional files")

        self.assertEqual(
            self.spec.detect(named_lookup, files=UnavailableFiles()),
            {"agent_id": "crush", "evidence": "runtime-marker"},
        )

    def test_detection_and_matches_are_reevaluated_on_each_call(self):
        env = {"CRUSH": "synthetic"}
        self.assertEqual(self.spec.detect(env.get)["agent_id"], "crush")
        self.assertEqual(
            self.spec.matches(env.get), [{"agent_id": "crush", "evidence": "runtime-marker"}]
        )
        env.clear()
        env["CLINE_WRAPPER_PATH"] = "synthetic"
        self.assertEqual(self.spec.detect(env.get)["agent_id"], "cline")
        self.assertEqual(
            self.spec.matches(env.get), [{"agent_id": "cline", "evidence": "runtime-marker"}]
        )
        env.clear()
        self.assertEqual(self.spec.detect(env.get), {"agent_id": None, "evidence": "none"})
        self.assertEqual(self.spec.matches(env.get), [])

    def test_match_fixture_schema_rejects_invalid_results_and_inputs(self):
        valid = {
            "spec_version": self.spec.version,
            "cases": [{"name": "synthetic empty", "env": {}, "expected": []}],
        }
        check.validate_match_fixtures(valid, self.spec)
        invalid_expected = [
            {"agent_id": None, "evidence": "none"},
            [{"agent_id": None, "evidence": "none"}],
            [{"agent_id": "codex", "evidence": "declared"}],
            [{"agent_id": "hi", "evidence": "runtime-marker"}],
            [{"agent_id": "unknown-test-agent", "evidence": "runtime-marker"}],
            [{"agent_id": "codex", "evidence": "runtime-marker", "value": "secret"}],
            [
                {"agent_id": "codex", "evidence": "runtime-marker"},
                {"agent_id": "codex", "evidence": "runtime-marker"},
            ],
        ]
        for expected in invalid_expected:
            document = copy.deepcopy(valid)
            document["cases"][0]["expected"] = expected
            with self.subTest(expected=expected):
                with self.assertRaises(check.CheckError):
                    check.validate_match_fixtures(document, self.spec)
        for field, value in (("unknown", True), ("stdout_is_tty", 0), ("files", "secret-path")):
            document = copy.deepcopy(valid)
            document["cases"][0][field] = value
            with self.subTest(field=field):
                with self.assertRaises(check.CheckError):
                    check.validate_match_fixtures(document, self.spec)

    def test_match_matrix_catches_foreign_rules_hidden_by_the_winner(self):
        spec = check.Specification(self.markdown)
        cline_index = next(i for i, row in enumerate(spec.runtime) if row[0] == "cline")
        # A broad Cline predicate would be hidden by a correct Qwen winner in
        # core fixtures. The complete expected match array must still reject it.
        spec.runtime[cline_index] = (
            "cline",
            ("or", spec.runtime[cline_index][1], ("non-empty", "QWEN_CODE")),
        )
        output, code = check.conformance(spec)
        self.assertEqual(code, 1)
        self.assertFalse(output["failures"])
        self.assertTrue(output["match_failures"])
        self.assertNotIn("env", json.dumps(output))

    def test_missing_match_coverage_is_conformance_failure(self):
        incomplete = copy.deepcopy(self.match_fixtures)
        incomplete["cases"] = [
            case
            for case in incomplete["cases"]
            if not any(result["agent_id"] == "crush" for result in case["expected"])
        ]
        with mock.patch.object(check.json, "loads", side_effect=[self.fixtures, incomplete]):
            output, code = check.conformance(self.spec)
        self.assertEqual(code, 1)
        self.assertFalse(output["match_failures"])
        self.assertIn(
            {"agent_id": "crush", "evidence": "runtime-marker"},
            output["missing_match_coverage"],
        )

    def test_no_expectation_reports_observation_only(self):
        output, code = check.self_check(self.spec, environment={"CODEX_THREAD_ID": "secret-thread"})
        self.assertEqual(
            (output["status"], code, output["expected_agent_id"]), ("observed", 0, None)
        )

    def test_conformance_failures_return_comparison_without_fixture_values(self):
        with mock.patch.object(
            self.spec, "detect", return_value={"agent_id": None, "evidence": "none"}
        ):
            output, code = check.conformance(self.spec)
        self.assertEqual(code, 1)
        self.assertEqual(output["status"], "failed")
        self.assertTrue(output["failures"])
        self.assertTrue(output["missing_coverage"])
        self.assertEqual(set(output["failures"][0]), {"case_number", "expected", "actual"})
        self.assertNotIn("env", json.dumps(output))

    def test_missing_catalog_coverage_is_conformance_failure(self):
        incomplete = copy.deepcopy(self.fixtures)
        incomplete["cases"] = [
            case for case in incomplete["cases"] if case["expected"]["agent_id"] != "hi"
        ]
        with mock.patch.object(check.json, "loads", side_effect=[incomplete, self.match_fixtures]):
            output, code = check.conformance(self.spec)
        self.assertEqual(code, 1)
        self.assertFalse(output["failures"])
        self.assertIn({"agent_id": "hi", "evidence": "declared"}, output["missing_coverage"])

    def test_only_allowlisted_keys_are_looked_up_without_enumeration(self):
        spec = self.spec
        lookups = []

        class NamedLookupOnly:
            def get(self, key):
                if key not in spec.keys:
                    raise AssertionError("Non-allowlisted key")
                lookups.append(key)
                return "secret-token" if key == "COPILOT_GITHUB_TOKEN" else None

            def __iter__(self):
                raise AssertionError("Environment enumeration")

        output, code = check.self_check(spec, "github-copilot", environment=NamedLookupOnly())
        self.assertEqual((output["status"], code), ("context-only", 1))
        self.assertNotIn("secret-token", json.dumps(output))
        self.assertEqual(sorted(lookups), sorted(spec.keys))
        self.assertEqual(
            output["matches"], [{"agent_id": "github-copilot", "evidence": "context-hint"}]
        )

    def test_cli_exit_status_and_error_redaction(self):
        commands = [
            (
                ["self-check", "--expect", "codex"],
                {"CODEX_THREAD_ID": "secret-thread"},
                0,
                "detected",
            ),
            (["self-check", "--expect", "codex"], {"AI_AGENT": "codex"}, 1, "declared-only"),
            (["self-check", "--expect", "secret-unregistered"], {}, 2, "error"),
            (["self-check"], {"AGENT": "secret-unregistered"}, 0, "observed"),
            (["self-check", "--unknown", "secret-argument"], {}, 2, "error"),
        ]
        for argv, env, expected_code, status in commands:
            with (
                mock.patch.object(check.os, "environ", env),
                mock.patch.object(check, "live_capabilities", return_value=(None, None)),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
            ):
                code = check.main(argv)
            self.assertEqual(code, expected_code)
            self.assertEqual(json.loads(stdout.getvalue())["status"], status)
            self.assertNotIn("secret", stdout.getvalue())

        class FailingProvider:
            def get(self, key):
                raise RuntimeError("secret-value-in-error")

        with (
            mock.patch.object(check.os, "environ", FailingProvider()),
            mock.patch.object(check, "live_capabilities", return_value=(None, None)),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            self.assertEqual(check.main(["self-check"]), 2)
        self.assertNotIn("secret-value", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
