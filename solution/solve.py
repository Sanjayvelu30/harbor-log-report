import json
import math

# Helper function to check if theta is between a1 and a2 counter-clockwise
def is_angle_between(theta, a1, a2):
    # Normalize angles to [0, 2*pi)
    a1 = a1 % (2 * math.pi)
    a2 = a2 % (2 * math.pi)
    theta = theta % (2 * math.pi)
    if a1 < a2:
        return a1 <= theta <= a2
    else: # Arc crosses the 0/2pi boundary
        return theta >= a1 or theta <= a2

# Distance from a point P to a line segment
def distance_to_line(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    seg_len_sq = dx*dx + dy*dy
    if seg_len_sq < 1e-15:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))
    cx = x1 + t * dx
    cy = y1 + t * dy
    return math.hypot(px - cx, py - cy)

# Distance from a point P to a circular arc
def distance_to_arc(px, py, cx, cy, r, a1, a2):
    # Endpoint coordinates
    x1 = cx + r * math.cos(a1)
    y1 = cy + r * math.sin(a1)
    x2 = cx + r * math.cos(a2)
    y2 = cy + r * math.sin(a2)
    
    # Distance to endpoints
    d_end1 = math.hypot(px - x1, py - y1)
    d_end2 = math.hypot(px - x2, py - y2)
    
    # Angle of P relative to center
    theta = math.atan2(py - cy, px - cx)
    if is_angle_between(theta, a1, a2):
        # Distance to the circle itself
        d_circle = abs(math.hypot(px - cx, py - cy) - r)
        return min(d_circle, d_end1, d_end2)
    else:
        return min(d_end1, d_end2)

# Solve cubic equation a*t^3 + b*t^2 + c*t + d = 0 for t in [0, 1]
def solve_cubic(a, b, c, d):
    roots = []
    if abs(a) < 1e-12:
        # Solve quadratic: b*t^2 + c*t + d = 0
        if abs(b) < 1e-12:
            # Solve linear: c*t + d = 0
            if abs(c) > 1e-12:
                roots.append(-d / c)
        else:
            disc = c*c - 4*b*d
            if disc >= 0:
                sqrt_disc = math.sqrt(disc)
                roots.append((-c - sqrt_disc) / (2*b))
                roots.append((-c + sqrt_disc) / (2*b))
    else:
        # Depressed cubic: y^3 + p*y + q = 0
        A = b / a
        B = c / a
        C = d / a
        p = B - (A**2)/3.0
        q = C - (A*B)/3.0 + 2.0*(A**3)/27.0
        disc = (q**2)/4.0 + (p**3)/27.0
        if disc > 0:
            sqrt_disc = math.sqrt(disc)
            u = -q/2.0 + sqrt_disc
            v = -q/2.0 - sqrt_disc
            # Compute real cube root
            u_root = math.copysign(abs(u)**(1.0/3.0), u)
            v_root = math.copysign(abs(v)**(1.0/3.0), v)
            roots.append(u_root + v_root - A/3.0)
        else:
            # Three real roots (or multiple roots)
            if p < 0:
                phi = math.acos(max(-1.0, min(1.0, (-q/2.0) / math.sqrt(-p**3/27.0))))
                mult = 2.0 * math.sqrt(-p/3.0)
                roots.append(mult * math.cos(phi/3.0) - A/3.0)
                roots.append(mult * math.cos((phi + 2*math.pi)/3.0) - A/3.0)
                roots.append(mult * math.cos((phi + 4*math.pi)/3.0) - A/3.0)
            else:
                # p must be 0 if disc <= 0 and p >= 0
                roots.append(-A/3.0)
    return [r for r in roots if -1e-9 <= r <= 1.0 + 1e-9]

# Distance from a point P to a quadratic bezier curve
def distance_to_bezier(px, py, x0, y0, x1, y1, x2, y2):
    # B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2 = A*t^2 + B*t + C
    Ax = x0 - 2*x1 + x2
    Ay = y0 - 2*y1 + y2
    Bx = 2*(x1 - x0)
    By = 2*(y1 - y0)
    Cx = x0
    Cy = y0
    
    # Distance is ||B(t) - P||. Find t in [0, 1] minimizing this.
    # f(t) = ||B(t) - P||^2
    # f'(t) = 2 (B(t) - P) . B'(t) = 0
    Dx = Cx - px
    Dy = Cy - py
    
    a_coef = 2 * (Ax*Ax + Ay*Ay)
    b_coef = 3 * (Ax*Bx + Ay*By)
    c_coef = Bx*Bx + By*By + 2*(Ax*Dx + Ay*Dy)
    d_coef = Bx*Dx + By*Dy
    
    candidate_ts = [0.0, 1.0]
    roots = solve_cubic(a_coef, b_coef, c_coef, d_coef)
    for r in roots:
        t = max(0.0, min(1.0, r))
        candidate_ts.append(t)
        
    min_dist = float('inf')
    for t in candidate_ts:
        bx = (1-t)**2 * x0 + 2*(1-t)*t * x1 + t**2 * x2
        by = (1-t)**2 * y0 + 2*(1-t)*t * y1 + t**2 * y2
        dist = math.hypot(px - bx, py - by)
        if dist < min_dist:
            min_dist = dist
    return min_dist

