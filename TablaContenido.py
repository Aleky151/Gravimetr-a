import pandas as pd
# Configuración inicial
EXCEL_PATH = "C:/Users/HP/OneDrive/Escritorio/PuntoSelectos/ValoresDEMPlusCiG.xlsx" 

PIXELES_A_BUSCAR = [[0,0], [67,0], [128,0], [27,23], [55,23], [72,35], [35,44], [0,48], [87,53], [47,57], 
                    [128,57], [71,74], [47,77], [86,95], [0,105], [64,105], [128,105]]

def buscar_coordenadas(excel_path, coordenadas_busqueda):
    """Busca coordenadas en un archivo Excel y devuelve los resultados."""
    try:
        # Leer el archivo Excel
        df = pd.read_excel(
            excel_path,
            engine='openpyxl',
            usecols=['i', 'j', 'X', 'Y', 'Z', 'Pendiente', 'G']  # Asegurar que usa estas columnas
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
    print(resultados[['i', 'j', 'X', 'Y', 'Z','Pendiente','G']].to_string(
        index=False,
        float_format="%.2f",  # Mostrar 2 decimales para X, Y, Z
        justify='center'
    ))
    
    # Opcional: Guardar resultados en nuevo Excel
    resultados.to_excel("DataSelectaPG.xlsx", index=False)
    print("\n💾 Resultados guardados en 'DataSelectaPG.xlsx'")
else:
    print("⚠️ No se encontraron coincidencias o hubo un error.")