# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob

# 1. CONFIGURACIÓN DE RUTAS
directorio_actual = os.path.dirname(os.path.abspath(__file__))
path_entrada = os.path.join(directorio_actual, "Datos", "equipos")
path_salida_seasons = os.path.join(directorio_actual, "Datos", "Temporadas_Individuales")

if not os.path.exists(path_salida_seasons):
    os.makedirs(path_salida_seasons)

archivos = glob.glob(os.path.join(path_entrada, "estadisticas_partidos_E*.csv"))

def corregir_ritmo(pace_valor, minutos_str):
    try:
        if pd.isna(minutos_str) or minutos_str == "" or pace_valor == 0: 
            return pace_valor
        if pace_valor < 25: return pace_valor * 5
        if pace_valor > 150: return pace_valor / 5
        return pace_valor
    except:
        return pace_valor

def procesar_bloque_equipos(archivo):
    df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', engine='python')
    df.columns = [col.replace('\ufeff', '').strip() for col in df.columns]
    
    if 'ID Temporada' not in df.columns:
        for col in df.columns:
            if 'Temporada' in col:
                df.rename(columns={col: 'ID Temporada'}, inplace=True)

    if 'ID Temporada' not in df.columns: return []
    temp_id = str(df['ID Temporada'].iloc[0])
    
    cols_stats = [
        'Puntos Local', 'Puntos Visitante', 'T2i Local', 'T2i Visitante', 
        'T2a Local', 'T2a Visitante', 'T3i Local', 'T3i Visitante', 
        'T3a Local', 'T3a Visitante', 'T1i Local', 'T1i Visitante', 'T1a Local', 'T1a Visitante',
        'Posesiones Local', 'Posesiones Visitante', 'Pace Partido',
        'Asistencias Local', 'Asistencias Visitante', 'Perdidas Local', 'Perdidas Visitante',
        'Robos Local', 'Robos Visitante', 'Tapones Local', 'Tapones Visitante',
        'R.Ofe Local', 'R.Ofe Visitante', 'R.Def Local', 'R.Def Visitante', 'Val Local', 'Val Visitante'
    ]
    
    for col in cols_stats:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

    if 'Pace Partido' in df.columns:
        col_minutos = 'Minutos Local' if 'Minutos Local' in df.columns else None
        df['Pace_Corregido'] = df.apply(lambda x: corregir_ritmo(x['Pace Partido'], x[col_minutos] if col_minutos else ""), axis=1)
    else:
        df['Pace_Corregido'] = 0

    equipos = pd.unique(df[['Equipo Local', 'Equipo Visitante']].values.ravel('K'))
    lista_temporada = []

    for eq in equipos:
        if pd.isna(eq) or eq == "": continue 
        
        # Filtramos todos los partidos del equipo (local o visitante)
        df_eq = df[(df['Equipo Local'] == eq) | (df['Equipo Visitante'] == eq)]
        
        # Sacamos las fases únicas que ha disputado este equipo en la temporada (Regular Season, Playoffs, etc.)
        fases_equipo = pd.unique(df_eq['Fase'].dropna().values)
        
        for fase in fases_equipo:
            if pd.isna(fase) or fase == "": continue
            
            # Filtramos los partidos del equipo exclusivamente para ESTA fase
            L = df[(df['Equipo Local'] == eq) & (df['Fase'] == fase)]
            V = df[(df['Equipo Visitante'] == eq) & (df['Fase'] == fase)]
            
            partidos = len(L) + len(V)
            if partidos == 0: continue

            # EXTRACCIÓN DEL ID Y ENTRENADOR DEL EQUIPO 
            if not L.empty:
                id_equipo = L['ID Equipo Local'].iloc[0] if 'ID Equipo Local' in L.columns else ""
                entrenador = L['Entrenador Local'].iloc[-1] if 'Entrenador Local' in L.columns else ""
            elif not V.empty:
                id_equipo = V['ID Equipo Visitante'].iloc[0] if 'ID Equipo Visitante' in V.columns else ""
                entrenador = V['Entrenador Visitante'].iloc[-1] if 'Entrenador Visitante' in V.columns else ""
            else:
                id_equipo, entrenador = "", ""

            # --- ACUMULADOS ---
            pts = L['Puntos Local'].sum() + V['Puntos Visitante'].sum()
            pts_rival = L['Puntos Visitante'].sum() + V['Puntos Local'].sum()
            t2i, t2a = (L['T2i Local'].sum() + V['T2i Visitante'].sum()), (L['T2a Local'].sum() + V['T2a Visitante'].sum())
            t3i, t3a = (L['T3i Local'].sum() + V['T3i Visitante'].sum()), (L['T3a Local'].sum() + V['T3a Visitante'].sum())
            t1i, t1a = (L['T1i Local'].sum() + V['T1i Visitante'].sum()), (L['T1a Local'].sum() + V['T1a Visitante'].sum())
            ast = L['Asistencias Local'].sum() + V['Asistencias Visitante'].sum()
            per = L['Perdidas Local'].sum() + V['Perdidas Visitante'].sum()
            rob = L['Robos Local'].sum() + V['Robos Visitante'].sum()      
            tap = L['Tapones Local'].sum() + V['Tapones Visitante'].sum()  
            val = L['Val Local'].sum() + V['Val Visitante'].sum()
            ro, rd = (L['R.Ofe Local'].sum() + V['R.Ofe Visitante'].sum()), (L['R.Def Local'].sum() + V['R.Def Visitante'].sum())
            pos_eq = L['Posesiones Local'].sum() + V['Posesiones Visitante'].sum()
            
            # Rivales
            t2i_riv, t2a_riv = (L['T2i Visitante'].sum() + V['T2i Local'].sum()), (L['T2a Visitante'].sum() + V['T2a Local'].sum())
            t3i_riv, t3a_riv = (L['T3i Visitante'].sum() + V['T3i Local'].sum()), (L['T3a Visitante'].sum() + V['T3a Local'].sum())
            t1i_riv, t1a_riv = (L['T1i Visitante'].sum() + V['T1i Local'].sum()), (L['T1a Visitante'].sum() + V['T1a Local'].sum())
            per_riv = L['Perdidas Visitante'].sum() + V['Perdidas Local'].sum()
            ro_riv, rd_riv = (L['R.Ofe Visitante'].sum() + V['R.Ofe Local'].sum()), (L['R.Def Visitante'].sum() + V['R.Def Local'].sum())
            pos_riv = L['Posesiones Visitante'].sum() + V['Posesiones Local'].sum()

            fga = t2i + t3i
            fga_riv = t2i_riv + t3i_riv
            wins = (L['Puntos Local'] > L['Puntos Visitante']).sum() + (V['Puntos Visitante'] > V['Puntos Local']).sum()

            stats = {
                'Temporada': temp_id,
                'Equipo': eq,
                'ID Equipo': id_equipo,
                'Entrenador': entrenador,  
                'Fase': fase,              
                'Partidos': partidos,
                'W': wins,
                'L': partidos - wins,
                '%_Wins': round((wins / partidos) * 100, 1),
                'PPG': round(pts / partidos, 2),
                'Asist_PG': round(ast / partidos, 2),
                'Perd_PG': round(per / partidos, 2),
                'Robos_PG': round(rob / partidos, 2),      
                'Tapones_PG': round(tap / partidos, 2),    
                'AST/TO_Ratio': round(ast / per if per > 0 else 0, 2),
                'AST%': round((ast / (t2a + t3a) * 100) if (t2a + t3a) > 0 else 0, 2), 
                'Reb_Off_PG': round(ro / partidos, 2),
                'Reb_Def_PG': round(rd / partidos, 2),
                'REB%_Total': round(((ro + rd) / (ro + rd + ro_riv + rd_riv) * 100) if (ro + rd + ro_riv + rd_riv) > 0 else 0, 2),
                'Val_PG': round(val / partidos, 2),
                
                # Tiros por partido y porcentajes
                'T2a_PG': round(t2a / partidos, 2), 'T2i_PG': round(t2i / partidos, 2), '%T2': round(t2a/t2i*100 if t2i>0 else 0, 1),
                'T3a_PG': round(t3a / partidos, 2), 'T3i_PG': round(t3i / partidos, 2), '%T3': round(t3a/t3i*100 if t3i>0 else 0, 1),
                'T1a_PG': round(t1a / partidos, 2), 'T1i_PG': round(t1i / partidos, 2), '%T1': round(t1a/t1i*100 if t1i>0 else 0, 1),
                
                # Distribución de puntos
                '%_Pts_Triple': round((t3a * 3 / pts * 100) if pts > 0 else 0, 1),
                '%_Pts_Dos': round((t2a * 2 / pts * 100) if pts > 0 else 0, 1),
                '%_Pts_TL': round((t1a / pts * 100) if pts > 0 else 0, 1),
                
                'Pace_Medio': round(pd.concat([L['Pace_Corregido'], V['Pace_Corregido']]).mean(), 2),
                'ORTG': round((pts / pos_eq * 100) if pos_eq > 0 else 0, 2),
                'DRTG': round((pts_rival / pos_riv * 100) if pos_riv > 0 else 0, 2),
                'NetRTG': round(((pts / pos_eq * 100) - (pts_rival / pos_riv * 100)) if pos_eq > 0 else 0, 2),
                
                'eFG%': round(((t2a + 1.5 * t3a) / (fga if fga > 0 else 1)) * 100, 2), 
                'TS%': round((pts / (2 * (fga + 0.44 * t1i)) * 100) if (fga + 0.44 * t1i) > 0 else 0, 2),
                '3PAr': round((t3i / fga) if fga > 0 else 0, 3), 
                'FTr': round(t1i / fga if fga > 0 else 0, 3),
                'ORB%': round((ro / (ro + rd_riv) * 100) if (ro + rd_riv) > 0 else 0, 2), 
                'DRB%': round((rd / (rd + ro_riv) * 100) if (rd + ro_riv) > 0 else 0, 2),
                'Pts_Permitidos_PG': round(pts_rival / partidos, 2), 

                # --- LOS 4 FACTORES ---
                'eFG%_Ol': round((t2a + 1.5 * t3a) / fga if fga > 0 else 0, 4),
                'TOV%_Ol': round(per / (fga + 0.44 * t1i + per) if (fga + 0.44 * t1i + per) > 0 else 0, 4),
                'OREB%_Ol': round(ro / (ro + rd_riv) if (ro + rd_riv) > 0 else 0, 4),
                'FT/FGA_Ol': round(t1a / fga if fga > 0 else 0, 4),
                
                'eFG_opp%_Ol': round((t2a_riv + 1.5 * t3a_riv) / fga_riv if fga_riv > 0 else 0, 4),
                'TOV_opp%_Ol': round(per_riv / (fga_riv + 0.44 * t1i_riv + per_riv) if (fga_riv + 0.44 * t1i_riv + per_riv) > 0 else 0, 4),
                'DREB%_Ol': round(rd / (rd + ro_riv) if (rd + ro_riv) > 0 else 0, 4),
                'FT/FGA_opp_Ol': round(t1a_riv / fga_riv if fga_riv > 0 else 0, 4),

                'Equipo_FGA': fga,
                'Equipo_FTA': t1i,
                'Equipo_TOV': per
            }
            lista_temporada.append(stats)
    return lista_temporada

# --- EJECUCIÓN ---
for f in sorted(archivos):
    try:
        datos_temp = procesar_bloque_equipos(f)
        if not datos_temp: continue
        
        df_temp = pd.DataFrame(datos_temp)
        
        # Ordenación lógica: Primero por Fase (para que queden agrupadas) y luego por %_Wins descendente
        df_temp = df_temp.sort_values(by=['Fase', '%_Wins'], ascending=[True, False])
        
        temp_label = str(df_temp['Temporada'].iloc[0]).replace("/", "-")
        nombre_archivo = f"Euroleague_{temp_label}_FullStats.csv"
        ruta_archivo = os.path.join(path_salida_seasons, nombre_archivo)
        
        df_temp.to_csv(ruta_archivo, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        print(f"Exportado: {nombre_archivo}")
        
    except Exception as e:
        print(f"Error en {f}: {e}")

print(f"\nLISTO! Todos los archivos en {path_salida_seasons}")