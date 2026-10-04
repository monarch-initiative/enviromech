# EnviroMech commands. `just` lists them.

schema := "src/enviromech/schema/enviromech.yaml"
emod := "src/enviromech/schema/aop_emod_linkml.yaml"
ref_config := ".linkml-reference-validator.yaml"

_default:
    @just --list

# Install the tools and the pinned linkml-aop, and put its EMOD schema where
# enviromech.yaml imports it from.
install: _sync emod-schema

_sync:
    uv sync

# Copy the EMOD schema out of the installed linkml_aop package. LinkML resolves
# an import next to the importing file, not inside an installed package, so the
# copy is what the import finds. It is not tracked; pyproject.toml pins its source.
emod-schema:
    uv run python -c "from importlib.resources import files; import shutil; shutil.copyfile(files('linkml_aop') / 'schema' / 'aop_emod_linkml.yaml', '{{emod}}')"

# Validate every record against the schema.
validate:
    uv run linkml-validate -s {{schema}} -C KeyEventRecord data/key_events/*.yaml
    uv run linkml-validate -s {{schema}} -C ObservationRecord data/observations/*.yaml

# Check every evidence snippet word for word against its cached source.
validate-references:
    uv run linkml-reference-validator validate data data/observations/*.yaml -s {{schema}} -t ObservationRecord --config {{ref_config}}

# Check the ids EnviroMech assigns: each Observation's matches its record id,
# and each Assay id names one Assay.
check-ids:
    uv run python scripts/check_ids.py

# Everything a change must pass.
qc: validate check-ids validate-references
