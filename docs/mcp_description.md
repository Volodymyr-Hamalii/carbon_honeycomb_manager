# MCP connectors, and the one in this project

This document has two halves. The first is general background: what MCP is, what a connector
actually does, and what you need to know to reason about one. The second describes the connector this
repository ships, how it is wired up, and how to extend it.

---

## Part 1. What an MCP connector is

### The problem it solves

An AI agent can read and write files and run shell commands, but that is a blunt instrument for a
codebase like this one. To answer "what is the distance from this intercalated atom to the nearest
carbon", the agent would have to write a throwaway Python script, import the right modules, guess at
the API, run it, and parse the output. Every time. It is slow, it is easy to get wrong, and the agent
has to re-derive your domain knowledge from scratch on every session.

The **Model Context Protocol (MCP)** is an open protocol that inverts this: instead of the agent
figuring out how to use your code, _you_ publish a set of named, documented, typed operations, and
the agent calls them the same way it calls its built-in tools. MCP is to AI agents roughly what a
REST API is to web clients - a stable contract in front of your internals.

### The three moving parts

1. **Host / client** - the application the user talks to (Claude Code, the Claude desktop app,
   Cowork, an IDE plugin). It owns the conversation and decides which tools to call.
2. **Server (the "connector")** - your process. It advertises a list of capabilities and executes
   them when asked. This is the part you write.
3. **Transport** - how the two talk. Two options matter in practice:
   - **stdio** - the client launches your server as a child process and talks over its stdin/stdout.
     Simple, local, no ports, no auth. This is what a project-local connector should use.
   - **streamable HTTP** - your server runs somewhere reachable over the network. Needed for shared
     or hosted servers, and then authentication becomes your problem.

### What a server can advertise

- **Tools** - functions the agent can call. Each has a name, a description, and a JSON Schema for its
  arguments. This is what you will use 95% of the time.
- **Resources** - readable content addressed by URI (like files). Useful for "here is a document, read
  it if you need it".
- **Prompts** - reusable prompt templates the user can invoke.

### The parts that actually decide whether it works

The protocol is the easy half. What determines whether an agent uses your connector well:

- **Tool descriptions are the API documentation, and the only one the agent gets.** The agent picks a
  tool by reading its name, its docstring and its parameter names. A tool called `process` with the
  docstring `"process the data"` will be used wrongly or not at all. Say what it returns, what the
  units are, and when _not_ to use it.
- **Granularity.** Too coarse ("build the whole structure") and the agent cannot steer or recover from
  a bad intermediate step. Too fine ("add two floats") and it burns turns on plumbing. Aim for
  operations a domain expert would name out loud.
- **Payload size.** Every result goes into the model's context. Returning 300 carbon coordinates when
  the agent needed a count is expensive and crowds out its reasoning. Offer a summary by default and a
  way to ask for the detail.
- **Statelessness.** Tools that mutate hidden server state are hard for an agent to reason about,
  because it cannot see that state. Prefer passing data in and getting data out.
- **Where the rules live.** See below - this is the single most important design decision in this
  connector.

### Rules belong in the skill, not in the server

A connector that answers "is this structure correct?" has baked one particular definition of
"correct" into code. The moment you want a second workflow with different criteria, you have to fork
the server or add flags to it.

The alternative: the server answers "here are the measurements and here is what is outside the
bounds _you gave me_", and the criteria live in a **skill** - a markdown document the agent loads
that describes the rules, the priorities and the procedure. Rules become text you can edit and argue
about; the server stays a measuring instrument. Multiple skills with contradictory rules can then
share one connector.

### Security, briefly

An MCP server runs with your permissions. A stdio server launched from a project config is as
trusted as the repository it lives in. Two habits worth keeping:

- Treat tool _arguments_ as untrusted input - they are ultimately produced by a model that may have
  read untrusted content. Validate paths and indexes rather than interpolating them into file
  operations.
