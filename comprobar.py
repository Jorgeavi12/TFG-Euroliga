# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os

# Configuración de la ruta exacta de tus datos
ruta_datos = r"C:\Users\Jorge\Desktop\TFG\Datos"
# Buscamos los archivos que genera el scraper de jugadores (ej: estadisticas_jugadores2025.csv)
archivos = glob.glob(os.path.join(ruta_datos, "estadisticas_jugadores*.csv"))

if not archivos:
    print(f"❌ No se encontraron archivos 'estadisticas_jugadores*.csv' en la ruta: {ruta_datos}")
else:
    print("=" * 70)
    print(f"🔍 ARCHIVOS DE JUGADORES ENCONTRADOS: {len(archivos)}")
    print("=" * 70)

    for archivo in sorted(archivos):
        nombre_archivo = os.path.basename(archivo)
        print(f"\n📊 TOP 10 ANOTADORES PARA EL ARCHIVO: {nombre_archivo}")
        print("-" * 70)
        # Cabecera de la tabla alineada por terminal
        print(f"{'POS':<4} | {'JUGADOR':<25} | {'EQUIPO':<22} | {'PART':<5} | {'PTS TOT':<7} | {'PPG':<5}")
        print("-" * 70)
        
        try:
            # Leemos con el separador punto y coma (;) que usa tu scraper
            df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', engine='python')
            
            # Limpiamos espacios en las columnas por si acaso
            df.columns = [c.strip() for c in df.columns]
            
            # Verificación rápida de que el archivo es el correcto
            if 'Nombre' not in df.columns or 'Puntos' not in df.columns:
                print(f"⚠️  El archivo {nombre_archivo} no tiene las columnas 'Nombre' o 'Puntos'.")
                continue

            # Nos aseguramos de que los puntos sean numéricos
            df['Puntos'] = pd.to_numeric(df['Puntos'], errors='coerce').fillna(0)

            # Agrupamos por el ID Único del jugador (o por Nombre + Equipo para no mezclar)
            # Usamos Nombre y Equipo para mostrarlo bonito en la tabla
            agrupado = df.groupby(['Nombre', 'Equipo']).agg(
                Partidos=('ID Partido', 'count'),   # Cuenta cuántos partidos ha jugado
                Puntos_Totales=('Puntos', 'sum')    # Suma todos sus puntos
            ).reset_index()

            # Calculamos el promedio de puntos por partido (PPG) de cada uno
            agrupado['PPG'] = round(agrupado['Puntos_Totales'] / agrupado['Partidos'], 1)

            # Ordenamos de mayor a menor por Puntos Totales y nos quedamos con los 10 primeros
            top_10 = agrupado.sort_values(by='Puntos_Totales', ascending=False).head(10)

            # Imprimimos el Top 10 por pantalla
            posicion = 1
            for _, fila in top_10.iterrows():
                print(f"{posicion:<4} | {fila['Nombre'][:25]:<25} | {fila['Equipo'][:22]:<22} | {fila['Partidos']:<5} | {fila['Puntos_Totales']:<7} | {fila['PPG']:<5}")
                posicion += 1
                
        except Exception as e:
            print(f"❌ Error al procesar {nombre_archivo}: {e}")
            
        print("=" * 70)