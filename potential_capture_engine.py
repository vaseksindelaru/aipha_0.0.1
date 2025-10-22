# potential_capture_engine.py

import pandas as pd

class PotentialCaptureEngine:
    """
    Una versión simplificada del motor de captura de potencial de Aipha 0.0.1.
    Utiliza barreras fijas de TP/SL y un límite de tiempo.
    """
    def __init__(self, tp_factor: float, sl_factor: float, time_limit: int):
        """
        Inicializa el motor con barreras fijas.

        Args:
            tp_factor (float): Factor porcentual para Take Profit. (ej. 5.0 para 5%)
            sl_factor (float): Factor porcentual para Stop Loss. (ej. 3.0 para 3%)
            time_limit (int): Número máximo de velas a esperar.
        """
        self.tp_factor = tp_factor / 100
        self.sl_factor = sl_factor / 100
        self.time_limit = time_limit
        print(f"[PCE] Motor inicializado con TP: {self.tp_factor*100}%, SL: {self.sl_factor*100}%, Límite: {self.time_limit} velas.")

    def label_events(self, prices: pd.DataFrame, t_events: pd.Series) -> pd.Series:
        """
        Etiqueta los eventos de trading.

        Args:
            prices (pd.DataFrame): DataFrame con columnas ['open', 'high', 'low', 'close'].
            t_events (pd.Series): Serie de timestamps que marcan el inicio de un evento.

        Returns:
            pd.Series: Serie con etiquetas (1 para TP, -1 para SL, 0 para timeout).
        """
        print("[PCE] Iniciando proceso de etiquetado...")
        out = pd.Series(index=t_events.index, dtype=float)

        for event_timestamp in t_events:
            entry_price = prices.loc[event_timestamp, 'close']

            tp_price = entry_price * (1 + self.tp_factor)
            sl_price = entry_price * (1 - self.sl_factor)

            # Recortamos el dataframe para mirar solo hacia el futuro desde el evento
            future_path = prices.loc[event_timestamp:].iloc[1:self.time_limit + 1]

            # ¿Tocó el Take Profit?
            hit_tp = future_path[future_path['high'] >= tp_price]

            # ¿Tocó el Stop Loss?
            hit_sl = future_path[future_path['low'] <= sl_price]

            if not hit_tp.empty and not hit_sl.empty:
                # Si ambos se tocan en el futuro, el primero en ocurrir gana
                out.loc[event_timestamp] = 1 if hit_tp.index[0] <= hit_sl.index[0] else -1
            elif not hit_tp.empty:
                out.loc[event_timestamp] = 1
            elif not hit_sl.empty:
                out.loc[event_timestamp] = -1
            else:
                # Si ninguno se toca, es un timeout
                out.loc[event_timestamp] = 0

        print("[PCE] Etiquetado completado.")
        return out.fillna(0) # Rellenamos por si acaso