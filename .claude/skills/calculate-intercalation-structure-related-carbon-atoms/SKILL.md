---
name: calculate-intercalation-structure-related-carbon-atoms
description: Build and validate ordered, repeating layers of intercalated atoms inside a carbon honeycomb channel, producing one_ch-{type}-v{i}-Claude.csv files.
---

# Calculate intercalated atom positions

Build the coordinates of intercalated atoms inside one carbon honeycomb channel, validate them
numerically and write them as `one_ch-{type}-v{i}-Claude.csv`.

All geometry, measurement and file access goes through the `carbon-honeycomb-manager` MCP server
(see `docs/mcp_description.md`). The server measures and edits but never judges: **the rules below
live in this skill**, and every target is passed to `validate_structure` as an argument. A different
skill with different rules reuses the same server.

## Input

The user names an element and a carbon structure, e.g. `Ar A1-7_h3` or `Xe C0-7_h3`.

- `element` is the lowercase symbol used as the data subdirectory: `ar`, `xe`, `kr`, `al`. Confirm it
  against `list_elements`.
- `structure` is the init-data directory name. Confirm it against `list_structures`.
- Never hardcode numbers for a particular element. Every constant comes from
  `get_intercalation_constants(element, structure)` for that exact element + structure pair.
  `Average {element}-C distance` depends on the structure too, so re-read it per structure.

If either is missing or does not match, ask before doing anything else.

## The rules a structure has to follow

Let `TARGET_C` = `Average {element}-C distance (Å)`, `TARGET_INTER` = `Distance between atoms (Å)`
and `HARD_MIN` = `Distance to remove too close atoms (Å)`, all from
`get_intercalation_constants`.

1. **Distances to carbon - for the atoms near the walls only.** The distance from a **near-wall**
   intercalated atom to its nearest carbon atom should be as close as possible to `TARGET_C`.

   **This rule does not apply to the central atoms** - the ones filling the middle of a wide channel,
   away from the walls. They are legitimately much further from carbon than the equilibrium distance,
   and that is correct, not a defect. In `ar/C2-7_h3/final_one_ch-v1-ABAB.xlsx` the 18 near-wall
   atoms sit at 2.60-2.64 Å from carbon (0 to +2% off target) while the 9 central atoms sit at
   4.00-6.84 Å (+54% to +163%) - and that file is a good structure. Same shape in
   `ar/A3-7_h3/final_one_ch-v1-ABAB.xlsx` and `ar/B4-7_h7/final_one_ch-v1-ABAB-Volod.xlsx`.

   `validate_structure` implements this split: an atom counts as near-wall when its distance to the
   nearest wall plane is at most `near_wall_max_dist_to_plane` (default: the upper edge of the carbon
   corridor). Central atoms appear in `dist_to_carbon_corridor_check.atom_indexes_exempt` and never
   count as violations. Read `summary.min_dist_to_carbon_near_wall` for rule 1 - **not**
   `summary.min_dist_to_carbon`, which mixes both populations and looks alarming for no reason.

   The central atoms are governed by rule 2 instead.

2. **Distances between intercalated atoms.** The distance from each intercalated atom to its nearest
   intercalated neighbour should be as close as possible to `TARGET_INTER`. This applies to **all**
   atoms, near-wall and central alike, and it is the only distance criterion for the central ones.
3. **Placement opposite wall features.** Intercalated atoms - the ones near the walls in particular -
   normally sit on the normal to a wall, opposite a polygon center or an edge hole. The structure
   should be roughly symmetric.
4. **Ordered, repeating layers along z.** A layer is the unordered set of atoms with the same z
   coordinate. The sequence of layer `(x, y)` sets must repeat and contain at most four unique
   layers. Use the explicit type names `AA`, `ABAB`, `ABCABC`, or `ABCDABCD`; the letters describe
   equal `(x, y)` sets, not merely uniform z spacing. Every occurrence of the same letter must have
   the same unordered `(x, y)` coordinates within coordinate precision. The combined carbon and
   intercalated elementary cell must self-repeat along Oz and may span several carbon periods.
5. **Maximum filling.** Prefer structures that fill the channel as densely as possible - but keep
   **every** reasonable filling variant as its own version, not only the densest one.

### Priority between the rules

Satisfying all five at once is usually impossible. At least one of rules 1 and 2 must hold well:

