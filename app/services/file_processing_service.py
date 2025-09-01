import pandas as pd
import os
import re
from io import BytesIO

# Obtener la ruta absoluta del directorio 'data/files'
BASE_FILES_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../../data/excels-positions')

# Asegurarse de que el directorio exista
os.makedirs(BASE_FILES_DIR, exist_ok=True)

def read_excel_from_bytes(file_bytes: BytesIO):
    return pd.read_excel(file_bytes, engine='openpyxl', header=None)

def _extraer_simbolo(texto):
    if not isinstance(texto, str):
        return texto

    if '-' in texto:
        partes = texto.split('-')
        simbolo = partes[-1].strip()
        prefijo = partes[0].strip()

        if prefijo == 'ADR':
            return simbolo
        elif prefijo in ['Dólar Cable', 'Peso Argentino']:
            return simbolo
        elif prefijo.startswith('CEDEAR'):
            return simbolo
        elif 'EXT' in texto and not simbolo.endswith('EXT'):
            return f"{simbolo} EXT"
        elif 'ADR' in texto and not simbolo.startswith('ADR'):
            return f"{simbolo} ADR"
        else:
            return simbolo
    return texto

def calculate_condor_latin_diff(df_latin: pd.DataFrame, df_condor: pd.DataFrame):
    especies_originales = df_latin.iloc[:, 0].copy()
    especies_procesadas = especies_originales.apply(_extraer_simbolo)

    diccionario_condor = dict(zip(df_condor.iloc[6:338, 1], df_condor.iloc[6:338, 3]))
    diccionario_latin = dict(zip(especies_procesadas, df_latin.iloc[:, 1]))

    diccionario_diferencias = {}
    for simbolo, cantidad_latin in diccionario_latin.items():
        if simbolo in diccionario_condor:
            cantidad_condor = diccionario_condor[simbolo]
            
            if pd.isna(cantidad_latin):
                cantidad_latin = 0 # Asumir 0 si es NaN

            try:
                diferencia = float(cantidad_condor) - float(cantidad_latin)
                if diferencia != 0:
                    diccionario_diferencias[simbolo] = {
                        "Qty-latin": cantidad_latin,
                        "Qty-argentina": cantidad_condor,
                        "Qty-diferencias": diferencia
                    }
            except (ValueError, TypeError):
                continue # Saltar si no se puede convertir a float
    return diccionario_diferencias

def calculate_condor_ibkr_diff(ibkr_bytes: bytes, condor_bytes: bytes, ibkr_filename: str):
    df_ibkr = pd.read_csv(BytesIO(ibkr_bytes), skiprows=1)
    df_condor = pd.read_excel(BytesIO(condor_bytes), engine="openpyxl", header=None)

    diccionario_condor = dict(zip(df_condor.iloc[6:319, 1], df_condor.iloc[6:319, 4].astype(int)))
    diccionario_ibkr = dict(zip(df_ibkr["Financial Instrument Description"], df_ibkr["Position"]))

    diccionario_diferencias = {}
    for simbolo, cantidad_condor in diccionario_condor.items():
        if simbolo in diccionario_ibkr:
            cantidad_ibkr = diccionario_ibkr[simbolo]
            diferencia = cantidad_condor - cantidad_ibkr
            if diferencia != 0:
                diccionario_diferencias[simbolo] = {
                    "Qty-condor": cantidad_condor,
                    "Qty-ibkr": cantidad_ibkr,
                    "Qty-diferencias": diferencia
                }
    return diccionario_diferencias

def _extract_values_and_symbols(cell_content):
    if not isinstance(cell_content, str):
        return []
    pattern = r"(\d+\.\d+).*?Stock Symbol (\w+)"
    return re.findall(pattern, cell_content)

def _obtener_valores_nemo(df):
    resultado = {}
    for nemo in df['NEMO'].unique():
        filtro_nemo = df[df['NEMO'] == nemo]
        valor = None
        if 'ADR' in filtro_nemo['Tipo'].values:
            valor = filtro_nemo.loc[filtro_nemo['Tipo'] == 'ADR', 'Qty. CEDEAR/ADR'].iloc[0]
        elif 'CEDEAR' in filtro_nemo['Tipo'].values:
            valor = filtro_nemo.loc[filtro_nemo['Tipo'] == 'CEDEAR', 'Equiv. Acc USA'].iloc[0]
        resultado[nemo] = valor
    return pd.DataFrame(list(resultado.items()), columns=['NEMO', 'Valor'])

def calculate_transactions_convers_diff(transactions_bytes: bytes, convers_bytes: bytes, transactions_filename: str, convers_filename: str):
    excel_file = pd.ExcelFile(BytesIO(transactions_bytes))
    sheet_names_validos = [sheet for sheet in excel_file.sheet_names if sheet in ["Position Transfer IN", "Position Transfer OUT"]]
    
    df_transactions = pd.concat([pd.read_excel(excel_file, sheet_name=sheet) for sheet in sheet_names_validos], ignore_index=True)
    
    df_transactions["Assets"] = df_transactions["Assets"].fillna('')
    df_transactions["Extracted Data"] = df_transactions["Assets"].apply(_extract_values_and_symbols)
    
    expanded_data = df_transactions.explode("Extracted Data").dropna(subset=["Extracted Data"])
    expanded_data[["Value", "Symbol"]] = pd.DataFrame(expanded_data["Extracted Data"].tolist(), index=expanded_data.index)
    
    final_data_transactions = expanded_data[["Symbol", "Value"]]
    final_data_transactions.loc[:, "Value"] = final_data_transactions["Value"].astype(float).astype(int)

    df_convers = pd.read_csv(BytesIO(convers_bytes), sep=None, engine='python')
    resultado_df_convers = _obtener_valores_nemo(df_convers)

    diccionario_transfer = dict(zip(final_data_transactions["Symbol"], final_data_transactions["Value"]))
    diccionario_control = dict(zip(resultado_df_convers["NEMO"], resultado_df_convers["Valor"]))
    
    diccionario_diferencias = {}
    
    all_symbols = set(diccionario_transfer.keys()) | set(diccionario_control.keys())

    for simbolo in all_symbols:
        cantidad_transfer = diccionario_transfer.get(simbolo, 0)
        cantidad_control = diccionario_control.get(simbolo, 0)
        
        # Convertir a float/int para asegurar la resta
        try:
            cantidad_control = float(cantidad_control) if not pd.isna(cantidad_control) else 0
        except (ValueError, TypeError):
            cantidad_control = 0

        diferencia = cantidad_transfer - cantidad_control
        
        if diferencia != 0:
            diccionario_diferencias[simbolo] = {
                "Qty-transfer": cantidad_transfer,
                "Qty-control": cantidad_control,
                "Qty-diferencias": diferencia
            }
            
    return diccionario_diferencias
