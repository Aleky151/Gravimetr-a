import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Leer el archivo
archivo = "Gravedad_spline_interpolada.xlsx"
df = pd.read_excel(archivo)

# Extraer columnas necesarias
lon = df['lon']
lat = df['lat']
grav = df['gravedad_spline']
i = df['i']
j = df['j']

# Obtener dimensiones únicas de la rejilla
n_i = len(np.unique(i))
n_j = len(np.unique(j))

# Reorganizar los datos en formato de rejilla (matriz)
lon_grid = lon.values.reshape((n_j, n_i))
lat_grid = lat.values.reshape((n_j, n_i))
grav_grid = grav.values.reshape((n_j, n_i))

# Graficar usando imshow
plt.figure(figsize=(10, 8))
# asumiendo df tiene columnas ['i','j','gravedad_spline','lon','lat']
pivot = df.pivot(index='j', columns='i', values='gravedad_spline')
lon_p  = df.pivot(index='j', columns='i', values='lon'             )
lat_p  = df.pivot(index='j', columns='i', values='lat'             )

plt.figure(figsize=(10,8))
plt.pcolormesh(
    lon_p.values,
    lat_p.values,
    pivot.values,
    cmap='viridis',
    shading='auto'
)
plt.colorbar(label='Gravedad (mGal)')
plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.title('Mapa de gravedad interpolada')

# aquí inviertes el ejex
plt.gca().invert_xaxis()

plt.show()
