import pandas as pd
import numpy as np
from scipy.optimize import fsolve
from CoeficientesDLT import obtenerCoefDLT
import rasterio

"""
Georreferenciación de imágenes utilizando el método DLT (Direct Linear Transformation).
"""
data=pd.read_csv("C:\\Users\\HP\\OneDrive\\Escritorio\\Gravimetría\\CSValoresDEM.csv")
coord_terrestre=data[['X','Y','Z']].values

# Abrir el DEM
with rasterio.open("C:\\Users\\HP\\OneDrive\\Escritorio\\Gravimetría\\Aster DEM.tif") as dem:
    # Leer el CSV con coordenadas del DEM
    # Función para obtener i, j (fila, columna del píxel)
    def get_pixel_coords(row):
        col, row_ = dem.index(row['X'], row['Y'])  # nota: col = j, row_ = i
        return pd.Series({'x': row_, 'y': col})

    # Aplica la función al dataframe
    data[['x', 'y']] = data.apply(get_pixel_coords, axis=1)

# Listo: df ahora tiene las columnas i, j (coordenadas de imagen en el DEM)
""""""
coord_imagen=data[['x','y']].values
# Obtener coeficientes DLT
c= obtenerCoefDLT(coord_imagen, coord_terrestre)
# Coeficientes DLT obtenidos
print("Coeficientes c0 a c10:", c)
#Georreferenciacion de todos los pixeles
def sistemaEc(vars,Z,c,x,y):
    X, Y = vars
    d= 1 + c[8]*X + c[9]*Y + c[10]*Z
    eq1 = (c[0] + c[1]*X + c[2]*Y + c[3]*Z) / d - x
    eq2 = (c[4] + c[5]*X + c[6]*Y + c[7]*Z) / d - y
    return [eq1, eq2]
        
resultados = []

for idx, fila in data.iterrows():
    x = fila['x']
    y = fila['y']
    Z = fila['Z']
    initial_guess = [fila['X'], fila['Y']]
    X_sol, Y_sol = fsolve(sistemaEc, initial_guess)
    resultados.append([X_sol, Y_sol])

# Agrega las soluciones al DataFrame
data[['X_resuelto', 'Y_resuelto']] = resultados

# Guardar si quieres
# df.to_csv('resultados.csv', index=False)

def calcDistancia():
    # Calcular el desplazamiento hacia la siguiente fila (fila n+1)
    dx = data['X'].shift(-1) - data['X']
    dy = data['Y'].shift(-1) - data['Y']
    dz = data['Z'].shift(-1) - data['Z']
    # Calcular distancia euclidiana 3D
    data['distancia'] = np.sqrt(dx**2 + dy**2 + dz**2)

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
data['dtheta']=data['distancia']/M_promedio
data['dlambda']=data['distancia']/Ns_promedio
# Calcular incrementos promedio de latitud y longitud    
incrementoLat= np.mean(data['dtheta'].values)
incrementoLong= np.mean(data['dlambda'].values)