- Be deliberate about which tools can destroy data. A tool that overwrites a file should say so in
  its description, and irreversible operations are better left to the human.

---

## Part 2. The connector in this project

### What it is for

`carbon-honeycomb-manager` exposes this project's domain layer - carbon channel geometry, distance
measurement, intercalated-atom editing and validation - so an agent can build intercalated structures
interactively instead of the user doing it by hand in Excel.

It was built for the task in
[`tasks/task_1.0_create_tools_for_claude_work.md`](../tasks/task_1.0_create_tools_for_claude_work.md)
and is driven by synchronized Codex and Claude skills:
[`.agents/.../SKILL.md`](../.agents/skills/calculate-intercalation-structure-related-carbon-atoms/SKILL.md)
and [`.claude/.../SKILL.md`](../.claude/skills/calculate-intercalation-structure-related-carbon-atoms/SKILL.md).
The polygon-reference workflow has its own synchronized
[Codex](../.agents/skills/calculate-intercalation-structure-related-carbon-polygon-points/SKILL.md)
and [Claude](../.claude/skills/calculate-intercalation-structure-related-carbon-polygon-points/SKILL.md)
skills so its center/vertex/edge-midpoint policy remains outside the server.

### Two design rules it follows

**It is rule-agnostic.** `validate_structure` takes every target and tolerance as an argument -
target distance to carbon, target distance between intercalated atoms, the deviation corridor, the
hard minimum, the z-periodicity tolerance. Unset arguments fall back to the values from
`get_intercalation_constants` for that element and structure. The report contains measurements and
violation flags; it never says "good" or "bad". The rules of the current workflow (rules 1-5, their
priority, the 8%/10% corridor, the rule-4-versus-corridor trade-off) live in the skill markdown.
A future skill with different rules reuses the server unchanged.

**It is element-agnostic.** `element` is a required argument of every structure tool, and all physical
constants resolve through `ATOM_PARAMS_MAP[element]` and the carbon geometry of the structure itself.
There are no argon numbers in the code. The same tools work for `ar`, `xe`, `kr` and `al`.

> Note: `Average {element}-C distance` depends on the **structure** as well as the element, because it
> is averaged with the real C-C distances of that structure. Do not cache it per element.

### Layout

```
src/mcp_server/
├── __main__.py                    # entry point: python -m src.mcp_server
├── server.py                      # the MCPServer instance and all @server.tool() functions
├── channel_provider.py            # cached carbon channel construction (expensive, so memoized)
├── mvp_params_adapter.py          # explicit tool arguments -> the GUI-oriented MvpParams dataclass
├── validation_targets_builder.py  # resolves unset validation targets from the project constants
└── serializers.py                 # domain objects <-> JSON-friendly lists and dicts
```

The package depends on the domain layer (`src.projects`, `src.services`, `src.entities`), and nothing
in the domain layer depends on it. The server can be changed or removed without touching the GUI
application.

### Registration

[`.mcp.json`](../.mcp.json) in the repository root:

```json
{
  "mcpServers": {
    "carbon-honeycomb-manager": {
      "type": "stdio",
      "command": ".venv/bin/python",
      "args": ["-m", "src.mcp_server"],
      "env": { "MPLBACKEND": "Agg", "LEVEL": "30" }
    }
  }
}
```

Any MCP client that reads `.mcp.json` from the project root picks it up. Requires
`pip install -r requirements.txt` (the `mcp` package was added for this).

The two environment variables matter:

- `MPLBACKEND=Agg` - the domain layer imports `matplotlib.pyplot`; without a headless backend a
  server process can try to touch a GUI.
- `LEVEL=30` - raises the project logger to `warning`, so routine `info` lines do not flood stderr.

### Why stdio needs care about stdout

Over the stdio transport, **stdout is the protocol channel**. A stray `print()` anywhere in the
import chain corrupts the JSON-RPC stream and the client drops the connection. `__main__.py` therefore
sets the matplotlib backend and moves any root logging handler that writes to stdout over to stderr
before the server starts. If you add code to the server, log - do not print.

