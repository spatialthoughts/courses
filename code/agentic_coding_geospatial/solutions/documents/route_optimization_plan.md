# Delivery Route Optimization with OpenRouteService

## Context

`scripts/route_optimization.ipynb` currently loads 100 delivery locations and 14 grocery
stores (both Washington DC open-data extracts, EPSG:4326) and displays them on a Folium
map. The next step is to actually solve the routing problem: assign the 100 deliveries to
stores, group them into round-trip runs of exactly 10 stops each (store -> 10 stops ->
same store), respect each store's 5-trips/day cap, and minimize total distance traveled,
producing a trip schedule and a map of the optimized routes.

The user wants to use the OpenRouteService (ORS) Optimization API (built on the VROOM
solver) to do this. **Before finalizing the design, I ran live test calls against the
user's actual ORS API key** to check real request limits, since a naive single-call
"one big joint VRP solve" design was suspected to be infeasible at this scale. The tests
confirmed:

- **ORS Optimization endpoint**: max **3 vehicles** and **70 locations** per request.
  A single request covering all 14 stores x 5 trip-slots (70 vehicles) and all 100+14=114
  locations is rejected (`"Too many vehicles (25), maximum is set to 3"` /
  `"Too many locations (100), maximum is set to 70"`).
- **ORS Matrix endpoint**: max **3,500 distance pairs** per request. A full 114x114 matrix
  (12,996 pairs) doesn't fit, but a 14x100 store-to-delivery matrix (1,400 pairs) does.

Given these confirmed limits, the first implementation used a **two-stage design**: (1)
group the 100 deliveries into 10 geographic batches of exactly 10 using pure delivery-to-
delivery proximity, completely blind to store locations, then (2) assign each already-fixed
batch to the best store via the Hungarian algorithm. **This produced a real problem**: 5 of
14 stores ended up with zero trips while others served 2, including cases where a batch was
routed to a distant store even though a much closer store existed for some of its individual
stops — because the batch's shape was locked in before any store was considered, an
unlucky batch could end up centered far from every store, and the Hungarian step could only
pick the "least bad" store for it, not reshape the batch itself.

**Fix**: collapse batching and store-assignment into a single greedy joint step, so store
proximity drives batch formation from the start instead of being applied after the fact:

1. Get real road distances from every store to every delivery via **one** ORS Matrix call
   (14 x 100 = 1,400 pairs, under the 3,500-pair cap).
2. Greedily form the 10 trips one at a time: at each step, for every store that still has
   capacity (< 5 trips assigned), compute the cost of its cheapest possible batch (its 10
   nearest still-unassigned deliveries, by real road distance); pick whichever (store,
   batch) pairing is cheapest across all eligible stores; lock it in, remove those
   deliveries from the pool, and decrement that store's remaining capacity. Repeat until
   all 100 deliveries are placed into 10 trips.
3. For each of the 10 (store, batch) pairs, call ORS Optimization with exactly **1 vehicle +
   10 jobs** (11 locations) to get the exact optimal stop order and real route geometry.

This uses 1 + 10 = 11 ORS API calls total, same as before, all comfortably within the
confirmed limits — the only change is *how* the 10 (store, batch) pairs are chosen. It
also removes the need for the earlier planar-CRS/`cdist` batching step entirely — the
whole pairing decision is now driven by the one real-road-distance matrix.

**Testing this greedy-only version against the real data still left a residual problem**:
the same 9 of 14 stores ended up in use (5 idle), and one batch had a total cost of 73 km
versus 7-36 km for the rest. Root cause: the greedy locks in each batch's *shape* to
whichever store won that round (its 10 nearest remaining deliveries), but never re-checks
whether a *different* store — possibly one that's currently idle — would actually be
cheaper for that exact set of 10 points once they're fixed. Late rounds, working with
whatever scattered deliveries are left over, are the most exposed to this.

