#!/usr/bin/env python3
"""Development checks for the Markdown specification; not a production SDK.

Runtime predicates have this grammar (AND binds more tightly than OR):
  expression := conjunction (" OR " conjunction)*
  conjunction := atom (" AND " atom)*
  atom := "non-empty `NAME`" | "`NAME` equals `CONSTANT`" | "(" expression ")"
Context tables additionally support the documented PATH, TTY and file predicates.
Unknown table syntax is an error, never an ignored or guessed detection rule.
"""

import json
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
ASCII_SPACE = "\t\n\v\f\r "
ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
ID = re.compile(r"`([a-z][a-z0-9-]*)`\Z")
TOKEN = re.compile(r"non-empty `[A-Z][A-Z0-9_]*`|`[A-Z][A-Z0-9_]*` equals `[^`\n]+`|AND|OR|[()]")
PATH_CONDITION = (
    "A PATH entry contains consecutive path components `.pi` and `agent`. "
    "Normalize backslashes to forward slashes and compare components case-sensitively; "
    "`.pi/agents` does not match. Split PATH using the target platform's path-list separator. "
    "This describes an installation/search path."
)
TTY_CONDITION = (
    "`TERM_PROGRAM` contains the case-sensitive substring `kiro` AND the caller explicitly "
    "supplies `stdout_is_tty = false`. Missing TTY information does not satisfy this condition."
)
FILE_CONDITION = (
    "The caller-provided filesystem probe reports that `/opt/.devin` exists. "
    "Skip this hint if no probe is supplied or if access is unavailable. "
    "Do not run a subprocess to check it."
)
CONTEXT_EXPLANATIONS = {
    "This may be persistent provider configuration.",
    "Model, permission and credential configuration alone does not establish an active agent.",
    "This identifies a Replit workspace.",
    "This can be inherited from an editor terminal.",
    "This can identify a human-operated editor terminal.",
}


class CheckError(Exception):
    """Messages are fixed diagnostics; never include environment/fixture values."""


def require(condition, message):
    if not condition:
        raise CheckError(message)


def ascii_lower(value):
    return value.translate(ASCII_LOWER)


def parse_expression(source):
    tokens = []
    position = 0
    while position < len(source):
        match = TOKEN.match(source, position)
        require(match is not None, "Unsupported runtime predicate syntax.")
        tokens.append(match.group())
        position = match.end()
        if position < len(source) and source[position] == " ":
            position += 1
    index = 0

    def atom():
        nonlocal index
        require(index < len(tokens), "Incomplete runtime predicate.")
        token = tokens[index]
        index += 1
        if token == "(":
            result = expression()
            require(index < len(tokens) and tokens[index] == ")", "Unbalanced runtime predicate.")
            index += 1
            return result
        if token.startswith("non-empty "):
            return ("non-empty", token.split("`")[1])
        if " equals " in token:
            pieces = token.split("`")
            return ("equals", pieces[1], pieces[3])
        raise CheckError("Unsupported runtime predicate atom.")

    def conjunction():
        nonlocal index
        result = atom()
        while index < len(tokens) and tokens[index] == "AND":
            index += 1
            result = ("and", result, atom())
        return result

    def expression():
        nonlocal index
        result = conjunction()
        while index < len(tokens) and tokens[index] == "OR":
            index += 1
            result = ("or", result, conjunction())
        return result

    result = expression()
    require(index == len(tokens), "Unexpected runtime predicate suffix.")
    return result


def table(markdown, header):
    lines = markdown.splitlines()
    locations = [i for i, line in enumerate(lines) if line.strip() == header]
    require(len(locations) == 1, "Missing or duplicate specification table.")
    start = locations[0] + 1
    count = len(header.strip("|").split("|"))
    require(start < len(lines), "Missing table separator.")
    separator = [cell.strip() for cell in lines[start].strip().strip("|").split("|")]
    require(len(separator) == count and all(re.fullmatch(r":?-{3,}:?", c) for c in separator),
            "Unsupported table separator.")
    rows = []
    for line in lines[start + 1:]:
        line = line.strip()
        if not line.startswith("|"):
            break
        require(line.endswith("|"), "Malformed table row.")
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        require(len(cells) == count, "Malformed table columns.")
        rows.append(cells)
    require(rows, "Empty specification table.")
    return rows


