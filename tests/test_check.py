"""Regression checks for development tooling, including host isolation/redaction."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
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

    def test_all_fixtures_are_isolated_from_host(self):
        class NoHostEnvironment:
            def get(self, key):
                raise AssertionError("Conformance touched host environment")

        with mock.patch.object(check.os, "environ", NoHostEnvironment()), \
                mock.patch.object(check, "live_capabilities", side_effect=AssertionError("live probe")), \
                mock.patch.object(check.os, "pathsep", ";"):
            output, code = check.conformance(self.spec)
        self.assertEqual(code, 0)
        self.assertEqual(output["status"], "passed")
        self.assertEqual(output["cases"], len(self.fixtures["cases"]))

    def test_missing_fixture_capabilities_stay_unavailable(self):
        cases = [
            ({}, None),
            ({"TERM_PROGRAM": "kiro"}, None),
            ({"TERM_PROGRAM": "kiro"}, False),
        ]
        self.assertEqual(check.run_case(self.spec, {"env": cases[0][0]})["evidence"], "none")
        self.assertEqual(check.run_case(self.spec, {"env": cases[1][0]})["evidence"], "none")
        self.assertEqual(check.run_case(self.spec, {"env": cases[2][0], "stdout_is_tty": False})["evidence"], "context-hint")

    def test_unknown_grammar_and_table_loss_fail_closed(self):
        bad_documents = [
            self.markdown.replace("non-empty `CRUSH`", "prefix `CRUSH`", 1),
            self.markdown.replace("non-empty `CRUSH`", "non-empty `CRUSH` XOR non-empty `OTHER`", 1),
            self.markdown.replace("`CRUSH` | registry", "`CRUSH` OR | registry", 1),
            self.markdown.replace("| Order | Canonical ID | Match condition and meaning |", "| Order | Product | Predicate |"),
            self.markdown.replace(".pi/agents` does not match", ".pi/agents` also matches", 1),
            self.markdown.replace("non-empty `GOOSE_PROVIDER`. This may be persistent provider configuration.",
                                  "non-empty `GOOSE_PROVIDER`. Require `GOOSE_ACTIVE` to equal `1` too."),
            self.markdown.replace("This identifies a Replit workspace.",
                                  "This identifies a Replit workspace. Only match when `ACTIVE` is non-empty."),
        ]
        for document in bad_documents:
            with self.subTest(index=bad_documents.index(document)):
                with self.assertRaises(check.CheckError):
                    check.Specification(document)

    def test_rules_and_catalog_come_from_markdown(self):
        document = self.markdown.replace("`crush`", "`synthetic-agent`").replace("non-empty `CRUSH`", "non-empty `SYNTHETIC_MARKER`")
        spec = check.Specification(document)
        self.assertIn("synthetic-agent", spec.catalog)
        self.assertNotIn("crush", spec.catalog)
        self.assertEqual(spec.detect({"SYNTHETIC_MARKER": "synthetic"}.get),
                         {"agent_id": "synthetic-agent", "evidence": "runtime-marker"})

    def test_indented_table_rows_do_not_silently_drop_rules(self):
        document = "\n".join(" " + line + " " if line.startswith("|") else line
                             for line in self.markdown.splitlines())
        spec = check.Specification(document)
        self.assertEqual(spec.runtime, self.spec.runtime)
        self.assertEqual(spec.contexts, self.spec.contexts)
        self.assertEqual(spec.catalog, self.spec.catalog)
        self.assertEqual(spec.aliases, self.spec.aliases)
        self.assertEqual(spec.detect({"AGENT": "grok"}.get),
                         {"agent_id": "grok-build", "evidence": "declared"})

    def test_fixture_schema_rejects_collisions_unknown_fields_and_duplicates(self):
        mutations = []
        duplicate = copy.deepcopy(self.fixtures)
        duplicate["cases"].append(duplicate["cases"][0])
        mutations.append(duplicate)
        unknown = copy.deepcopy(self.fixtures)
        unknown["cases"][0]["locale"] = "tr"
        mutations.append(unknown)
        collision = copy.deepcopy(self.fixtures)
        collision["cases"][0].update(env={"CRUSH": "1", "crush": "2"}, env_name_case="ascii-insensitive")
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
            ({"AI_AGENT": "unknown-secret", "CODEX_THREAD_ID": "secret-thread"}, "declaration-masked", 1),
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

    def test_no_expectation_reports_observation_only(self):
        output, code = check.self_check(self.spec, environment={"CODEX_THREAD_ID": "secret-thread"})
        self.assertEqual((output["status"], code, output["expected_agent_id"]), ("observed", 0, None))

    def test_conformance_failures_return_comparison_without_fixture_values(self):
        with mock.patch.object(self.spec, "detect", return_value={"agent_id": None, "evidence": "none"}):
            output, code = check.conformance(self.spec)
        self.assertEqual(code, 1)
        self.assertEqual(output["status"], "failed")
        self.assertTrue(output["failures"])
        self.assertTrue(output["missing_coverage"])
        self.assertEqual(set(output["failures"][0]), {"case_number", "expected", "actual"})
        self.assertNotIn("env", json.dumps(output))

    def test_missing_catalog_coverage_is_conformance_failure(self):
        incomplete = copy.deepcopy(self.fixtures)
        incomplete["cases"] = [case for case in incomplete["cases"]
                               if case["expected"]["agent_id"] != "hi"]
        with mock.patch.object(check.json, "loads", return_value=incomplete):
            output, code = check.conformance(self.spec)
        self.assertEqual(code, 1)
        self.assertFalse(output["failures"])
        self.assertIn({"agent_id": "hi", "evidence": "declared"}, output["missing_coverage"])

    def test_only_allowlisted_keys_are_looked_up_without_enumeration(self):
        spec = self.spec

        class NamedLookupOnly:
            def get(self, key):
                if key not in spec.keys:
                    raise AssertionError("Non-allowlisted key")
                return "secret-token" if key == "COPILOT_GITHUB_TOKEN" else None

            def __iter__(self):
                raise AssertionError("Environment enumeration")

        output, code = check.self_check(spec, "github-copilot", environment=NamedLookupOnly())
        self.assertEqual((output["status"], code), ("context-only", 1))
        self.assertNotIn("secret-token", json.dumps(output))

    def test_cli_exit_status_and_error_redaction(self):
        commands = [
            (["self-check", "--expect", "codex"], {"CODEX_THREAD_ID": "secret-thread"}, 0, "detected"),
            (["self-check", "--expect", "codex"], {"AI_AGENT": "codex"}, 1, "declared-only"),
            (["self-check", "--expect", "secret-unregistered"], {}, 2, "error"),
            (["self-check"], {"AGENT": "secret-unregistered"}, 0, "observed"),
            (["self-check", "--unknown", "secret-argument"], {}, 2, "error"),
        ]
        for argv, env, expected_code, status in commands:
            with mock.patch.object(check.os, "environ", env), \
                    mock.patch.object(check, "live_capabilities", return_value=(None, None)), \
                    contextlib.redirect_stdout(io.StringIO()) as stdout:
                code = check.main(argv)
            self.assertEqual(code, expected_code)
            self.assertEqual(json.loads(stdout.getvalue())["status"], status)
            self.assertNotIn("secret", stdout.getvalue())

        class FailingProvider:
            def get(self, key):
                raise RuntimeError("secret-value-in-error")

        with mock.patch.object(check.os, "environ", FailingProvider()), \
                mock.patch.object(check, "live_capabilities", return_value=(None, None)), \
                contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(check.main(["self-check"]), 2)
        self.assertNotIn("secret-value", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