# Total distance to the boundary
def distance_to_boundary(px, py, segments):
    min_d = float('inf')
    for seg in segments:
        if seg["type"] == "line":
            x1, y1 = seg["coords"][0]
            x2, y2 = seg["coords"][1]
            d = distance_to_line(px, py, x1, y1, x2, y2)
        elif seg["type"] == "arc":
            cx, cy = seg["center"]
            r = seg["radius"]
            a1, a2 = seg["angles"]
            d = distance_to_arc(px, py, cx, cy, r, a1, a2)
        elif seg["type"] == "bezier":
            x0, y0 = seg["control_points"][0]
            x1, y1 = seg["control_points"][1]
            x2, y2 = seg["control_points"][2]
            d = distance_to_bezier(px, py, x0, y0, x1, y1, x2, y2)
        else:
            raise ValueError(f"Unknown segment type: {seg['type']}")
        if d < min_d:
            min_d = d
    return min_d

# Ray casting crossing count with y perturbation to avoid degeneracies
def count_crossings(px, py, segments):
    y_prime = py
    for i in range(100):
        seed = float(i * 12345.6789)
        eps = ((seed % 1.0) - 0.5) * 1e-5
        candidate_y = py + eps
        
        clean = True
        for seg in segments:
            if seg["type"] == "line":
                y0, y1 = seg["coords"][0][1], seg["coords"][1][1]
                if abs(y0 - candidate_y) < 1e-7 or abs(y1 - candidate_y) < 1e-7:
                    clean = False
                    break
            elif seg["type"] == "arc":
                cx, cy = seg["center"]
                r = seg["radius"]
                a1, a2 = seg["angles"]
                y1_end = cy + r * math.sin(a1)
                y2_end = cy + r * math.sin(a2)
                if abs(y1_end - candidate_y) < 1e-7 or abs(y2_end - candidate_y) < 1e-7:
                    clean = False
                    break
                # Extremums
                for angle in [math.pi/2, -math.pi/2]:
                    if is_angle_between(angle, a1, a2):
                        y_ext = cy + r * math.sin(angle)
                        if abs(y_ext - candidate_y) < 1e-7:
                            clean = False
                            break
                if not clean:
                    break
            elif seg["type"] == "bezier":
                y0 = seg["control_points"][0][1]
                y1 = seg["control_points"][1][1]
                y2 = seg["control_points"][2][1]
                if abs(y0 - candidate_y) < 1e-7 or abs(y2 - candidate_y) < 1e-7:
                    clean = False
                    break
                Ay = y0 - 2*y1 + y2
                By = 2*(y1 - y0)
                if abs(Ay) > 1e-12:
                    t_ext = -By / (2*Ay)
                    if 0 <= t_ext <= 1:
                        y_ext = Ay * t_ext**2 + By * t_ext + y0
                        if abs(y_ext - candidate_y) < 1e-7:
                            clean = False
                            break
                if not clean:
                    break
        if clean:
            y_prime = candidate_y
            break
            
    crossings = 0
    for seg in segments:
        if seg["type"] == "line":
            x0, y0 = seg["coords"][0]
            x1, y1 = seg["coords"][1]
            if (y0 < y_prime < y1) or (y1 < y_prime < y0):
                t = (y_prime - y0) / (y1 - y0)
                x = x0 + t * (x1 - x0)
                if x > px:
                    crossings += 1
        elif seg["type"] == "arc":
            cx, cy = seg["center"]
            r = seg["radius"]
            a1, a2 = seg["angles"]
            if r**2 - (y_prime - cy)**2 >= 0:
                dx = math.sqrt(r**2 - (y_prime - cy)**2)
                for sign in [-1, 1]:
                    x = cx + sign * dx
                    if x > px:
                        theta = math.atan2(y_prime - cy, x - cx)
                        if is_angle_between(theta, a1, a2):
                            crossings += 1
        elif seg["type"] == "bezier":
            x0, y0 = seg["control_points"][0]
            x1, y1 = seg["control_points"][1]
            x2, y2 = seg["control_points"][2]
            
            Ay = y0 - 2*y1 + y2
            By = 2*(y1 - y0)
            Cy = y0 - y_prime
            
            ts = []
            if abs(Ay) < 1e-12:
                if abs(By) > 1e-12:
                    ts.append(-Cy / By)
            else:
                disc = By**2 - 4*Ay*Cy
                if disc >= 0:
                    sqrt_disc = math.sqrt(disc)
                    ts.append((-By - sqrt_disc) / (2*Ay))
                    ts.append((-By + sqrt_disc) / (2*Ay))
            for t in ts:
                if 0 < t < 1:
                    x = (1-t)**2 * x0 + 2*(1-t)*t * x1 + t**2 * x2
                    if x > px:
                        crossings += 1
    return crossings

def classify_point(px, py, segments):
    d = distance_to_boundary(px, py, segments)
    if d <= 1e-8:
        return "boundary"
    crossings = count_crossings(px, py, segments)
    if crossings % 2 == 1:
        return "inside"
    else:
        return "outside"

def main():
    with open("/app/boundary.json") as f:
        segments = json.load(f)
    with open("/app/points.json") as f:
        points = json.load(f)
        
    results = {}
    for pid, coords in points.items():
        px, py = coords
        results[pid] = classify_point(px, py, segments)
        
    with open("/app/results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
