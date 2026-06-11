# TFG-Euroliga

Este repositorio contiene los scripts y flujos de datos desarrollados para el Trabajo Fin de Grado (TFG) en Ingeniería Informática en la Escuela Técnica Superior de Ingeniería Informática (ETSINF) de la Universitat Politècnica de València (UPV).

El objetivo del proyecto es construir una arquitectura de datos integrada (Pipeline ETL) que automatiza la ingesta, transformación y modelado semántico de los datos históricos de la Euroliga para su posterior análisis en un cuadro de mando de Power BI.


## Estructura del Repositorio

El desarrollo se divide en tres fases lógicas distribuidas en los siguientes módulos de scripts en Python:

### 1. Módulo de Extracción (Web Scraping)
Encargado de la obtención de los datos en bruto desde las plataformas oficiales.
* `estadisticas_partidos.py`: Extracción automatizada de los eventos y datos generales de los partidos por temporada.
    * Librerías: `selenium` (Webdriver, Options), `beautifulsoup4`, `json`, `pandas`, `time`, `warnings`, `datetime`.
* `estadisticas_jugadores.py`: Extracción del rendimiento estadístico de los jugadores a partir de las URLs de los partidos capturados previamente.
    * Librerías: `pandas`, `requests`, `os`, `time`, `random`, `re`.

### 2. Módulo de Transformación (Procesamiento y Analítica Avanzada)
Fase dedicada a la limpieza de datos, cálculo de métricas avanzadas de baloncesto (Four Factors, ritmos, eficiencias) y consolidación temporal.
* `analisis_avanzado_jugadores.py` y `analisis_avanzado_equipos.py`
* `promedios_jugadores.py` y `promedios_equipos.py` (Cálculo segmentado por temporada).
* `promedios_jugadores_todas.py` y `promedios_equipos_todas.py` (Unificación de series históricas).
* `historico_jugadores.py` y `historico_equipos.py`
    * Librerías: `pandas`, `glob`, `os`, `re`.

### 3. Módulo de Carga (Modelado Dimensional)
Scripts encargados de estructurar y normalizar los datos bajo un modelo en estrella (tablas de dimensiones y hechos) preparados para la capa de presentación.
* `dimFactequipos.py` y `FactHistoricoequipos.py`
* `dimfactjugadores.py` y `factHistorico_jugadores.py`
    * Librerías: `pandas`, `os`.



## Flujo de Ejecución e Instrucciones de Uso

**IMPORTANTE:** Para garantizar la integridad referencial y evitar errores de ejecución, **se debe completar el flujo de los EQUIPOS en primer lugar**, y posteriormente el flujo de los JUGADORES. Varios scripts del módulo de jugadores realizan cruces de datos mapeando los archivos de los equipos.

Para generar correctamente los archivos CSV finales destinados al modelo semántico, ejecute los scripts estrictamente en el siguiente orden secuencial:

### Fase I: Ingesta en Bruto
1. **Ejecutar `estadisticas_partidos.py`**: Debe correrse año a año para las temporadas deseadas (en este proyecto, desde la 2010 a la actual; se desconoce si funciona para temporadas anteriores).
2. **Ejecutar `estadisticas_jugadores.py`**: Requiere obligatoriamente que el script anterior haya finalizado, ya que consume dinámicamente las URLs de los partidos generadas en el paso anterior.

### Fase II: Enriquecimiento de Datos
3. **Ejecutar `analisis_avanzado_equipos.py` y `analisis_avanzado_jugadores.py`**: Incorpora algoritmos para añadir las estadísticas avanzadas a los registros de cada encuentro.
4. **Ejecutar `promedios_equipos.py` y `promedios_jugadores.py`**: Consolida las estadísticas medias de rendimiento, divididas de forma independiente en archivos anuales.

### Fase III: Unificación e Integración Cruzada
5. **Ejecutar `promedios_equipos_todas.py`**: Unifica el histórico completo de promedios de los clubes.
6. **Completar la Carga de Equipos (`dimFactequipos.py`)**: Es imperativo generar las dimensiones de los equipos en este punto para evitar fallos de desalineación en los nombres de los clubes.
7. **Ejecutar `promedios_jugadores_todas.py`**: Cruza los promedios globales de jugadores apoyándose en la tabla de dimensiones ya procesada de los equipos.
8. **Ejecutar `historico_equipos.py` e `historico_jugadores.py`**: Unifica en un único archivo los totales de cada equipo y jugador.

### Fase IV: Generación del Modelo en