def canonical(cell):
    match = ID.fullmatch(cell)
    require(match is not None, "Invalid canonical ID syntax.")
    return match.group(1)


def predicate_keys(node):
    if node[0] in ("non-empty", "equals"):
        return {node[1]}
    if node[0] in ("and", "or"):
        return predicate_keys(node[1]) | predicate_keys(node[2])
    return {"PATH"} if node[0] == "path" else {"TERM_PROGRAM"} if node[0] == "tty" else set()


class Specification:
    def __init__(self, markdown):
        versions = re.findall(r"^Version: \*\*([0-9]+\.[0-9]+\.[0-9]+)\*\*", markdown, re.M)
        require(len(versions) == 1, "Missing or duplicate specification version.")
        self.version = versions[0]
        runtime = table(markdown, "| Priority | Canonical ID | Product | Match condition | Marker evidence |")
        self.runtime = []
        for index, row in enumerate(runtime, 1):
            require(row[0] == str(index), "Runtime priorities must be consecutive and ordered.")
            self.runtime.append((canonical(row[1]), parse_expression(row[3])))
        contexts = table(markdown, "| Order | Canonical ID | Match condition and meaning |")
        self.contexts = []
        for index, row in enumerate(contexts, 1):
            require(row[0] == str(index), "Context order must be consecutive.")
            condition = row[2]
            if condition == PATH_CONDITION:
                node = ("path",)
            elif condition == TTY_CONDITION:
                node = ("tty",)
            elif condition == FILE_CONDITION:
                node = ("file",)
            else:
                predicate, separator, explanation = condition.partition(". ")
                # Accept only the reviewed explanatory suffixes. An unfamiliar
                # second sentence could add a condition; never silently drop it.
                require(not separator or explanation in CONTEXT_EXPLANATIONS,
                        "Unsupported context predicate explanation or restriction.")
                node = parse_expression(predicate)
            self.contexts.append((canonical(row[1]), node))
        declarations = table(markdown, "| Canonical ID | Product | Reference |")
        self.declaration_only = [canonical(row[0]) for row in declarations]
        for rows in (self.runtime, self.contexts):
            require(len({row[0] for row in rows}) == len(rows), "Duplicate canonical ID within a rule table.")
        automatic_ids = {row[0] for row in self.runtime + self.contexts}
        require(len(set(self.declaration_only)) == len(self.declaration_only), "Duplicate declaration-only ID.")
        require(not automatic_ids.intersection(self.declaration_only), "Declaration-only ID has an automatic rule.")
        self.catalog = automatic_ids | set(self.declaration_only)
        self.aliases = {}
        for row in table(markdown, "| Alias | Canonical ID |"):
            match = re.fullmatch(r"`([a-z][a-z0-9_-]*)`", row[0])
            require(match is not None, "Invalid declaration alias.")
            alias, target = match.group(1), canonical(row[1])
            require(alias not in self.aliases and alias not in self.catalog and target in self.catalog,
                    "Duplicate alias or unknown alias target.")
            self.aliases[alias] = target
        self.keys = {"AI_AGENT", "AGENT"}
        for _, node in self.runtime + self.contexts:
            self.keys.update(predicate_keys(node))

    def detect(self, lookup, files=None, stdout_is_tty=None, path_separator=":", automatic=False):
        if not automatic:
            for key in ("AI_AGENT", "AGENT"):
                value = lookup(key)
                if value is not None and value.strip(ASCII_SPACE):
                    declared = ascii_lower(value.strip(ASCII_SPACE))
                    declared = self.aliases.get(declared, declared)
                    return {"agent_id": declared if declared in self.catalog else None, "evidence": "declared"}

        def matches(node):
            kind = node[0]
            if kind == "non-empty":
                return bool(lookup(node[1]))
            if kind == "equals":
                return lookup(node[1]) == node[2]
            if kind == "and":
                return matches(node[1]) and matches(node[2])
            if kind == "or":
                return matches(node[1]) or matches(node[2])
            if kind == "path":
                for entry in (lookup("PATH") or "").split(path_separator):
                    parts = entry.replace("\\", "/").split("/")
                    if any(parts[i:i + 2] == [".pi", "agent"] for i in range(len(parts) - 1)):
                        return True
                return False
            if kind == "tty":
                return stdout_is_tty is False and "kiro" in (lookup("TERM_PROGRAM") or "")
            if kind == "file":
                return files is not None and "/opt/.devin" in files
            raise CheckError("Unsupported parsed predicate.")

        for rows, evidence in ((self.runtime, "runtime-marker"), (self.contexts, "context-hint")):
            for agent_id, node in rows:
                if matches(node):
                    return {"agent_id": agent_id, "evidence": evidence}
        return {"agent_id": None, "evidence": "none"}


