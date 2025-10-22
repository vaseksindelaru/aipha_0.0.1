# main.py

import pandas as pd
from potential_capture_engine import PotentialCaptureEngine
from shadow import Shadow

def create_sample_data():
    """Genera datos de precios y eventos de ejemplo."""
    dates = pd.to_datetime(pd.date_range(start='2023-01-01', periods=50))
    data = {
        'open':  [100, 101, 102, 103, 105, 104, 106, 108, 110, 112, 111, 109, 107, 105, 103] + [100] * 35,
        'high':  [101, 102, 103, 105, 106, 105, 107, 110, 112, 113, 112, 110, 108, 106, 104] + [102] * 35,
        'low':   [99,  100, 101, 102, 104, 103, 105, 107, 109, 110, 110, 108, 106, 104, 102] + [98] * 35,
        'close': [101, 102, 103, 105, 104, 106, 108, 110, 112, 111, 109, 107, 105, 103, 101] + [100] * 35
    }
    prices = pd.DataFrame(data, index=dates[:len(data['open'])])
    prices.index.name = 'timestamp'

    # Eventos en los que queremos iniciar una "operación"
    events = pd.Series([prices.index[0], prices.index[10]])
    return prices, events

if __name__ == "__main__":
    print("--- INICIANDO SISTEMA AIPHA (VERSIÓN SIMPLIFICADA) ---")

    # 1. Preparación de datos
    print("\n[Main] Creando datos de ejemplo...")
    precios, eventos = create_sample_data()
    print("Datos creados.")
    print("Eventos a analizar:", eventos.dt.date.to_list())

    # 2. Instanciación de la Capa 2 (PCE)
    print("\n[Main] Instanciando el PotentialCaptureEngine de Capa 2...")
    pce = PotentialCaptureEngine(tp_factor=5.0, sl_factor=3.0, time_limit=10)

    # 3. Instanciación de la Capa de Conocimiento (Shadow)
    print("\n[Main] Instanciando el componente Shadow...")
    shadow = Shadow()
    print("Shadow está listo para recibir análisis.")

    # 4. Orquestación del Flujo
    print("\n[Main] Solicitando al PCE que etiquete los eventos...")
    # Main llama a PCE y obtiene los resultados
    labeled_results = pce.label_events(precios, eventos)

    print("\n[Main] Resultados del etiquetado recibidos:")
    print(labeled_results)

    print("\n[Main] Enviando los resultados al Shadow para su análisis...")
    # Main pasa los resultados a Shadow, que no tiene idea de cómo se generaron
    shadow.analyze_pce_output(labeled_results)

    print("\n--- PROCESO COMPLETADO ---")