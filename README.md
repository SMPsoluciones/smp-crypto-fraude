# ¿Cómo se reconoce una cuenta fraudulenta en Ethereum?

Caso de análisis de datos de **SMP Soluciones**. Un tablero en Streamlit que compara 9.816 cuentas de
Ethereum (2.179 marcadas como fraude) para mostrar en qué se comportan distinto y proponer una lista
simple de señales de alerta, con su tasa de acierto. En español por defecto; en inglés con `?lang=en`.

## Qué muestra

- **Resumen:** tres hallazgos calculados con los datos, cada uno con una acción concreta, y la tasa de fraude según la actividad de la cuenta.
- **Comportamiento:** valores típicos (medianas) de fraude contra legítimas: vida activa, ether recibido y enviado, con cuántas direcciones se relaciona y cada cuánto recibe.
- **Tokens:** los tokens ERC20 que más se asocian a cuentas fraudulentas, con un mínimo de cuentas por token.
- **Señales de alerta:** cuatro reglas transparentes (sin modelos de caja negra) y cuánto aciertan según cuántas se cumplan.
- **Datos:** la tabla filtrada, descarga en CSV y notas de método y limpieza.

Filtros: tipo de cuenta (todas, fraude, legítimas) y nivel de actividad.

## Cómo correrlo

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Si cambias la base de datos, regenera el archivo limpio con `python preparar_datos.py`.

## Datos

Fuente: **Ethereum Fraud Detection Dataset** (Kaggle). Una fila por dirección de Ethereum con su conducta
agregada y la marca de fraude (`FLAG`) que trae la fuente.

Limpieza (detalle en `preparar_datos.py`):
- 9.841 filas → 9.816 cuentas: 25 direcciones venían repetidas y se dejó la primera aparición.
- Nombres de columna con espacios al inicio, pasados a snake_case.
- 829 cuentas (todas fraudulentas) no traen datos de tokens ERC20: quedan como "sin dato", no como cero.
- Nombres de token basura (`0`, `None`, vacíos, caracteres de control) tratados como "sin dato".
- El tiempo entre envíos o recepciones vale 0 cuando hubo menos de dos: se toma como "no medible".
- 529 cuentas (todas fraudulentas) no tienen ninguna transacción de ether; se excluyen de las comparaciones de conducta.

## Archivos

| Archivo | Qué es |
|---|---|
| `app.py` | El tablero |
| `smp.py` | Base visual común de los casos de SMP Soluciones (colores, tarjetas, gráficos) |
| `preparar_datos.py` | Lee `fraud_crypto.db` y genera `datos/cuentas.csv.gz` |
| `datos/cuentas.csv.gz` | Datos limpios que usa el tablero |
| `fraud_crypto.db` | Base SQLite original (tabla `transactions` y agregados de la versión anterior) |
| `transactions.csv` | Datos originales en CSV |
| `crypto_queries.sql` | Consultas SQL de la exploración |
| `crypto_fraud_dashboard*.py` | Versiones anteriores del tablero (reemplazadas por `app.py`) |
| `.streamlit/config.toml` | Tema de Streamlit |
| `requirements.txt` | Dependencias |

Herramientas: Python, SQL (SQLite), pandas, Plotly y Streamlit.