**Tried adding a polish step** (re-run the Hungarian algorithm to optimally reassign the
already-formed batches to stores) — this had no effect at all on the real data: since each
batch was constructed specifically as *that store's* cheapest available set, no other store
was ever cheaper for the exact same point set, so the reassignment never fired. A direct
diagnostic (comparing each delivery's actual serving store to its true nearest store)
confirmed the underlying problem was real: one idle store was the genuine nearest store for
three different deliveries, by gaps of up to 6.3 km, and never won a single greedy round
because its cheapest 10-batch (dominated by a few isolated points) couldn't compete on
total-batch-cost against a store with a tighter natural cluster elsewhere — even though it
was individually the better choice for those specific points.

**Final design — replace the batch-first greedy entirely with capacity allocation via local
search**, which optimizes the real objective (total assignment distance) directly instead
of a proxy:

1. **Allocate trip-slots to stores via local search.** Start from any feasible allocation
   (e.g. round-robin across the 14 stores). Repeatedly try moving one trip-slot from a
   store that has one to a store below its 5-trip cap; for each candidate move, solve the
   *exact* optimal delivery-to-store assignment for that resulting capacity vector (see
   step 2) and keep the move only if it lowers total assignment distance. Repeat until no
   single-slot move improves things. This lets genuinely under-served stores pick up trips
   (and overloaded ones give them up) based on real cost, not on which store happened to
   win an early round.
2. **Solve the exact optimal delivery-to-store assignment for a given capacity vector**,
   reused both inside the search and for the final allocation: expand each store into
   `n_trips[store] * 10` identical-cost columns (so the matrix has exactly 100 columns,
   matching the 100 deliveries), and solve with `scipy.optimize.linear_sum_assignment` —
   a perfect matching, so this is provably optimal given the capacity vector, not a
   heuristic.
3. **Split each store's now-fixed set of assigned deliveries into compact batches of 10**
   (only needed for stores running more than one trip) using the same nearest-neighbor
   chaining as the original design, scoped to just that store's own deliveries on a
   projected CRS (EPSG:32618) — this only affects in-trip routing efficiency, not which
   store serves which delivery, since that's already decided optimally in step 2.

**Verified this is a real improvement, not just a different heuristic**: total assignment
distance dropped from ~264-271 km (greedy / greedy+polish) to 237 km, the worst-case gap
between a delivery's actual store and its true nearest store dropped from 6.3 km to 2.6 km,
and the single 73 km outlier trip disappeared (new range: 8-34 km per trip). Some idle
stores remain — but now only when local search, directly re-optimizing total distance at
each step, confirms giving that store a trip would not reduce total distance, not as a side
effect of batch formation order.

The user also provided their real ORS API key directly and asked for it to be stored as a
plain constant in its own notebook cell (not `.env`/dotenv) — this will be honored, with a
one-line caution comment noting the key will be in plaintext in the notebook file.

**Per explicit user instruction, this calls the ORS REST API directly via `requests`**
(already available in the `claude_code_workshop` env as a dependency) rather than
installing the `openrouteservice` Python client package — no new package needs to be
installed. Two REST quirks were confirmed with live test calls against the endpoints and
must be handled manually since the convenience client isn't used:
- The Optimization endpoint only returns `distance`/`geometry` on the route if the request
  body includes `"options": {"g": true}` — the top-level `"geometry": true` field (shown in
  some docs/examples) was tested and silently returns `null` for both on this account.
- The returned `geometry` is a Google-style encoded polyline string (`[lon, lat]` order,
  precision 5), which needs a small manual decode function (no `openrouteservice.convert`
  helper available) — verified end-to-end against a live response (911 decoded points,
  start/end coordinates matching the requested store location within polyline rounding
  tolerance).

## Implementation

All new work is appended to the end of `scripts/route_optimization.ipynb` (after the
existing 8 cells: imports, data loading, previews, and the existing Folium map). Target
conda env: `claude_code_workshop` (already has geopandas, folium, pandas, scipy,
scikit-learn, pyogrio, shapely — confirmed via `conda list`).

No package installation is needed — everything is built on `requests` (already present)
plus packages already confirmed in the env (`scipy`, `numpy`, `pandas`).

**Notebook cells, in order (final):**

1. Markdown — `## Route Optimization` section intro: describes the problem (multi-depot
   capacitated VRP, 10 trips of 10 stops, 5-trip/store cap, minimize distance) and the
   approach (matrix -> local-search capacity allocation -> exact assignment -> compact
   grouping -> route), noting ORS's per-request limits (3 vehicles / 70 locations for
   Optimization, 3,500 pairs for Matrix), and briefly why a naive geography-first batching
   approach was replaced (see Context).
2. Code — imports: `requests`, `numpy as np`, `pandas as pd`, `time`,
   `from scipy.optimize import linear_sum_assignment`, `from scipy.spatial.distance import
   cdist`.
3. Markdown — `### API Key` + one-line caution that this key is stored in plaintext in the
   notebook and should be rotated/protected if the notebook is ever shared or this folder
   is put under git.
4. Code — `ORS_API_KEY = '<key>'` and `ORS_HEADERS = {'Authorization': ORS_API_KEY,
   'Content-Type': 'application/json'}`, plus the two endpoint URL constants
   (`https://api.openrouteservice.org/v2/matrix/driving-car` and
   `https://api.openrouteservice.org/optimization`).
5. Code — a small `decode_polyline(encoded, precision=5)` helper function implementing the
   standard Google-polyline decode algorithm (returns a list of `[lon, lat]` pairs) — needed
   because we're calling the REST API directly rather than using the `openrouteservice`
   client's built-in decoder. Include a one-line comment noting the ORS Optimization
   endpoint only includes `distance`/`geometry` in its response when the request body sets
   `"options": {"g": true}` (confirmed by testing — the alternate top-level `"geometry": true`
   field returns `null` for both on this account).
6. Markdown — `### Step 1 — Get store-to-delivery road distances`.
7. Code — one `requests.post(MATRIX_URL, json={'locations': store_coords +
   delivery_coords, 'sources': [0..13], 'destinations': [14..113], 'metrics':
   ['distance']}, headers=ORS_HEADERS)` call (1,400 pairs, under the 3,500 cap) to get a
   `store_delivery_distances` array (shape `n_stores x n_deliveries`, meters).
