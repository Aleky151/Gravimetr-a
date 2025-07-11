import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1) Carga de datos
teo = pd.read_excel("Coordenadas_con_gravedad_teorica.xlsx")
interp = pd.read_excel("Gravedad_spline_interpolada.xlsx")

# 2) Merge sobre i,j
df = pd.merge(
    teo,
    interp,
    on=["i","j"],
    how="inner"
)

# 3) Renombrar columnas de gravedad para mayor claridad
df = df.rename(columns={
    "gravedad_teorica_mGal": "g_teo",
    "gravedad_spline":  "g_interp"
})

# 4) Cálculo de errores
df["residual"]    = df["g_interp"] - df["g_teo"]
df["abs_error"]   = df["residual"].abs()
df["percent_err"] = df["abs_error"] / df["g_teo"] * 100

# 5) Métricas globales
ME   = df["residual"].mean()
MAE  = mean_absolute_error(df["g_teo"], df["g_interp"])
RMSE = np.sqrt(mean_squared_error(df["g_teo"], df["g_interp"]))
MAPE = df["percent_err"].mean()
MAXE = df["abs_error"].max()

print("ME   = %.3f mGal"   % ME)
print("MAE  = %.3f mGal"   % MAE)
print("RMSE = %.3f mGal"   % RMSE)
print("MAPE = %.6f %%"      % MAPE)
print("Max |error| = %.3f mGal" % MAXE)

# 7) Cálculo de precisión relativa
mean_g_interp   = df["g_interp"].mean()
relative_prec   = MAXE / mean_g_interp

print(f"Valor medio g_interp = {mean_g_interp:.3f} mGal")
print(f"Precisión relativa = {relative_prec:.6e}  (adimensional)")
print(f"Precisión relativa = {relative_prec*100:.8f} %")

# 6) Margen de error E% (usando el g_interp en el punto de máxima diferencia)
idx_max = df["abs_error"].idxmax()
g_at_max = df.loc[idx_max, "g_interp"]
margin_error = MAXE / g_at_max * 100
print(f"Margen de error E% = {margin_error:.8f} %")

# 6) Gráficos de diagnóstico
  
# 6.1 Scatter g_interp vs g_teo
plt.figure(figsize=(6,6))
plt.scatter(df["g_teo"], df["g_interp"], s=20, alpha=0.6)
mn, mx = df[["g_teo","g_interp"]].min().min(), df[["g_teo","g_interp"]].max().max()
plt.plot([mn,mx],[mn,mx], 'r--', lw=1)
plt.xlabel("Gravedad teórica (mGal)")
plt.ylabel("Gravedad interpolada (mGal)")
plt.title("g_interp vs g_teo")
plt.grid(True)
plt.tight_layout()

# 6.2 Histograma de residuales
plt.figure(figsize=(6,4))
plt.hist(df["residual"], bins=30, color="C1", edgecolor="k", alpha=0.7)
plt.axvline(0, color='k', lw=1)
plt.xlabel("Residual (g_interp – g_teo) [mGal]")
plt.ylabel("Frecuencia")
plt.title("Histograma de residuales")
plt.tight_layout()

# 6.3 Mapa de residuales georreferenciado
plt.figure(figsize=(8,6))
sc = plt.scatter(
    df["lon"], 
    df["lat"], 
    c=df["residual"], 
    cmap="coolwarm", 
    s=25, 
    edgecolor="k", 
    linewidth=0.2
)
plt.colorbar(sc, label="Residual [mGal]")
plt.xlabel("Longitud")
plt.ylabel("Latitud")
plt.title("Mapa de residuales de gravedad")
plt.tight_layout()

plt.show()

