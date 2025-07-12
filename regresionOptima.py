import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Configuración optimizada
CHUNK_SIZE = 1000  # Tamaño de chunk reducido
SAMPLE_SIZE = 13000  # Tamaño de muestra para visualización

def load_and_process(file_path):
    """Carga y procesa el archivo de forma eficiente"""
    try:
        # Leer solo las columnas necesarias para ahorrar memoria
        df = pd.read_excel(file_path, usecols=['alt', 'gravedad_spline', 'lon', 'lat'])
        print(f"Datos cargados correctamente. Filas: {len(df)}")
        return df
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return None

def calculate_regression(df):
    """Calcula la regresión lineal y residuales"""
    if df is None or len(df) == 0:
        return None, None, None
    
    # Modelo global
    X = df[['alt']].values
    y = df['gravedad_spline'].values
    
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    residuals = y - y_pred
    
    return model, residuals, y_pred

def plot_results(df, residuals, sample_size=SAMPLE_SIZE):
    """Visualización optimizada de resultados"""
    if len(df) > sample_size:
        sample_idx = np.random.choice(len(df), sample_size, replace=False)
        df_sample = df.iloc[sample_idx]
        residuals_sample = residuals[sample_idx]
    else:
        df_sample = df
        residuals_sample = residuals
    
    # Gráfico de residuales
    plt.figure(figsize=(15, 10))
    
    # Residuales vs predichos
    plt.subplot(2, 2, 1)
    plt.scatter(df_sample['alt'], residuals_sample, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.title('Residuales vs Altitud')
    plt.xlabel('Altitud')
    plt.ylabel('Residuales')
    plt.grid(True)
    
    # Histograma de residuales
    plt.subplot(2, 2, 2)
    plt.hist(residuals_sample, bins=50, alpha=0.7)
    plt.title('Distribución de Residuales')
    plt.xlabel('Residuales')
    plt.ylabel('Frecuencia')
    plt.grid(True)
    
    # Mapa de residuales
    plt.subplot(2, 2, (3,4))
    scatter = plt.scatter(df_sample['lon'], df_sample['lat'], 
                        c=residuals_sample, cmap='coolwarm', 
                        alpha=0.7, s=20)
    plt.colorbar(scatter, label='Residuales')
    plt.title('Mapa de Residuales')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    file_path = 'Gravedad_spline_interpolada.xlsx'
    
    # Carga de datos
    df = load_and_process(file_path)
    if df is None:
        return
    
    # Cálculo de regresión
    model, residuals, y_pred = calculate_regression(df)
    if model is None:
        return
    
    # Resultados del modelo
    print("\nRESULTADOS DEL MODELO")
    print(f"Coeficiente (pendiente): {model.coef_[0]}")
    print(f"Intercepto: {model.intercept_}")
    print(f"Número de observaciones: {len(df)}")
    
    # Añadir residuales al DataFrame
    df['residual'] = residuals
    
    # Visualización
    plot_results(df, residuals)

if __name__ == "__main__":
    main()