### The tools

30 tools, grouped by what they do.

**Discovery**

| Tool                | Returns                                                                                                           |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `list_projects`     | project directories under `data/projects`                                                                         |
| `list_elements`     | elements with data, plus the elements the code supports                                                           |
| `list_structures`   | init-data structure directories for an element (real subdirectories only, so stray `.DS_Store` files are skipped) |
| `list_result_files` | result-data files and the next free version per ordered layer type                                                  |

**Metadata**

| Tool                          | Returns                                                                                         |
| ----------------------------- | ----------------------------------------------------------------------------------------------- |
| `get_intercalation_constants` | the GUI `Get intercalation constants` table for an element + structure pair                     |
| `get_channel_params`          | channel center, coordinate limits, z self-repeat period, per-plane polygon and edge-hole counts |
| `get_plane_geometry`          | plane equation, polygon centers and edge holes of one wall                                      |
| `get_carbon_coordinates`      | carbon coordinates of the channel or of a single wall                                           |

**Intercalated atoms**

| Tool                    | Does                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| `read_inter_atoms`      | reads coordinate `.csv` plus legacy `.xlsx` / `.dat` files                                             |
| `write_inter_atoms`     | writes `atom_id, x_inter, y_inter, z_inter`; new files should use CSV                                  |
| `write_final_structure` | revalidates required checks and writes `one_ch[-{family}]-{type}-v{i}-{author}.csv` without overwriting |
| `get_distance_matrix`   | the GUI `Get distance matrix` for a saved file                                                         |

**Generators** (the GUI buttons)

`generate_atoms_near_planes`, `generate_atoms_opposite_centers`, `generate_atoms_opposite_faces`.

**Polygon-reference workflow**

- `get_polygon_reference_sites` returns stable ring-center, carbon-vertex and C-C edge-midpoint
  sites with source provenance and all wall/inward-normal associations. It supports type, wall,
  detail and result-limit filters.
- `generate_atoms_at_polygon_sites` is a pure, unmerged candidate generator. Center candidates use
  the center target; vertex and edge-midpoint candidates use the face target. Targets may be passed
  explicitly or resolved from the element constants.
- `measure_polygon_site_distances` reports per-atom in-plane alignment and interpolated normal
  targets, the -8%/+10% corridor flags, recommended inward shifts, and explicit central-atom
  exemptions. It accepts inline atoms or a saved file. By default it measures against the nearest
  wall; `reference_wall_index` fixes one source wall for all atoms, while aligned
  `reference_wall_indexes` supports mixed-wall models. It never makes an acceptance decision.

**Edit primitives**

`add_atoms`, `delete_atoms`, `move_atoms_on_vector`, `move_atoms_to_channel_center`,
`move_atoms_along_plane_normal`, `shift_atoms_along_z`, `translate_atoms_along_z`.

**Validation**

`validate_structure` - the numeric report described below.

Pass `required_z_period_multiplier` when the intended elementary cell deliberately spans a known
number of carbon periods. The seam is then measured against that explicit cell instead of an
incidental shorter repeat inferred from a finite coordinate sample. The value must not exceed
`max_z_period_multiplier`.

**Long-running search**

- `compare_structures` compares unordered candidates, optionally modulo the carbon z period.
- `save_run_checkpoint`, `load_run_checkpoint`, `list_run_checkpoints` persist explicit JSON run
  state under the structure's `.agent-runs` result subdirectory.

### Conventions the tools share

- Coordinates are lists of `[x, y, z]` triples in angstroms, rounded to 3 decimal places. Results
  also expose stable `atom_id` values. Measured values are rounded to 4.
- Every edit tool takes the atoms either **inline** via `atoms` or **from a file** via `file_name`,
  and returns the resulting coordinates. It writes a file only when `output_file_name` is given. This
  keeps the server stateless and lets an agent chain edits without file churn.
