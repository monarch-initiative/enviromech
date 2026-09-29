# EnviroMech task runner. Scripts run under the sibling dismech checkout's
# environment, the same placeholder arrangement the schema uses for its
# linkml-aop import; set DISMECH_ROOT to point elsewhere.

set positional-arguments

dismech := env_var_or_default("DISMECH_ROOT", justfile_directory() / ".." / "dismech")

# List recipes
default:
    @just --list

# Emit a SourceNode block for one or more dismech node references (quote each one)
resolve-source-node +refs:
    uv run --project "{{dismech}}" python scripts/resolve_source_node.py --dismech "{{dismech}}" "$@"

# Check every source_nodes[] entry of one or more KeyEventAggregation files against dismech
check-source-nodes +files:
    #!/usr/bin/env bash
    set -euo pipefail
    args=(); for f in "$@"; do args+=(--check "$f"); done
    uv run --project "{{dismech}}" python scripts/resolve_source_node.py --dismech "{{dismech}}" "${args[@]}"

# Validate the example records against the schema
validate-examples:
    uv run --project "{{dismech}}" linkml-validate -s src/enviromech/schema/enviromech.yaml -C KeyEventAggregation src/data/examples/*.yaml
