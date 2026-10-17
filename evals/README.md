# Migration behavior evidence

Contract 3 exercises three boundaries with the current Skill: an actual native migration preserving owned checks and unknown content, a dirty target, and a noncanonical source. Fixtures and hidden expected ownership decisions are separate. The model receives only the Skill, task, source and isolated target; it does not see expected results. A parent independently reruns migration-structure verification, `make verify` and `make accept`, or checks protected owner changes / a rejected source target remain unchanged. These bounded fixture results establish migration behavior, not real-product acceptance.

`results.json` records observed ownership decisions and refers to parent evidence under `evidence/`. The validator binds evidence bytes and Skill digest; it does not rerun a model or certify the model's self-report. Tests use explicitly synthetic data to exercise the validator only. Source and target revisions, commands, outputs and the actual model response are retained in the execution evidence. There is no runtime dependency on these files.

The previous seven routing simulations, their input fixtures, package entrypoint and run metadata remain byte-for-byte under `history/v4-workbench/`; earlier failed rubric evidence remains under `history/v4-rubric1/`. Neither is promoted to an executed result.