- Edit results are re-sorted by z, y, x after every operation. Atom indexes therefore shift, but
  `atom_id` remains stable; edit by `selected_atom_ids` whenever possible.
- The three MCP generators are pure and write no intermediate files. The GUI-facing generator
  methods still save their coordinate output, now as CSV.
- Path construction resolves every generated path and rejects any argument that escapes
  `data/projects`. Final names validate stacking/author components and never overwrite an existing
  final file.
- Errors are raised as exceptions; the client sees them as tool errors with the message.

### The validation report

`validate_structure` returns, per atom: coordinates; minimum distance to carbon and its deviation
from the target in percent; minimum distance to the nearest intercalated atom and its deviation;
minimum distance to a wall plane and which plane; whether the atom sits near a wall; the distances to
the 6 nearest carbon atoms and their spread; and which wall feature (hexagon center, pentagon center,
edge hole) the atom sits opposite to, at what normal distance and with what in-plane offset.

Aggregated: min / max / mean / median of each of those, the near-wall and central carbon distances
separately, the z range, and how many atoms sit opposite each kind of feature.

Plus four checks:

- `hard_floor_check` - no explicit pair of intercalated atoms and no inferred periodic seam closer
  than the physical minimum. Explicit offending pairs are listed; `periodic_seam_min_distance` and
  `periodic_seam_passed` cover the tiled-cell boundary. The guarded final writer therefore cannot
  accept a finite cell that becomes a hard clash when repeated.
- `dist_to_carbon_corridor_check` and `dist_between_inter_atoms_corridor_check` - which atoms fall
  below or above the allowed deviation corridor. The carbon one applies to near-wall atoms only (see
  below); the intercalated-intercalated one applies to every atom.
- `z_periodicity_check` - the smallest number `N` of carbon z periods after which the structure maps
  onto itself, the resulting repeat length, whether the match could be **verified against overlapping
  atoms**, and the tiling `seam` distances.

And two summaries: `violations` (a list of the checks that failed) and `compromise` (`both`,
`rule_4_over_corridor`, `corridor_over_rule_4`, `neither`).

#### Near-wall atoms versus central atoms

The intercalated-carbon equilibrium distance only constrains the atoms that actually touch a wall. The
atoms filling the middle of a wide channel are held in place by their intercalated neighbours, so they
sit far above `target_dist_to_carbon` - and that is correct, not a defect.

An atom counts as **near-wall** when its perpendicular distance to the closest wall plane is at most
`near_wall_max_dist_to_plane`, which defaults to `dist_to_carbon_upper_bound` (the upper edge of the
carbon corridor). The rationale for the default: an atom already further from the wall than the
largest acceptable intercalated-carbon distance cannot be at equilibrium with that wall.

Only near-wall atoms are checked against the carbon corridor. The rest appear in
`dist_to_carbon_corridor_check.atom_indexes_exempt` and never produce a violation. Note the split is
safe in the other direction: an atom that is _too close_ to a wall necessarily has a small distance to
the plane, so it is always classified near-wall and always checked.

Measured on the shipped references (argon, `target_dist_to_carbon` about 2.60 Å, near-wall limit about
2.86 Å):

| structure         | near-wall | dist to plane | dev from target | central | dist to plane | dev from target |
| ----------------- | --------- | ------------- | --------------- | ------- | ------------- | --------------- |
| `C2-7_h3` v1-ABAB | 18        | 2.504-2.604   | -0.1% .. +1.6%  | 9       | 3.984-6.834   | +54% .. +163%   |
| `B4-7_h7` v1-ABAB | 16        | 2.674-2.675   | +2.9% .. +7.5%  | 21      | 3.421-6.549   | +32% .. +152%   |
| `A3-7_h3` v1-ABAB | 18        | 2.160-2.168   | about 0%        | 9       | 3.648-6.620   | +43% .. +161%   |
| `B1-7_h7` v1-ABAB | 12        | 2.500-2.572   | about 0%        | 0       | -             | -               |

