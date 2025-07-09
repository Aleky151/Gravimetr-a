import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve

# Cargar datos
df_dem = pd.read_csv("CSValoresDEMcola.csv")  # Puntos a interpolar
df_control = pd.read_csv("Puntos_referencia.csv")  # Puntos con gravedad conocida

# Convertir a radianes
df_dem['theta'] = np.deg2rad(90 - df_dem['Latitud'])  # Co-latitud
df_dem['lambda_'] = np.deg2rad(df_dem['Longitud'])    # Longitud

# Parámetros WGS84
a = 6378137.0          # Semieje mayor (m)
e2 = 0.00669437999014  # Excentricidad al cuadrado

# Calcular M y N*sin(theta) para puntos de control (Ecuaciones 3 y 5)
def calcular_M_N(lat):
    theta = np.deg2rad(90 - lat)
    M = a * (1 - e2) / (1 - e2 * np.cos(theta)**2)**1.5
    N = a / np.sqrt(1 - e2 * np.sin(theta)**2)
    return M, N * np.sin(theta)

# Promedio de M y N*sin(theta) (Ecuaciones 15-16)
M_promedio = np.mean([calcular_M_N(lat)[0] for lat in df_control['Latitud']])
Nsin_promedio = np.mean([calcular_M_N(lat)[1] for lat in df_control['Latitud']])

# Resolución de la imagen (ej: 30m para Landsat)
q = 30  # metros
d_theta = q / M_promedio  # Incremento co-latitudinal (rad)
d_lambda = q / Nsin_promedio  # Incremento longitudinal (rad)

n_puntos = len(df_dem)
D = lil_matrix((n_puntos, n_puntos))  # Matriz dispersa
Y = np.zeros(n_puntos)

# Llenar la matriz D con coeficientes d_lk (simplificado)
for i in range(n_puntos):
    theta = df_dem.iloc[i]['theta']
    lambda_ = df_dem.iloc[i]['lambda_']
    
    # Coeficientes d_lk (ejemplo para d_0,0)
    d_00 = 2 * (np.cos(theta)**4 / ((1 - e2 * np.sin(theta)**2)**2 * d_lambda**4)) + \
           (-2/d_theta**2 - 2*np.cos(theta)**2 / (1 - e2 * np.sin(theta)**2))**2 + \
           (2 + d_theta * (1/np.tan(d_theta - theta)) / np.sqrt(1 - e2 * np.sin(theta)**2)) * \
           (2 - d_theta * (1/np.tan(theta)) / np.sqrt(1 - e2 * np.sin(theta)**2)) / (4 * d_theta**4)
    
    D[i, i] = d_00  # Diagonal principal
    # Añadir más coeficientes según Anexo 1 (d_-1,0, d_1,0, etc.)

# Asignar valores conocidos a Y
for idx, row in df_control.iterrows():
    idx_punto = df_dem[(df_dem['Latitud'] == row['Latitud']) & 
                       (df_dem['Longitud'] == row['Longitud'])].index[0]
    Y[idx_punto] = -row['g_teorica']  # Trasladar al lado derecho de la ecuación
    
D_csr = D.tocsr()  # Convertir a formato CSR para eficiencia
X = spsolve(D_csr, Y)  # Resolver el sistema

# Guardar resultados
df_dem['Gravedad_Interpolada'] = X
df_dem.to_csv("Resultados_Interpolacion.csv", index=False)

# --- NUEVO: Importar gravedad EGM2008 (g_teorica) y unir por Longitud y Latitud ---
df_egm = pd.read_csv("Resultados_Modelado_Geopotencial.csv")
df_dem = df_dem.merge(df_egm[['Longitud', 'Latitud', 'g_teorica']], on=['Longitud', 'Latitud'], how='left')

# Calcular diferencias
df_dem['Error'] = df_dem['Gravedad_Interpolada'] - df_dem['g_teorica']
print(f"Error máximo: {df_dem['Error'].abs().max():.2f} mGal")

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 8))
plt.scatter(df_dem['Longitud'], df_dem['Latitud'], c=df_dem['Gravedad_Interpolada'], 
            cmap='viridis', s=5)
plt.colorbar(label='Gravedad (mGal)')
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.title('Mapa de Gravedad Interpolada')
plt.savefig('Mapa_Gravedad.png', dpi=300)
plt.show()