- **few atoms (narrow channel)** - rule 1 wins (distances to the nearest carbon). In a narrow channel
  every atom is a near-wall atom, so rule 1 covers the whole structure;
- **many atoms (wide channel)** - rule 2 wins (distances between intercalated atoms). Here the
  structure splits: the near-wall shell is still held to rule 1, and rule 2 carries the interior;
- otherwise, aim for most atoms being close to both targets.

### Allowed deviations

Compression up to 8% and expansion up to 10% from the equilibrium distances, i.e. the corridor
`[TARGET × 0.92, TARGET × 1.10]`. `HARD_MIN` (= `TARGET_INTER × 0.7`) is a physical floor: **never
write a structure that puts two intercalated atoms closer than that.**

The corridor around `TARGET_C` applies to the near-wall atoms only (see rule 1). The corridor around
`TARGET_INTER` applies to every atom.

Large uniform stretching is unlikely physically, so distances close to `TARGET_C` are preferable to
distances that merely stay inside the corridor.

**When rule 4 conflicts with the corridor** (typical for narrow channels like `A1-7_h3` or
`C0-7_h3`), rule 4 wins - but then build **two versions**: one where rule 4 holds even though the
corridor is left, and one where the corridor holds even though the repeat is worse. Keep both, and
state in the report which trade-off each version makes.

### Existing reference files are context, not a target

Legacy `final_one_ch-*.xlsx` and generated `one_ch-*.csv` files under the structure's result directory
show what an acceptable structure looks
like. Your structures are **not required to match them** - a different, or even better, structure is a
normal and expected outcome. Judge your result **only by the rules above**. Show the numbers so the
user can compare for themselves.

## Procedure

### Search loop and stopping policy

- Explore at most **5 structurally distinct candidate branches**. A branch is one starting packing
  pattern plus its iterative corrections; do not count ordinary corrections as new candidates.
- There is no fixed maximum number of correction iterations and no required number of accepted
  variants. Continue improving a candidate while the deterministic validation metrics improve.
- Track `iterations_without_improvement`. Reset it to 0 after a meaningful improvement; abandon the
  current candidate after **4 consecutive** validation rounds without improvement, then try the next
  distinct branch if fewer than 5 have been attempted.
- An iteration improves when it fixes a higher-priority failed check, reduces its violations or
  deviation without materially worsening a higher-priority rule, improves seam repeatability, or
  increases filling without breaking an already satisfied hard constraint. Record the compared
  metrics in the checkpoint; do not claim improvement from visual intuition alone.
- Before accepting a variant, compare it with every accepted variant using `compare_structures`,
  passing `carbon_z_period` and `distinct_rmsd_threshold=0.4`. A different atom count is distinct;
  otherwise the permutation- and z-period-aware RMSD must exceed the threshold.
- Create a `run_id` and call `save_run_checkpoint` after the baseline and every meaningful
  generate/edit/validate round. Store the current `atoms` and `atom_ids`, attempted and accepted
  candidates, latest metrics, `iterations_without_improvement`, last change, next hypothesis and
  status. On a resumed task, use `list_run_checkpoints` / `load_run_checkpoint` instead of rebuilding
  state from chat context.

1. **Scope the channel.** `get_channel_params(element, structure)` and
   `get_intercalation_constants(element, structure)`. Note `num_of_planes`, `carbon_z_period`, the z
   limits, the channel radius implied by `coordinate_limits`, and `hexagons_per_plane` /
   `edge_holes_per_plane`.
2. **Generate candidate positions near the walls.** `generate_atoms_near_planes(element, structure)`
   - the equivalent of the GUI `Generate near planes`. This pure tool writes no intermediate file;
   its returned coordinates are the starting point, not the answer.
3. **Measure what you got.** `validate_structure(element, structure, atoms=<candidates>)`. Read the
   per-atom rows: which atoms are near their targets, which are too close to each other, which sit
   opposite a wall feature.
4. **Thin out and adjust.** Prefer stable `selected_atom_ids` over indexes. Use `delete_atoms` to drop
   the atoms that crowd their neighbours, and
   `move_atoms_along_plane_normal` / `move_atoms_to_channel_center` / `move_atoms_on_vector` to pull
   distances towards the targets. Re-run `validate_structure` after each round.
5. **Fill the channel interior** for wide channels: `add_atoms` with explicit coordinates, spaced by
   `TARGET_INTER`, kept symmetric around the channel axis (rule 3, rule 5). Space these atoms by
   `TARGET_INTER` from each other and from the near-wall shell - do **not** try to bring them closer
   to carbon. Their distance to the walls follows from the packing and will be far above `TARGET_C`;
   in the references it reaches +160%. Judge them by rule 2 only.