No atom in any reference lands between about 2.7 and 3.4 Å from a wall, so the two populations are
cleanly separated and the default limit is comfortably inside the gap.

Report `summary.min_dist_to_carbon_near_wall` for rule 1, not `summary.min_dist_to_carbon` - the
latter mixes both populations and looks alarming for a perfectly good structure (`B4-7_h7` reads a
mean deviation of +45% undivided, versus +5% across the atoms rule 1 actually constrains).

#### How the z self-repeat check works

Shifting the atom set along Oz by `N × carbon_z_period` must map it onto itself. Only the region
where the original and the shifted set overlap can be compared, which gives three outcomes:

- **match** - the sets agree inside the overlap;
- **mismatch** - they do not;
- **nothing to compare** - the set is shorter than the shift, so it repeats trivially but nothing was
  actually verified. Reported as `verified_by_overlap: false`.

The third case is normal and expected for a correctly built _elementary cell_, which by definition is
exactly one repeat tall. For those, read the `seam` block instead: the atoms are reduced to one
primitive cell, tiled once, and `min_dist_across_seam` is compared with `min_dist_inside_cell`. A much
smaller seam distance means the tiling clashes; a much larger one means it leaves a gap.
The seam distance is also part of `hard_floor_check`, so a seam below the physical hard minimum
fails the default `write_final_structure` gate even when all explicit pairs are safe.

Verified against the shipped references:

| structure    | file                              | atoms | min dist to C (mean) | nearest inter-inter | `min_period_multiplier`         |
| ------------ | --------------------------------- | ----- | -------------------- | ------------------- | ------------------------------- |
| `ar/A1-7_h3` | `final_one_ch-v1.xlsx`            | 3     | 2.717                | 4.320 (+15.1%)      | 1, verified                     |
| `ar/C0-7_h3` | `final_one_ch-v3-ABC.xlsx`        | 12    | 2.580                | 3.888 (+3.6%)       | 9, seam 3.904 vs interior 3.888 |
| `ar/B4-7_h7` | `final_one_ch-v1-ABAB-Volod.xlsx` | 37    | 3.764                | 3.758 (+0.1%)       | 2, verified                     |

`A1-7_h3` is reported as `rule_4_over_corridor` - it repeats along z but its 4.320 A spacing is above
the +10% corridor - which is exactly the trade-off recorded for it by hand.

### Performance

Building a carbon channel derives the wall planes, polygons and edge holes geometrically from the raw
`.dat` coordinates. It costs about 0.6 s for `ar/A1-7_h3` (72 atoms) and about 80 s for `ar/C0-7_h3`
(324 atoms), because the polygon search is combinatorial in the number of wall atoms.

`ChannelProvider` therefore memoizes the channel objects (`lru_cache`, 16 entries). Since
`CarbonHoneycombChannel` is a frozen dataclass with cached derived properties, caching the instance
caches the whole geometry: the first tool call against a large structure is slow, everything after it
is fast. Call `ChannelProvider.clear_cache()` if the init-data files change while the server is
running.

Practical consequence for an agent session: expect one slow call per structure, then work normally.

### The `PMvpParams` adapter

Every domain entry point (`IntercalationAndSorption.*`, `CarbonHoneycombModeller.*`) takes a
`PMvpParams` - a dataclass shaped around the GUI, carrying coordinate limits, a file name and a dozen
flags. Rewriting those signatures to take explicit arguments would touch every presenter and view, so
the MCP layer keeps `MvpParamsAdapter` instead: tools expose explicit typed arguments and the adapter
packs them into the dataclass the domain expects. Refactoring the domain signatures is deliberately
out of scope.

### Extending it

To add a tool:

1. Put the actual work in the domain layer (`src/projects/...` or `src/services/...`), with an
   interface in `src/interfaces/` when it becomes part of the public surface. The server should be a
   thin wrapper.
