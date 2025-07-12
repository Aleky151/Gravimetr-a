import pandas as pd
import numpy as np
from tqdm import tqdm
import os

# Configuración
RUTA_EXCEL = 'IncrementosData.xlsx'
HOJA = 'Sheet1'  # Cambia esto al nombre de tu hoja si es necesario'
TOTAL_FILAS = 129  # Aproximado o exacto si lo conoces
CHUNK_SIZE = 129
COLUMNAS = ['X', 'Y', 'Z']
ARCHIVO_SALIDA = 'IncrementosCoord.xlsx'

def procesar_excel_por_partes():
    # Primero verifiquemos el archivo de entrada
    if not os.path.exists(RUTA_EXCEL):
        raise FileNotFoundError(f"No se encontró el archivo {RUTA_EXCEL}")
    
    # Crear un DataFrame vacío para acumular resultados
    resultados_completos = pd.DataFrame()

    for chunk_num in tqdm(range(0, TOTAL_FILAS, CHUNK_SIZE), desc="Procesando Excel"):
        try:
            # Leer chunk actual
            df = pd.read_excel(
                RUTA_EXCEL,
                sheet_name=HOJA,
                skiprows=chunk_num + 1,  # +1 para saltar el header
                nrows=CHUNK_SIZE,
                header=None,
                names=COLUMNAS
            )
            
            # Verificar si el chunk está vacío
            if df.empty:
                continue
                
            # Calcular incrementos y distancias
            df['∆X'] = df['X'].diff()
            df['∆Y'] = df['Y'].diff()
            df['∆Z'] = df['Z'].diff()
            
            R = 6371000  # Radio de la Tierra en metros
            df['Dist_Horizontal'] = np.sqrt(
                (df['∆Y'] * (np.pi/180) * R)**2 + 
                (df['∆X'] * (np.pi/180) * R * np.cos(np.radians(df['Y'])))**2
            )
            df['Dist_3D'] = np.sqrt(df['Dist_Horizontal']**2 + df['∆Z']**2)
            
            # Eliminar filas con NaN (primera fila de cada chunk)
            df = df.dropna(subset=['∆X', '∆Y', '∆Z'])
            
            # Acumular resultados
            resultados_completos = pd.concat([resultados_completos, df], ignore_index=True)
            
        except Exception as e:
            print(f"Error procesando chunk {chunk_num}: {str(e)}")
            continue
    
    # Guardar todos los resultados al final
    try:
        resultados_completos.to_excel(
            ARCHIVO_SALIDA,
            sheet_name='Resultados',
            index=False,
            engine='openpyxl'
        )
    except Exception as e:
        print(f"Error al guardar el archivo de salida: {str(e)}")
        # Intentar guardar como CSV si falla Excel
        resultados_completos.to_csv('IncrementosCoord_respaldo.csv', index=False)
        print("Los resultados se guardaron como 'IncrementosCoord_respaldo.csv'")

if __name__ == "__main__":
    procesar_excel_por_partes()
    print(f"Procesamiento completado. Resultados en '{ARCHIVO_SALIDA}'")