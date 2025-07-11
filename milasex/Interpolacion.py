import numpy as np
import pandas as pd
from scipy.linalg import solve

# 1) Read your grid‐point file
df = pd.read_excel("ValoresDEMPlusCoordImage.xlsx")
df.rename(columns={"X": "lon", "Y": "lat", "Z": "alt"}, inplace=True)

# 2) Build your control-point DataFrame
control_data = [
    [-72.2303, -13.3136, 3321, 977108],
    [-72.2117, -13.3136, 3647, 977007.4],
    [-72.1947, -13.3136, 3300, 977114.5],
    [-72.2228, -13.32,   3656, 977004.7],
    [-72.215,  -13.32,   3690, 976994.3],
    [-72.2103, -13.3233, 3681, 976997.1],
    [-72.2206, -13.3258, 3713, 976987.2],
    [-72.2303, -13.3269, 3122, 977169.6],
    [-72.2061, -13.3283, 3740, 976978.9],
    [-72.2172, -13.3294, 3835, 976949.6],
    [-72.1947, -13.3294, 3498, 977053.6],
    [-72.2106, -13.3342, 4077, 976875],
    [-72.2172, -13.335,  3900, 976943.9],
    [-72.2064, -13.34,   3777, 976967.7],
    [-72.2303, -13.3428, 3216, 977140.9],
    [-72.2125, -13.3428, 3881, 976935.6],
    [-72.1947, -13.3428, 3576, 977029.8]
]
control_df = pd.DataFrame(control_data, columns=["lon", "lat", "alt", "gravedad"])

# 3) Utility: convert lat/lon → unit‐sphere Cartesian
def latlon_to_unitxyz(lat, lon):
    φ = np.radians(lat)
    λ = np.radians(lon)
    x = np.cos(φ) * np.cos(λ)
    y = np.cos(φ) * np.sin(λ)
    z = np.sin(φ)
    return np.vstack((x, y, z)).T  # shape (N,3)

# 4) Build the thin‐plate spline system at control points
pts = latlon_to_unitxyz(control_df["lat"].values,
                        control_df["lon"].values)
n = pts.shape[0]

# 4a) spherical distances θ_ij = arccos(P_i·P_j)
#     then G(θ)=θ^2 log(θ + ε)
dot = np.clip(pts @ pts.T, -1.0, 1.0)
θ = np.arccos(dot)
ε = 1e-6
G = θ**2 * np.log(θ + ε)

# 4b) low‐order polynomial terms P=[1, x, y, z]
P = np.hstack([np.ones((n,1)), pts])    # shape (n,4)

# 4c) assemble the (n+4)x(n+4) system
L = np.zeros((n+4, n+4))
L[:n, :n]     = G
L[:n, n:]     = P
L[n:, :n]     = P.T
# rhs: known gravity at controls, zeros for the polynomial constraints
rhs = np.zeros(n+4)
rhs[:n] = control_df["gravedad"].values

# 4d) solve for [α; β]
sol = solve(L, rhs, assume_a='sym')   # α are the first n entries, β the last 4
α = sol[:n]
β = sol[n:]    # β = [b0, b1, b2, b3]

# 5) now build an evaluator
def spheroidal_spline(lat, lon):
    """
    Evaluate the biharmonic spline at (lat,lon).
    """
    x, y, z = latlon_to_unitxyz(lat, lon)[0]
    p = np.array([1.0, x, y, z])
    # compute θ_i for this new point
    dots = np.clip(pts @ np.array([x,y,z]), -1.0, 1.0)
    t = np.arccos(dots)
    Gv = t**2 * np.log(t + ε)
    return Gv @ α + p @ β

# 6) apply it over your whole df
df["gravedad_spline"] = df.apply(
    lambda row: spheroidal_spline(row["lat"], row["lon"]), axis=1
)

# 7) write out
df.to_excel("Gravedad_spline_interpolada.xlsx", index=False)