2. Add a `@server.tool()` function in `src/mcp_server/server.py`. Its signature becomes the JSON
   Schema, so annotate everything and give defaults for optional arguments.
3. Write the docstring for the agent, not for a developer: what it returns, in what units, and when
   not to use it. Mention any surprising behaviour - that is the only place the agent will see it.
4. Keep it rule-agnostic. If the tool needs a threshold, make it a parameter with a default resolved
   from the project constants.
5. Return JSON-friendly values (`serializers.py` has the helpers) and keep the payload proportionate.
6. Add a test. The domain logic is unit-testable without the server - see `tests/`, which uses a
   synthetic 6-wall channel with a hand-computed geometry instead of the real data files, so the
   suite runs in under a second.

### Known geometry findings worth knowing

Four defects were fixed while building this connector, and one of them changed observable behaviour.

**The polygon bond threshold.** `CarbonHoneycombPlaneActions` decided which pairs of wall atoms form a
polygon edge using `max(per-atom minimum distance) × 1.25`, which resolves to 1.863 A. In the shipped
structures the real C-C bonds span 1.440-1.540 A, but the two atoms flanking an edge hole of an
armchair-oriented wall are 1.641 A apart and are **not** bonded. Those spurious edges short-circuited
the real hexagons into 5-cycles, which is why `ar/C0-7_h3` reported 17 pentagons and 0 hexagons per
plane. The threshold is now `min(distance) × 1.1`, which sits between the longest real bond (+6.9%)
and the shortest non-bond (+14.0%).

After the fix, across all 24 shipped `ar` and `xe` structures: pentagon count is 0 everywhere, and the
hexagon counts are stable (`A1-7_h3` 3 per plane, `B4-7_h7` 24 per plane, `C1/C2/C3` 5/10/15).

**`C0-7_h3` walls genuinely contain no complete polygon.** This is the expected geometry, not a
remaining bug. `C0` is the narrowest armchair-oriented wall: its atom columns sit at x = 0, 1.428,
2.148, 3.575, and an armchair hexagon needs four columns spaced 0.72, 1.44, 0.72. No such set fits
inside the wall - every hexagon of a `C0` wall straddles a channel edge and so belongs to two planes
at once. Consequences:

- `hexagons_per_plane` and `pentagons_per_plane` are all zeros for `C0-7_h3`; `edge_holes_per_plane`
  is 17 and carries the wall features for rule 3.
- `ave_dist_between_closest_hexagon_centers` used to crash with
  `ValueError: XA must be a 2-dimensional array`. It now falls back to all polygon centers and
  returns `NaN` (serialized as `null`) with a warning when there are fewer than two.
- `CarbonHoneycombModeller.get_channel_params` used to crash the same way, with
  `IndexError: too many indices for array`, while computing `Min distance between hexagon layers`
  from an empty center array. It now returns `NaN` for that constant, with a warning. This one was
  found by running the tools on `xe/C0-7_h3`, and it broke `get_channel_params` for every C-family
  structure.
- `generate_atoms_near_planes` produces fewer candidates for `C0` than it used to, because it no
  longer places atoms opposite the 17 phantom pentagons. The remaining candidates come from the edge
  holes.
- To keep rule 3 measurable there, the validation report includes the per-atom
  `nearest_carbon_distances` and `nearest_carbon_spread`. An atom opposite a ring center is roughly
  equidistant from 6 carbon atoms, so a small spread indicates good placement even when
  `opposite_feature` is `null`.

If per-plane polygons turn out to be needed for the C-family, the fix is ring detection on the whole
channel bond graph rather than per plane - that would recover the bent hexagons that straddle the
edges. It is not implemented.

**`PointsMover.move_on_vector` ignored the z component**, applying `vector[2]` to the y column. Fixed;
it is used by `FullChannelBuilder` and `InterAtomsSetter` as well as by the new editor.
