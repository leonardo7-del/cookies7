from datetime import date, timedelta
from collections import defaultdict
from src.domain.services.venta_service import VentaService

class DashboardService:
    def __init__(self):
        self.venta_service = VentaService()

    def serie_ventas_ultimos_dias(self, dias=7):
        """Devuelve listas (fechas_str, totales) para los últimos N días."""
        fin = date.today()
        inicio = fin - timedelta(days=dias-1)
        ventas = self.venta_service.obtener_ventas_por_fecha(inicio, fin)
        totales_por_fecha = defaultdict(float)
        for v in ventas:
            try:
                # v.fecha_venta puede ser date/datetime
                f = v.fecha_venta
                if hasattr(f, 'date'):
                    f = f.date()
                totales_por_fecha[f] += float(getattr(v, 'total', 0.0) or 0.0)
            except Exception:
                pass
        # Construir serie ordenada día a día
        fechas = []
        totales = []
        actual = inicio
        while actual <= fin:
            fechas.append(actual.strftime('%d-%m'))
            totales.append(round(totales_por_fecha.get(actual, 0.0), 2))
            actual += timedelta(days=1)
        return fechas, totales
