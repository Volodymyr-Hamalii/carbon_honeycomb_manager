---
name: calculate-intercalation-structure-related-carbon-polygon-points
description: Build, rebuild, and validate intercalated structures using carbon polygon centers, vertices, and edge midpoints, producing final_one_ch-v{i}[-{stacking}]-Codex.csv files.
---

# Calculate intercalation from carbon polygon points

Build or rebuild one-channel intercalated structures by preferring exact alignment with polygon
reference sites and using interpolated normal distances only when packing constraints require it.
This workflow deliberately does not center a narrow-channel model: it assigns atoms to concrete
wall sites even when the resulting coordinates form a compact cluster near the channel axis.
All geometry and edits go through the `carbon-honeycomb-manager` MCP server. The server measures;
this skill owns the priorities and acceptance decisions.

## Input and constants

Require `element` and `structure`; verify them with `list_elements` and `list_structures`. An optional
existing `file_name` means rebuild that model without overwriting it. Read
`get_intercalation_constants(element, structure)` for every run. Never embed element-specific
numbers in this skill. The current acceptance smoke target is Ar, but the procedure is
element-agnostic and becomes usable for other elements when their constants are populated.

Let:

- `CENTER_TARGET` = `Place opposite centers distance (Å)`;
- `FACE_TARGET` = `Place opposite faces distance (Å)`;
- `TARGET_INTER` = `Distance between atoms (Å)`;
- `INTER_LOWER` = `TARGET_INTER × 0.92`;
- `HARD_MIN` = `Distance to remove too close atoms (Å)`.
- `POLYGON_NEAR_WALL_LIMIT` = `max(CENTER_TARGET, FACE_TARGET) × 1.10`.

Pass `POLYGON_NEAR_WALL_LIMIT` as `near_wall_max_dist_to_plane` to both
`measure_polygon_site_distances` and `validate_structure`. This keeps both reports on the same
near-wall/central definition and avoids accidentally exempting exact polygon candidates when the
ordinary carbon-corridor default is smaller than the polygon normal targets.

## Rules and priorities

1. A near-wall atom should preferably project exactly onto a polygon center, any carbon vertex, or
   the midpoint of any unique C-C pair whose strict 3D distance is below 1.65 Å. Centers use
   `CENTER_TARGET`; vertices and edge midpoints use `FACE_TARGET` along the inward normal.
2. All intercalated-neighbour distances should be as close as possible to `TARGET_INTER`. No
   nearest-neighbour distance may be below `INTER_LOWER`; this is an acceptance gate, not a soft
   packing preference.
3. If exact alignment conflicts with packing, the hard floor, z-periodicity, or symmetry, use the
   target returned by `measure_polygon_site_distances`: it interpolates between center and face
   targets from the in-plane distances. Exact alignment remains preferable.
4. The model must self-repeat along Oz. A valid elementary cell may span multiple carbon periods.
5. Maximize filling while retaining meaningfully different trade-off models.

An interior atom in an ordinary or wide channel may be exempt from polygon-site targets and be
governed by intercalated-neighbour spacing. A narrow-channel atom is **not** exempt merely because
it lies close to the channel center. Source-wall provenance may guide generation and one edit, but
the atom's current nearest wall governs every acceptance decision. After any movement, re-detect
that wall and apply the center/vertex/edge target and the -8%/+10% normal corridor relative to it.
Every non-exempt near-wall atom must pass this polygon-normal corridor; it is a hard acceptance
gate, not a soft preference. The model must also pass the global nearest-carbon corridor reported
by `validate_structure`. No atom pair may ever violate `HARD_MIN`, and no nearest intercalated pair
may fall below `INTER_LOWER`. These constraints outrank filling, symmetry, visual quality, and
every soft objective.

Never write a final CSV when any critical gate fails: polygon-normal corridor, global
nearest-carbon corridor, `INTER_LOWER` for finite pairs or the periodic seam, hard floor, or
z-periodicity. Keep a promising but invalid geometry only in a run checkpoint. If the user
explicitly asks to preserve an invalid illustrative structure, its filename and report must say
`INVALID` and name the failed gate; never present it as an accepted `final_one_ch-*` model.