def load_spec(root=ROOT):
    return Specification((root / "detect-agent.md").read_text(encoding="utf-8"))


def validate_fixtures(data, spec):
    require(type(data) is dict and set(data) == {"spec_version", "cases"}, "Invalid conformance document fields.")
    require(data["spec_version"] == spec.version, "Conformance version differs from specification.")
    require(type(data["cases"]) is list and data["cases"], "Conformance cases must be a non-empty list.")
    names = set()
    allowed = {"name", "env", "expected", "env_name_case", "files", "stdout_is_tty", "path_separator"}
    for case in data["cases"]:
        require(type(case) is dict and {"name", "env", "expected"} <= set(case) <= allowed,
                "Invalid conformance case fields.")
        name = case["name"]
        require(type(name) is str and bool(name.strip()) and name not in names, "Empty or duplicate case name.")
        names.add(name)
        env = case["env"]
        require(type(env) is dict and all(type(k) is str and type(v) is str for k, v in env.items()),
                "Synthetic environment must contain string keys and values.")
        mode = case.get("env_name_case", "sensitive")
        require(mode in ("sensitive", "ascii-insensitive"), "Invalid synthetic name lookup mode.")
        if mode == "ascii-insensitive":
            require(len({ascii_lower(k) for k in env}) == len(env), "Colliding synthetic environment names.")
        if "files" in case:
            require(type(case["files"]) is list and all(type(p) is str for p in case["files"]),
                    "Synthetic files must be a list of strings.")
        if "stdout_is_tty" in case:
            require(type(case["stdout_is_tty"]) is bool, "Synthetic TTY state must be boolean.")
        if "path_separator" in case:
            require(case["path_separator"] in (":", ";"), "Invalid synthetic PATH separator.")
        expected = case["expected"]
        require(type(expected) is dict and set(expected) == {"agent_id", "evidence"}, "Invalid expected result fields.")
        agent_id, evidence = expected["agent_id"], expected["evidence"]
        require(agent_id is None or type(agent_id) is str and agent_id in spec.catalog,
                "Unknown expected canonical ID.")
        require(evidence in ("none", "declared", "runtime-marker", "context-hint"), "Invalid expected evidence.")
        require((evidence != "none" or agent_id is None) and
                (evidence not in ("runtime-marker", "context-hint") or agent_id is not None),
                "Inconsistent expected result.")


def run_case(spec, case):
    env = case["env"]
    if case.get("env_name_case") == "ascii-insensitive":
        env = {ascii_lower(k): v for k, v in env.items()}
        lookup = lambda key: env.get(ascii_lower(key))
    else:
        lookup = env.get
    return spec.detect(lookup, files=case.get("files"), stdout_is_tty=case.get("stdout_is_tty"),
                       path_separator=case.get("path_separator", ":"))


