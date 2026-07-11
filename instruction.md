Determine whether a set of 2D coordinates lie "inside", "outside", or exactly on the "boundary" of a closed 2D region bounded by a mix of circular arcs, quadratic Bézier curves, and line segments.

### Inputs

1. `/app/boundary.json`: A list of boundary segments defining a simple closed path, where each segment is represented as:
   - A line segment: `{"type": "line", "coords": [[x1, y1], [x2, y2]]}` (from `[x1, y1]` to `[x2, y2]`).
   - A circular arc segment: `{"type": "arc", "center": [cx, cy], "radius": r, "angles": [a1, a2]}` (centered at `[cx, cy]` of radius `r`, traversing counterclockwise from angle `a1` to `a2` in radians).
   - A quadratic Bézier curve segment: `{"type": "bezier", "control_points": [[x0, y0], [x1, y1], [x2, y2]]}` (parametrized by $B(t) = (1-t)^2 P_0 + 2(1-t)t P_1 + t^2 P_2$ for $t \in [0, 1]$ where $P_0=[x0, y0], P_1=[x1, y1], P_2=[x2, y2]$).

2. `/app/points.json`: A JSON dictionary mapping point IDs (strings `"0"` to `"99"`) to coordinate pairs `[x, y]`.

### Requirements

- Classify each query point from `/app/points.json` as one of the following strings:
  - `"boundary"`: The Euclidean distance from the query point to the closest point on the boundary segments is $\le 10^{-9}$.
  - `"inside"`: The query point lies strictly inside the closed 2D region (and has a distance to the boundary $> 10^{-9}$).
  - `"outside"`: The query point lies strictly outside the closed 2D region (and has a distance to the boundary $> 10^{-9}$).
- Note: Non-boundary points are guaranteed to have a distance of at least $10^{-5}$ from the boundary to prevent numerical ambiguity.
- Write your classifications to a JSON file at `/app/results.json`, which must be a single JSON dictionary mapping each point ID (from `"0"` to `"99"`) to its exact classification string.

You have 1800 seconds to complete this task. The clock starts now.
