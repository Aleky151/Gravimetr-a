import numpy as np
import pandas as pd
from scipy.special import lpmv  # Polinomios asociados de Legendre

# Cargar datos desde el archivo CSV
df = pd.read_csv("CSValoresDEM.csv", header=None, names=["Longitud", "Latitud", "Altura"])
df = df.apply(pd.to_numeric, errors='coerce')
df = df.dropna() 
lon = df["Longitud"].values
lat = df["Latitud"].values
h = df["Altura"].values

# Convertir coordenadas a radianes
theta = np.deg2rad(90 - lat)  # Co-latitud
lambda_ = np.deg2rad(lon)     # Longitud

# Constantes del modelo WGS84 y EGM2008
a = 6378137.0          # Semieje mayor (m)
omega = 7.292115e-5    # Velocidad angular de la Tierra (rad/s)
GM = 3.986004418e14    # Constante gravitacional geocéntrica (m³/s²)
e2 = 0.00669437999014  # Excentricidad al cuadrado (WGS84)

# Cargar coeficientes EGM2008 (ejemplo simplificado - deberías cargar el archivo completo)
def cargar_coeficientes_egm2008():
    """Función para cargar coeficientes armónicos esféricos del EGM2008"""
    # En la práctica, deberías cargar esto desde un archivo .txt o .gfc
    # Aquí solo ponemos algunos coeficientes como ejemplo
    a_nm = {
        (2,0): -0.484165371736e-3,  # C20
        (2,1): -0.206615509074e-9,   # C21
        (2,2): 0.243938357328e-5,    # C22
        # Agregar más coeficientes según sea necesario
    }
    b_nm = {
        (2,1): 0.138441389137e-8,    # S21
        (2,2): -0.140027370385e-5,   # S22
        # Agregar más coeficientes según sea necesario
    }
    return a_nm, b_nm

a_nm, b_nm = cargar_coeficientes_egm2008()

# Calcular el potencial gravitacional W_e (Ecuación 12 mejorada)
def potencial_gravitacional(theta, lambda_, a_nm, b_nm, nmax=360):
    """
    Calcula el potencial gravitacional usando armónicos esféricos
    """
    W_e = 0.0
    for n in range(nmax + 1):
        for m in range(n + 1):
            # Solo calcular si tenemos coeficientes para este n,m
            if (n,m) in a_nm or (n,m) in b_nm:
                Pnm = lpmv(m, n, np.cos(theta))
                term = Pnm * (a_nm.get((n,m), 0) * np.cos(m*lambda_) + 
                       b_nm.get((n,m), 0) * np.sin(m*lambda_))
                W_e += term
    
    # Normalizar y agregar término de rotación
    W_e = (GM/a) * W_e + 0.5 * (a**2) * (omega**2) * (np.sin(theta)**2)
    return W_e

# Calcular la gravedad teórica (mejorado)
def gravedad_teorica(theta, lambda_, a_nm, b_nm, h=0, nmax=360):
    """
    Calcula la gravedad normal en el elipsoide (sin considerar altura)
    """
    # Primero calculamos el potencial
    W = potencial_gravitacional(theta, lambda_, a_nm, b_nm, nmax)
    
    # Derivada respecto a theta (co-latitud)
    dtheta = 1e-8
    W_theta = potencial_gravitacional(theta + dtheta, lambda_, a_nm, b_nm, nmax)
    g_theta = (W - W_theta) / dtheta  # Componente norte
    
    # Derivada respecto a lambda (longitud)
    dlambda = 1e-8
    W_lambda = potencial_gravitacional(theta, lambda_ + dlambda, a_nm, b_nm, nmax)
    g_lambda = (W_lambda - W) / (dlambda * np.sin(theta))  # Componente este
    
    # Componente radial (aproximación)
    g_r = -9.780327 * (1 + 0.0053024 * np.sin(theta)**2 - 0.0000058 * np.sin(2*theta)**2)
    
    # Magnitud total (convertir a mGal)
    g_total = np.sqrt(g_theta**2 + g_lambda**2 + g_r**2) * 1e5  # m/s² a mGal
    return g_total

# Calcular valores de gravedad para todas las coordenadas
g_teorica = np.array([gravedad_teorica(t, l, a_nm, b_nm) for t, l in zip(theta, lambda_)])

# Guardar resultados en el DataFrame
df["We"] = [potencial_gravitacional(t, l, a_nm, b_nm) for t, l in zip(theta, lambda_)]
df["g_teorica"] = g_teorica

# Exportar resultados
df.to_csv("Resultados_Modelado_Geopotencial.csv", index=False)
print("✅ Resultados exportados: Resultados_Modelado_Geopotencial.csv")

def correccion_altura(g_teorica, h):
    """Aplica corrección por altura (Free-air correction)"""
    return g_teorica - (0.3086 * h)  # h en metros, corrección en mGal

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def plot_gravity_field(lon, lat, g_values):
    plt.figure(figsize=(12,8))
    m = Basemap(projection='merc', llcrnrlat=lat.min()-1, urcrnrlat=lat.max()+1,
                llcrnrlon=lon.min()-1, urcrnrlon=lon.max()+1, resolution='i')
    m.drawcoastlines()
    m.drawcountries()
    
    x, y = m(lon, lat)
    sc = m.scatter(x, y, c=g_values, s=10, cmap='jet')
    plt.colorbar(sc, label='Gravedad (mGal)')
    plt.title('Campo de gravedad teórico')
    plt.savefig('Mapa_Gravedad.png', dpi=300)
    plt.show()

# Graficar el campo de gravedad
plot_gravity_field(lon, lat, g_teorica)
print("✅ Mapa de gravedad generado: Mapa_Gravedad.png")

