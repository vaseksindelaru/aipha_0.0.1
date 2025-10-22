# shadow.py

import pandas as pd

class Shadow:
    """
    Representa una capa de conocimiento que analiza los resultados
    producidos por otras capas, sin conocer su implementación interna.
    """
    def __init__(self):
        print("[Shadow] Componente de análisis inicializado.")

    def analyze_pce_output(self, labels: pd.Series):
        """
        Analiza las etiquetas generadas por el PCE.
        Su único "conocimiento" es el formato de las etiquetas (1, -1, 0).
        """
        print("\n[Shadow] Recibiendo datos para análisis...")

        if labels.empty:
            print("[Shadow] No hay etiquetas para analizar.")
            return

        print("[Shadow] --- INICIO DEL ANÁLISIS DE SHADOW ---")

        num_events = len(labels)
        tp_count = (labels == 1).sum()
        sl_count = (labels == -1).sum()
        timeout_count = (labels == 0).sum()

        print(f"Total de eventos analizados: {num_events}")
        print(f"  - Take Profits (1): {tp_count} ({(tp_count/num_events)*100:.2f}%)")
        print(f"  - Stop Losses (-1): {sl_count} ({(sl_count/num_events)*100:.2f}%)")
        print(f"  - Timeouts (0):    {timeout_count} ({(timeout_count/num_events)*100:.2f}%)")

        print("[Shadow] --- FIN DEL ANÁLISIS DE SHADOW ---")