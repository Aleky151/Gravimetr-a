import numpy as np
import pandas as pd

RUTA_EXCEL = 'IncrementosCoord.xlsx'
HOJA='Resultados'
TOTAL_FILAS = 129 # Total de filas a leer
COLUMNAS = ['X', 'Y', 'Dist_3D']

# Cargar datos desde un archivo Excel
data = pd.read_excel(
    RUTA_EXCEL,
    sheet_name=HOJA,
    usecols=COLUMNAS
)

#WGS84 values:
# Constantes WGS84
a = 6378137.0  # semieje mayor (m)
e2 = 0.00669437999014  # excentricidad al cuadrado
e = np.sqrt(e2)

# Convertir latitud (Y) de grados a radianes
theta_rad = np.radians(data['Y'])  

# Cálculo de M (radio de curvatura meridional)
numeradorM = a * (1 - e2)
denominadorM = (1 - e2 * np.sin(theta_rad)**2)**(1.5)  # (3/2) = 1.5
M_promedio = np.mean(numeradorM / denominadorM)

# Cálculo de N (radio de curvatura primer vertical)
denominadorN = np.sqrt(1 - e2 * np.sin(theta_rad)**2) 
N_promedio = np.mean(a / denominadorN)

print(f"⟨M⟩ = {M_promedio:.3f} metros")
print(f"⟨N⟩ = {N_promedio:.3f} metros")

# Calcular incrementos angulares (usar Dist_3D)
data['dtheta'] = data['Dist_3D'] / M_promedio  # radianes
data['dlambda'] = -data['Dist_3D'] / (N_promedio * np.sin(theta_rad))  

# Incrementos promedio
incrementoLat = np.mean(data['dtheta'])
incrementoLong = np.mean(data['dlambda'])
print(f"Incremento promedio de latitud: {incrementoLat:.6f} rad")
print(f"Incremento promedio de longitud: {incrementoLong:.6f} rad")

theta_promedio = np.mean(np.radians(data['Y']))  # Latitud promedio en radianes
print(f"sin(θ) promedio = {np.sin(theta_promedio):.3f}")