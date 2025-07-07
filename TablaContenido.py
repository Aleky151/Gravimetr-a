import pandas as pd
# Configuración inicial
EXCEL_PATH = "C:/Users/HP/OneDrive/Escritorio/PuntoSelectos/ValoresDEMPlusCoordImage.xlsx" 

PIXELES_A_BUSCAR = [[i, i] for i in range(106)]  # range(106) genera 0 a 105
ultima_fila = 105  # Asumiendo que tu imagen tiene 106 filas (0 a 105)
for j in range(107, 129):  # Desde 107 hasta 128 (inclusive)
    PIXELES_A_BUSCAR.append([ultima_fila, j])

def buscar_coordenadas(excel_path, coordenadas_busqueda):
    """Busca coordenadas en un archivo Excel y devuelve los resultados."""
    try:
        # Leer el archivo Excel
        df = pd.read_excel(
            excel_path,
            engine='openpyxl',
            usecols=['i', 'j', 'X', 'Y', 'Z']  # Asegurar que usa estas columnas
        )
        
        # Convertir las coordenadas a buscar en un DataFrame temporal
        busqueda_df = pd.DataFrame(coordenadas_busqueda, columns=['i', 'j'])
        
        # Fusionar con los datos originales para encontrar coincidencias
        resultados = pd.merge(
            busqueda_df,
            df,
            on=['i', 'j'],
            how='inner'
        )
        
        return resultados

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {excel_path}")
        return pd.DataFrame()  # DataFrame vacío en caso de error
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return pd.DataFrame()

# Ejecutar la búsqueda
resultados = buscar_coordenadas(EXCEL_PATH, PIXELES_A_BUSCAR)

# Mostrar resultados
if not resultados.empty:
    print("✅ Resultados encontrados:")
    print(resultados[['i', 'j', 'X', 'Y', 'Z']].to_string(
        index=False,
        float_format="%.2f",  # Mostrar 2 decimales para X, Y, Z
        justify='center'
    ))
    
    # Opcional: Guardar resultados en nuevo Excel
    resultados.to_excel("IncrementosData.xlsx", index=False)
    print("\n💾 Resultados guardados en 'IncrementosData.xlsx'")
else:
    print("⚠️ No se encontraron coincidencias o hubo un error.")