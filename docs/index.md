# EnviroHealthMech

EnviroHealthMech is an environmental health mechanisms repository built from AI-curated
literature sources. It records how exposures to chemicals and other hazards external to
the body relate to adverse effects, represented as phenotypes and diseases.

## What it holds

EnviroHealthMech holds exposure-outcome knowledge whatever the strength of the evidence behind
it:

- associations between an exposure and an adverse effect, with no known mechanism;
- hypothesized mechanisms proposed to explain such associations;
- mature Adverse Outcome Pathways (AOPs), used in chemical safety risk assessment
  decisions.

How well supported a record is can be read from its evidence, confidence, and provenance,
which are recorded separately. See
[decision 1](explanation/design-decisions.md#1-what-envirohealthmech-is).

## How it relates to dismech

EnviroHealthMech follows the approach of the
[Disorder Mechanisms Knowledge Base (dismech)](https://github.com/monarch-initiative/dismech)
and inherits some of its design principles for how content is curated and validated. The difference is what each is organized around. dismech is organized around
disease entries; in EnviroHealthMech the exposure-outcome association is itself the thing
recorded, so it can exist before any curated disease entry or known mechanism, and
mechanisms attach to it. See
[decision 2](explanation/design-decisions.md#2-relationship-to-dismech).

## Schema

EnviroHealthMech does not yet have a schema of its own. Its base schema is the AOP-Wiki EMOD
schema from [EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop):
[`src/linkml_aop/schema/aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml).
See [decision 3](explanation/design-decisions.md#3-base-schema).
