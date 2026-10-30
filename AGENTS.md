# Instructions for agents

This repository is a language-independent detection specification, with local
development tools. `detect-agent.md` is the only normative source of rules;
the Python checker is a development aid, not a production SDK.

## Check whether you are recognized

1. Read [the self-check guide](docs/agent-self-check.md) and the
   [result contract](detect-agent.md#1-result-contract).
2. Choose your expected canonical product ID from the specification based on
   the product/launcher you are using, not your model name or the detector output.
3. Run `python3 scripts/check.py conformance` to verify the repository's rules
   and synthetic fixtures.
4. Run `python3 scripts/check.py self-check --expect <canonical-id>` through your
   actual command tool. Do not set marker variables or declarations to pass it.
5. Report the expected ID, standard result, automatic result, status, specification
   version, and execution scope. A declaration, context hint, or passing synthetic
   test alone does not prove automatic recognition in your live environment.

If Python 3.9+ is unavailable, follow the manual procedure in the guide. Do not
install a runtime just to inspect this repository unless the task calls for it.

## Update a detection method

- Follow the guide's decision path: distinguish an outdated consuming
  implementation, declaration masking, inherited markers, and missing rule coverage.
- Follow [CONTRIBUTING.md](CONTRIBUTING.md). Change the specification first,
  then synthetic cases; update the specification version and changelog for a
  detection-contract change. Do not add a second rule catalog.
- Read only documented variables or specific evidence-backed candidate names.
  Never dump the environment, scan variable prefixes, or publish marker values,
  tokens, session IDs, internal endpoints, user paths, or proprietary source.
- Verify with `python3 scripts/check.py conformance` and
  `python3 -m unittest discover -s tests -v`.
- Use a feature branch and a pull request. Never merge code into `main`.