def conformance(spec, root=ROOT):
    data = json.loads((root / "conformance" / "cases.json").read_text(encoding="utf-8"))
    validate_fixtures(data, spec)
    failures = []
    coverage = set()
    for index, case in enumerate(data["cases"], 1):
        actual = run_case(spec, case)
        if actual != case["expected"]:
            failures.append({"case_number": index, "expected": case["expected"], "actual": actual})
        else:
            coverage.add((actual["agent_id"], actual["evidence"]))
    required = {(row[0], "runtime-marker") for row in spec.runtime}
    required.update((row[0], "context-hint") for row in spec.contexts)
    required.update((agent_id, "declared") for agent_id in spec.declaration_only)
    missing = [{"agent_id": agent_id, "evidence": evidence}
               for agent_id, evidence in sorted(required - coverage)]
    failed = bool(failures or missing)
    return {"spec_version": spec.version, "status": "failed" if failed else "passed",
            "cases": len(data["cases"]), "canonical_ids": len(spec.catalog),
            "failures": failures, "missing_coverage": missing}, int(failed)


def self_check(spec, expected=None, environment=None, files=None, stdout_is_tty=None, path_separator=None):
    require(expected is None or expected in spec.catalog, "--expect must be a canonical product ID.")
    provider = os.environ if environment is None else environment
    # Query named keys only. Preserve the native provider's lookup semantics;
    # do not enumerate/copy os.environ or print its values.
    snapshot = {key: provider.get(key) for key in sorted(spec.keys)}
    result = spec.detect(snapshot.get, files=files, stdout_is_tty=stdout_is_tty,
                         path_separator=os.pathsep if path_separator is None else path_separator)
    automatic = spec.detect(snapshot.get, files=files, stdout_is_tty=stdout_is_tty,
                            path_separator=os.pathsep if path_separator is None else path_separator, automatic=True)
    status = "observed"
    if expected is not None:
        target = {"agent_id": expected, "evidence": "runtime-marker"}
        if result == automatic == target:
            status = "detected"
        elif result["evidence"] == "declared" and automatic == target:
            status = "declaration-masked"
        elif result == {"agent_id": expected, "evidence": "declared"}:
            status = "declared-only"
        elif automatic == {"agent_id": expected, "evidence": "context-hint"}:
            status = "context-only"
        elif automatic["agent_id"] is None:
            status = "unrecognized"
        else:
            status = "mismatch"
    return {"spec_version": spec.version, "result": result, "automatic_result": automatic,
            "expected_agent_id": expected, "status": status}, int(expected is not None and status != "detected")


def live_capabilities():
    try:
        files = ["/opt/.devin"] if Path("/opt/.devin").exists() else []
    except OSError:
        files = None
    try:
        tty = sys.stdout.isatty()
    except (AttributeError, OSError):
        tty = None
    return files, tty


def main(argv=None):
    try:
        arguments = list(sys.argv[1:] if argv is None else argv)
        # Keep parsing independent of locale/environment lookups and never echo
        # rejected arguments, which may accidentally contain private values.
        if arguments in (["--help"], ["-h"], ["conformance", "--help"], ["self-check", "--help"]):
            print("Usage: python3 scripts/check.py conformance\n"
                  "       python3 scripts/check.py self-check [--expect CANONICAL_ID]\n"
                  "Development checks only; detection does not authenticate the immediate caller.")
            return 0
        require(bool(arguments), "Choose conformance or self-check; see --help.")
        command, expected = arguments[0], None
        if command == "conformance":
            require(len(arguments) == 1, "conformance accepts no arguments; see --help.")
        elif command == "self-check":
            if len(arguments) == 3 and arguments[1] == "--expect":
                expected = arguments[2]
            else:
                require(len(arguments) == 1, "self-check accepts only --expect CANONICAL_ID; see --help.")
        else:
            raise CheckError("Choose conformance or self-check; see --help.")
        spec = load_spec()
        if command == "conformance":
            output, code = conformance(spec)
        else:
            files, tty = live_capabilities()
            output, code = self_check(spec, expected, files=files, stdout_is_tty=tty)
    except CheckError as error:
        output, code = {"status": "error", "error": str(error)}, 2
    except Exception:
        # Environment providers and I/O errors can include values/paths in exception
        # messages. Keep CLI errors fixed and omit tracebacks, even for unknown errors.
        output, code = {"status": "error", "error": "Check failed; verify specification syntax, fixture schema and command arguments."}, 2
    print(json.dumps(output, ensure_ascii=True, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