## Narrow-channel wall-first mode

Use this mode when the available cross-section forces all plausible intercalated positions into a
central axial cluster, as in A1.5. Do not use `move_atoms_to_channel_center`, a channel-center target,
or radial symmetrization as an objective in this mode.

1. Choose one deterministic primary wall whose plane contains or is parallel to Ox. Inspect all
   walls with `get_plane_geometry`, minimize the absolute x component of the normalized plane
   normal, and break an equivalent opposite-wall tie by the lowest `wall_index`.
2. Explore three distinct primary-wall branches: only polygon centers (type #1), only carbon
   vertices (type #2), and only eligible edge midpoints (type #3). Generate and correct each atom
   along that wall's inward normal while preserving the selected site's in-plane projection. A
   wall filter can also return cross-wall rings associated with that wall: retain only candidates
   whose source point lies in the selected plane and whose normalized `inward_normal` is parallel
   and codirectional with the selected wall's inward normal.
3. Explore a combined branch that assigns atoms to different walls and mixes site types #1/#2/#3
   to maximize packing. A fifth branch may test a meaningfully different mixed-wall stacking or
   periodic compromise.
4. `reference_wall_index` / `reference_wall_indexes` may be used immediately after generation or
   during one wall-relative edit to preserve source provenance. Re-run
   `measure_polygon_site_distances` without either argument after the edit. If another wall is now
   nearer, reassign the atom to that wall and re-evaluate its nearest site, target normal distance,
   and corridor status before continuing.
5. The actual nearest wall is always the acceptance reference frame, including in narrow-channel
   mode. Do not accept a source-wall measurement after an atom crosses the medial boundary.
   Validate carbon distances, atom distances, the hard floor, and periodic seams globally as well.

## Search loop

- Explore at most 5 structurally distinct candidate branches. A correction round is not a new
  branch. In narrow-channel wall-first mode, prioritize the three primary-wall site-type branches,
  then the combined branch, then at most one alternative combined branch.
- Stop a branch after 4 consecutive validation rounds without meaningful improvement. There is no
  fixed iteration cap while metrics continue improving.
- A meaningful improvement is: a transition to an exact site normal, lower absolute polygon-site
  deviation, fewer corridor violations, better inter-atom distances, denser filling, or a better z
  seam without weakening a higher-priority constraint. A candidate is not improved or acceptable
  while any non-exempt atom fails the nearest-wall polygon-normal corridor, any finite or periodic
  nearest-neighbour distance is below `INTER_LOWER`, or any non-exempt near-wall atom is outside
  the global nearest-carbon corridor.
- Call `save_run_checkpoint` after the baseline and every meaningful generate/edit/validate round. Include
  aligned `atoms` and `atom_ids`, branch number, metrics, no-improvement count, last edit, next
  hypothesis, and accepted variants. Resume from `list_run_checkpoints` / `load_run_checkpoint`.
- Before accepting a model, use `compare_structures` against all accepted models with the carbon z
  period and `distinct_rmsd_threshold=0.4`. Different atom counts are distinct; otherwise require a
  genuinely different packing.

## Procedure

1. Read channel parameters and constants. Determine whether ordinary/wide-channel mode or the
   narrow-channel wall-first mode applies. Call `get_polygon_reference_sites` in summary mode, then
   request only the site types or walls needed for the current branch. In narrow mode, select the
   primary Ox-aligned wall before generating atoms.
2. For a new model, call `generate_atoms_at_polygon_sites`. It is a pure source of candidates and
   deliberately does not merge close positions. Create different branches by choosing different
   symmetric subsets or stacking patterns. For rebuild, use `read_inter_atoms(file_name)` as the
   baseline and never use that source name as an output. Always remeasure generated candidates.
   In narrow mode, retain each source `wall_index` as generation provenance, but do not use it to
   override a different nearest wall found after movement.
3. Keep coordinates and stable `atom_id` aligned. Prefer `selected_atom_ids` for
   `delete_atoms`, `move_atoms_on_vector`, `move_atoms_to_channel_center`, and
   `move_atoms_along_plane_normal`.
4. After every meaningful correction round, run both:
   - `measure_polygon_site_distances` without reference-wall arguments for the authoritative
     nearest-wall target, exact/interpolated normal distance, corridor status, and legitimate
     central exemptions. A second call with explicit reference walls may be used only as a
     diagnostic comparison during construction;
   - `validate_structure` for the hard floor, inter-atom corridor, filling context, and
     z-periodicity. Reject the candidate when `dist_between_inter_atoms_corridor_check` reports any
     `atom_ids_below`, even if `hard_floor_check` passes. Also reject it when
     `dist_to_carbon_corridor_check` reports any non-exempt atom below or above its global
     nearest-carbon corridor; an exact source-wall normal is not an exception.
5. Resolve conflicts in this order: hard floor; the global nearest-carbon corridor; the
   `INTER_LOWER` finite-pair and periodic-seam gates; the nearest-wall polygon-normal corridor;
   exact polygon-site placement when feasible; closeness to `TARGET_INTER`; z seam and symmetry;
   filling. Reduce filling or reject the branch rather than weaken any of the first four gates.
6. For wall-relative corrections, use the measured `recommended_inward_shift`: positive moves
   inward, negative moves toward the current nearest wall. Re-measure after moving without reference-wall
   arguments in every mode; use the newly detected nearest wall for the next correction and for
   acceptance. In narrow mode, never replace this correction with movement toward the channel
   center. Only a legitimately exempt interior atom may ignore polygon recommendations and
   optimize packing and periodicity alone.
7. Build the elementary z-cell, replicate with `translate_atoms_along_z` where needed, and validate
   the seam. Once the intended cell spans a known number of carbon periods, pass that value as
   `required_z_period_multiplier` to both `validate_structure` and `write_final_structure`; do not
   let an incidental shorter match in a finite sample redefine the cell. `hard_floor_check` must
   pass for both explicit pairs and `periodic_seam_min_distance`. The seam must also be at least
   `INTER_LOWER`; reject any cell below that stricter limit even if its finite coordinates,
   `hard_floor_check`, and `z_periodicity_check` otherwise pass. Keep distinct, defensible
   compromises as separate accepted variants.
8. Before writing, re-run both reports on the exact final inline coordinates. Run the polygon
   report without reference-wall arguments. Require zero non-exempt
   `corridor_violation_atom_ids`, no hard-floor violations, a passed
   `dist_to_carbon_corridor_check`, no `atom_ids_below` in the inter-atom corridor check,
   `periodic_seam_min_distance >= INTER_LOWER`, and a valid z-periodic explanation. An upper
   inter-atom expansion or another soft corridor violation may be disclosed as a trade-off, but
   lower inter-atom compression, polygon-normal violations, and global nearest-carbon corridor
   violations may not. Pass `dist_to_carbon_corridor_check` among the `required_checks` to
   `write_final_structure`. Do not write an empty, duplicate, or critically invalid model. After
   writing, read the CSV back and repeat both reports without reference-wall overrides; delete the
   output if serialization or nearest-wall reassignment makes any critical gate fail.
9. Write only through `write_final_structure`, with `author="Codex"`. The result must be
   `final_one_ch-v{i}[-{stacking}]-Codex.csv`; never create an intermediate coordinate file and
   never create `final_all_ch-*`.

## Final report

For each written version report: file name and atom count; channel mode; primary wall and the
per-atom wall-assignment strategy; all targets including `INTER_LOWER`; wall-assigned versus
legitimately exempt central counts; alignment counts for center, vertex, edge midpoint, and
interpolation; min/mean/max
normal deviation and violating atom IDs; inter-atom min/mean/max, below-limit atom IDs, and
hard-floor result; global nearest-carbon min/mean/max and corridor result; z repeat and seam with an
explicit `INTER_LOWER` comparison; filling/diversity rationale; and the specific trade-off versus
other versions. Report every atom whose authoritative nearest wall changed from its source wall.
Report rejected branches separately and do not list them as written or accepted models.