8. Markdown — `### Step 2 — Decide how many trips each store runs (local search)`: explains
   the search moves one trip-slot at a time and keeps a move only if it lowers the exact
   total assignment distance, so idle stores stay idle only when genuinely justified by cost.
9. Code — a `solve_assignment(n_trips)` helper: expand each store into `n_trips[store] * 10`
   identical-cost columns (100 columns total, matching the 100 deliveries), solve with
   `linear_sum_assignment`, return the total cost and the resulting `delivery -> store_idx`
   mapping. Start `n_trips` from a round-robin allocation across the 14 stores. Loop: for
   every (donor, receiver) store pair where donor has a trip to give and receiver is under
   its 5-trip cap, try moving one trip-slot and re-run `solve_assignment`; keep the first
   improving move found and restart the scan; stop when no move improves total cost.
10. Markdown — `### Step 2b — Assign every delivery to a store`: given the final capacity
    vector from the search, run the exact assignment once more to get `delivery_to_store`.
11. Code — `final_cost, delivery_to_store = solve_assignment(n_trips)`; print the final
    total assignment distance.
12. Markdown — `### Step 2c — Split each store's deliveries into compact trips of 10`:
    explains that store choice is already decided optimally; this step only groups a
    multi-trip store's deliveries into geographically compact batches for efficient
    in-trip routing.
13. Code — reproject `deliveries` to EPSG:32618; for each store, repeatedly take the
    unassigned member of its delivery set plus its 9 nearest same-store neighbors (via
    `cdist` on projected coordinates) to form one trip, until that store's assigned
    deliveries are fully grouped; append each group as `{'store_idx':, 'deliveries':}` to
    `trips`.
14. Code — sanity checks + summary table: assert `len(trips) == 10`, all 100 delivery
    indices covered exactly once, no store exceeds 5 trips; show a table of
    trip -> store -> batch cost (km).
15. Markdown — `### Step 3 — Solve optimal stop order per trip (ORS Optimization)`.
16. Code — loop over `trips`; for each, build `jobs` (10 deliveries: id, `[lon, lat]` from
    the original EPSG:4326 geometry — `geometry.x`/`geometry.y` is already lon/lat order,
    confirmed against the data, no swap needed) and a single-vehicle `vehicles` list
    (start=end=store's `[lon, lat]`, capacity=`[10]`); POST to the Optimization URL with
    `{'jobs': jobs, 'vehicles': vehicles, 'options': {'g': True}}`; store each result
    (ordered `steps`, `distance`, `duration`, `geometry` string). Add a short `time.sleep(1)`
    between calls as a courtesy against per-minute rate limits. Check `response['unassigned']`
    is empty each time and flag/print if not (edge case: a job ORS couldn't place).
17. Markdown — `### Step 4 — Build the trip schedule table`.
18. Code — assemble a `schedule_df` (one row per trip): `store` (name + address, since
    store names repeat across branches), `trip` (1..n within that store), ordered list of
    delivery addresses (via an id -> ADDRESS lookup built from `deliveries`), `n_stops`,
    `distance_km`, `duration_min`. Include final sanity checks: total stops across all trips
    == 100, no store's trip count exceeds 5 (grouped by `store_idx`, not by name). Display
    the table.
19. Markdown — `## Optimized Routes Map`.
20. Code — rebuild the existing store/delivery Folium map (same `.explore()` pattern as the
    current final cell), then for each trip decode its route geometry with the
    `decode_polyline` helper from cell 5 (returns `[lon, lat]` — must be swapped to
    `[lat, lon]` for Folium) and add it as a `folium.PolyLine` inside a
    `folium.FeatureGroup(name='Optimized Routes')` with a tooltip showing store/trip/distance,
    colored per trip; add `folium.LayerControl()` and display the map.

## Verification

- Execute the notebook end-to-end via
  `conda run -n claude_code_workshop jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=python3 scripts/route_optimization.ipynb`
  and confirm no cell errors.
- Confirm the printed sanity checks pass: 10 groups of exactly 10, no store exceeds 5
  trips, all 100 deliveries appear exactly once across the final schedule, no `unassigned`
  jobs reported by ORS.
- Visually inspect the final Folium map to confirm 10 distinct route loops are drawn, each
  starting/ending at its assigned store, with store and delivery markers still visible via
  layer toggles.

## Post-plan additions

Implemented after the original plan was approved and executed:

- **Export routes to GeoJSON**: all 10 trips saved as a single
  `outputs/route_optimization/routes.geojson` (one LineString feature per route plus a
  Point feature per stop, tagged with `trip`/`store`/`sequence`/`feature_type`) for
  validation in a GIS tool. An earlier version wrote one file per trip; consolidated into
  a single file per a follow-up request.
- **Store delivery manifests**: one PDF per store (via `reportlab`, installed into
  `claude_code_workshop` with the user's approval) in `outputs/route_optimization/`,
  named `manifest_{store_address}.pdf`, listing each of that store's trips with the
  delivery order and addresses in a table, for driver use / validation.