6. **Make ordered layers repeat along z.** Build a 1-4-layer template, then
   `translate_atoms_along_z` to fill the channel height. Confirm with the `z_periodicity_check`
   section of the report: `min_period_multiplier` must not be null, and
   `seam.min_dist_across_seam` must be close to `seam.min_dist_inside_cell` - a much smaller value
   means the tiling clashes, a much larger one means it leaves a gap.
7. **Build every reasonable variant** (rule 5), plus the two trade-off versions whenever rule 4 and
   the corridor conflict.
8. **Validate before writing.** Run `validate_structure` on the final coordinates of each variant.
   `write_final_structure` recomputes validation and defaults to requiring `hard_floor_check`; still
   inspect the report first and fix or drop a variant that fails it.
9. **Write.** Before writing, group atoms by z and explicitly audit that their unordered `(x, y)`
   sets follow the declared type. Then call
   `write_final_structure(element, structure, atoms, stacking=..., author="Claude")`. `stacking` is
   required and is one of `AA`, `ABAB`, `ABCABC`, `ABCDABCD`; a one-layer narrow structure is `AA`.
   The output is `one_ch-{type}-v{i}-Claude.csv`. Versioning is independent per type and starts at 1.
10. **Report to the user in chat**, one block per version (see below). Do not write a separate report
    file unless the user asks.

Work iteratively with the returned `atoms`, `coordinates` and `atom_ids`. Pass `atoms=` together with
the aligned `atom_ids=` on the next call and select atoms by ID. Indexes remain a legacy fallback.
The explicit checkpoint, not chat context alone, is the source of truth for resumable work.

## Report format

Per written version:

```
### one_ch-{type}-v{i}-Claude.csv  ({N} atoms)

Targets (element {E}, structure {S}):
  Average {E}-C distance      {TARGET_C} Å
  Distance between atoms      {TARGET_INTER} Å   corridor [{lo}, {hi}]
  Hard minimum                {HARD_MIN} Å

Atoms: {n} near the walls / {n} central

Rule 1  dist to C (near-wall only)  min {..} / mean {..} / max {..}   deviation {..}% .. {..}%
        central atoms (exempt)      min {..} / mean {..} / max {..}
Rule 2  dist to inter (all atoms)   min {..} / mean {..} / max {..}   deviation {..}% .. {..}%
Rule 3  opposite       {n} hexagon / {n} pentagon / {n} edge hole / {n} none
        nearest-carbon spread  mean {..} Å
Rule 4  repeats after {k} carbon z periods ({length} Å); seam {..} Å vs interior {..} Å
Rule 5  filling: {short description of this variant vs the others}

Hard floor: PASSED / VIOLATED
Trade-off:  {both | rule 4 over corridor | corridor over rule 4 | neither}
Violations: {list or none}
```

Then a short paragraph: which rules this variant favours, why, and how it differs from the other
versions. If a reference file exists, you may add its numbers side by side - as information, not as a
pass/fail criterion.

## Notes and gotchas

- **`hexagons_per_plane` can be all zeros.** The armchair-oriented C-family walls (e.g. `C0-7_h3`)
  have every hexagon straddling a channel edge, so no polygon lies entirely inside a single plane.
  There, rule 3 is measured through `edge_holes` and through the per-atom `nearest_carbon_distances`
  / `nearest_carbon_spread`: an atom opposite a ring center is roughly equidistant from 6 carbons, so
  a small spread means good placement even when `opposite_feature` is null.
- **`verified_by_overlap: false`** in `z_periodicity_check` means the structure is exactly one
  elementary cell tall, so nothing overlaps it to compare against. That is normal for a correctly
  built elementary cell - lean on the `seam` numbers in that case.
- **Do not generate `all_ch-*` files.** The user generates those from your `one_ch-*`
  after checking them.
- **Do not use `generate_atoms_opposite_centers` / `generate_atoms_opposite_faces`** for this skill.
  They rely on the `place_opposite_centers` / `place_opposite_faces` constants, which belong to a
  separate approach (and are still placeholders for most elements). Rule 1 here refers only to
  `Average {element}-C distance`.
- Prefer `atoms=` inline over writing intermediate files. Write only the final versions.
