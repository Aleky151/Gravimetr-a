import pandas as pd
import numpy as np
from scipy.linalg import lstsq
from scipy.optimize import fsolve
from CoeficientesDLT import obtenerCoefDLT
"""
Georreferenciación de imágenes utilizando el método DLT (Direct Linear Transformation).
"""
data=pd.read_csv('puntos_control.csv')
print (data.head())
coord_imagen=data[['x','y']].values
coord_terrestre=data[['X','Y','Z']].values
# Obtener coeficientes DLT
coeficientes_dlt= obtenerCoefDLT(coord_imagen, coord_terrestre)
# Coeficientes DLT obtenidos
print("Coeficientes c0 a c10:", coeficientes_dlt)
