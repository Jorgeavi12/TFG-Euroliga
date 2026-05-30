import pandas as pd
import os

# --- CONFIGURACIÓN ---
ruta_archivo = r'C:\Users\Jorge\Desktop\TFG\Datos\jugadores\Promedios_jugadores\Jugadores_Completo.csv'

# Diccionario basado en tu lista (Nombre: ID)
mapeo_equipos = {
    "AEK Athens": "AEK", "ALBA Berlin": "BER", "AS Monaco": "MCO", "AX Armani Exchange Milan": "MIL",
    "AX Armani Exchange Olimpia Milan": "MIL", "Alba Berlin": "BER", "Anadolu Efes Istanbul": "IST",
    "Armani Jeans Milano": "MIL", "Asseco Prokom Gdynia": "SOP", "Asvel Basket": "ASV",
    "Baskonia Vitoria Gasteiz": "BAS", "Baskonia Vitoria-Gasteiz": "BAS", "Belgacom Spirou Charleroi": "CHA",
    "Benetton Basket": "BEN", "Bennet Cantu": "CTU", "Brose Bamberg": "BAM", "Brose Baskets": "BAM",
    "Brose Baskets Bamberg": "BAM", "Budivelnik Kiev": "NIK", "Buducnost VOLI Podgorica": "BUD",
    "CSKA Moscow": "CSK", "Caja Laboral": "BAS", "Caja Laboral Vitoria": "BAS",
    "Cazoo Baskonia Vitoria-Gasteiz": "BAS", "Cholet Basket": "CHO", "Cibona VIP": "CIB",
    "Cibona Zagreb": "CIB", "Crvena Zvezda Meridianbet Belgrade": "RED", "Crvena Zvezda Telekom Belgrade": "RED",
    "Crvena Zvezda mts Belgrade": "RED", "Darussafaka Dogus Istanbul": "DAR", "Darussafaka Tekfen Istanbul": "DAR",
    "EA7 Emporio Armani": "MIL", "EA7 Emporio Armani Milan": "MIL", "Efes Pilsen": "IST",
    "Efes Pilsen Istanbul": "IST", "FC Barcelona": "BAR", "FC Barcelona Lassa": "BAR",
    "FC Barcelona Regal": "BAR", "FC Bayern Munich": "MUN", "Fenerbahce Beko Istanbul": "ULK",
    "Fenerbahce Dogus Istanbul": "ULK", "Fenerbahce Istanbul": "ULK", "Fenerbahce Ulker": "ULK",
    "Fenerbahce Ulker Istanbul": "ULK", "Galatasaray Liv Hospital Istanbul": "GAL",
    "Galatasaray Medical Park": "GAL", "Galatasaray Odeabank Istanbul": "GAL", "Gescrap Bilbao Basket": "BIL",
    "Herbalife Gran Canaria": "CAN", "Idea Slask": "SLA", "JSF Nanterre": "NTR",
    "KIROLBET Baskonia Vitoria Gasteiz": "BAS", "KIROLBET Baskonia Vitoria-Gasteiz": "BAS",
    "KRKA Novo Mesto": "KRK", "Khimki Moscow Region": "KHI", "LDLC ASVEL Villeurbanne": "ASV",
    "Laboral Kutxa Vitoria": "BAS", "Lietuvos Rytas Vilnius": "LIE", "Lokomotiv Kuban Krasnodar": "TIV",
    "Lottomatica Roma": "ROM", "Maccabi Electra Tel Aviv": "TEL", "Maccabi Elite Tel Aviv": "TEL",
    "Maccabi FOX Tel Aviv": "TEL", "Maccabi Playtika Tel Aviv": "TEL", "Montepaschi Siena": "SIE",
    "Olympiacos": "OLY", "Olympiacos Piraeus": "OLY", "Pamesa Valencia": "PAM", "Panathinaikos": "PAN",
    "Panathinaikos AKTOR Athens": "PAN", "Panathinaikos Athens": "PAN", "Panathinaikos OPAP Athens": "PAN",
    "Panathinaikos Superfoods Athens": "PAN", "Paris Basketball": "PRS", "Partizan": "PAR",
    "Partizan Mozzart Bet Belgrade": "PAR", "Partizan NIS Belgrade": "PAR", "Partizan mt:s Belgrade": "PAR",
    "Pau-Orthez": "PAU", "Power Electronics Valencia": "PAM", "Real Madrid": "MAD", "Regal Barcelona": "BAR",
    "SLUC Nancy": "NAN", "Skipper Fortitudo Bologna": "FOR", "Spirou Charleroi": "CHA",
    "Stelmet Zielona Gora": "GSS", "Strasbourg": "STR", "TD Systems Baskonia Vitoria-Gasteiz": "BAS",
    "Tau Ceramica": "BAS", "UNICS Kazan": "UNK", "Ulker": "ULK", "Unicaja": "MAL", "Unicaja Malaga": "MAL",
    "Unics Kazan": "UNK", "Union Olimpija": "LJU", "Union Olimpija Ljubljana": "LJU", "Valencia Basket": "VAL",
    "Virtus Segafredo Bologna": "VIR", "Zagreb": "ZAG", "Zalgiris": "ZAL", "Zalgiris Kaunas": "ZAL",
    "Zenit St Petersburg": "DYR"
}

def mapear_ids_jugadores():
    if not os.path.exists(ruta_archivo):
        print(f"❌ Error: No se encuentra el archivo en {ruta_archivo}")
        return

    print(f"⚙️ Leyendo archivo de jugadores...")
    # Cargamos el archivo respetando tu formato
    df = pd.read_csv(ruta_archivo, sep=';', decimal=',', encoding='utf-8-sig')

    # Limpiamos posibles espacios en blanco en la columna Equipo para asegurar el match
    df['Equipo'] = df['Equipo'].str.strip()

    print(f"🔍 Mapeando IDs de equipos...")
    # Creamos la serie de IDs basándonos en el nombre del equipo
    # Si un equipo no está en el diccionario, dejará un aviso
    df['ID_Equipo'] = df['Equipo'].map(mapeo_equipos)

    # Revisamos si algún equipo se quedó sin ID (porque el nombre no coincide exacto)
    sin_id = df[df['ID_Equipo'].isna()]['Equipo'].unique()
    if len(sin_id) > 0:
        print(f"⚠️ ¡Ojo! Estos equipos no están en tu diccionario: {sin_id}")

    # Reordenar columnas para meter ID_Equipo entre 'Equipo' y 'Partidos_Jugados'
    cols = list(df.columns)
    # Buscamos la posición de 'Equipo'
    idx_equipo = cols.index('Equipo')
    # Movemos 'ID_Equipo' (que ahora es la última) a la posición idx_equipo + 1
    new_cols = cols[:idx_equipo+1] + ['ID_Equipo'] + cols[idx_equipo+1:-1]
    df = df[new_cols]

    # Guardar el archivo sobrescribiendo el original
    df.to_csv(ruta_archivo, index=False, sep=';', encoding='utf-8-sig', decimal=',')
    
    print("-" * 30)
    print(f"✅ ¡Hecho! Columna ID_Equipo añadida con éxito.")
    print(f"📍 Archivo actualizado: {ruta_archivo}")

if __name__ == "__main__":
    mapear_ids_jugadores()