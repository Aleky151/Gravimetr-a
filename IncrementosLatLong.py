import numpy as np
import pandas as pd

RUTA_EXCEL = 'IncrementosCoord.xlsx'
HOJA='Resultados'
TOTAL_FILAS = 129  # Aproximado o exacto si lo conoces
COLUMNAS = ['X', 'Y', 'Dist_Horizontal']

# Cargar datos desde un archivo Excel
data = pd.read_excel(
    RUTA_EXCEL,
    sheet_name=HOJA,
    usecols=COLUMNAS
)
"""
#WGS84 values:
# Constantes conocidas
a = 6378137         # semieje mayor (m)
e = 0.0069**(1/2) # excentricidad de la Tierra
# Supongamos que df['X'] contiene las latitudes en grados
theta_deg = data['X']
theta_rad = np.radians(theta_deg)

# Aplicar la fórmula
numeradorM = a * (1 - e**2)
denominadorM = (1 - e**2 * np.cos(theta_rad)**2)**(3/2)

# Calcular M promedio
M_promedio = np.mean(numeradorM / denominadorM)

print(f"⟨M⟩ = {M_promedio:.3f} metros")

numeradorNs= a * np.sin(theta_rad)
denominadorNs= (1 - e**2 * np.cos(theta_rad)**2)**(1/2)
#Nsen media
Ns_promedio = np.mean(numeradorNs / denominadorNs)

print(f"⟨Ns⟩ = {Ns_promedio:.3f} metros")

# Calcular incrementos de latitud y longitud
(-1)*data['∆Y']=data['Dist_Horizontal']/M_promedio
data['∆X']=data['Dist_Horizontal']/Ns_promedio
# Calcular incrementos promedio de latitud y longitud    
incrementoLat= np.mean((data['∆Y'].values)*(-1))
incrementoLong= np.mean(data['∆X'].values)
print(f"Incremento promedio de latitud: {incrementoLat:.6f} rad")
print(f"Incremento promedio de longitud: {incrementoLong:.6f} rad")

"""
# Constantes WGS84
a = 6378137.0  # semieje mayor (m)
e2 = 0.00669437999014  # excentricidad al cuadrado
e = np.sqrt(e2)

# Convertir latitud (X) a radianes
theta_rad = np.radians(data['X'])  # Asumiendo que 'X' es latitud en grados

# Cálculo de M (radio de curvatura meridional)
numeradorM = a * (1 - e2)
denominadorM = (1 - e2 * np.sin(theta_rad)**2)**(1.5)  # (3/2) = 1.5
M_promedio = np.mean(numeradorM / denominadorM)

# Cálculo de N (radio de curvatura primer vertical)
denominadorN = np.sqrt(1 - e2 * np.sin(theta_rad)**2)  # ¡Usar SIN!
N_promedio = np.mean(a / denominadorN)

print(f"⟨M⟩ = {M_promedio:.3f} metros")
print(f"⟨N⟩ = {N_promedio:.3f} metros")

# Calcular incrementos angulares (usar Dist_Horizontal)
data['dtheta'] = data['Dist_Horizontal'] / M_promedio  # radianes
data['dlambda'] = data['Dist_Horizontal'] / (N_promedio * np.cos(theta_rad))  # ¡Añadir cos(θ) para longitud!

# Incrementos promedio
incrementoLat = np.mean(data['dtheta'])
incrementoLong = np.mean(data['dlambda'])
print(f"Incremento promedio de latitud: {incrementoLat:.6f} rad")
print(f"Incremento promedio de longitud: {incrementoLong:.6f} rad")