import pandas as pd

try:
    from src.db_plots import *
except:
    from db_plots import *

def has_rows_w_nulls(df):
    """
    Funcion para checkear si una tabla tiene filas
     con valores nulos
    """
    rows_w_nulls = df[df.isnull().any(axis=1)]
    if len(rows_w_nulls) > 0:
        return True
    else:
        return False

def fill_null_values(df, sort_columns=[], method='both'):
    """
    Llena los valores nulos en una columna específica de un DataFrame utilizando un método de llenado hacia adelante o hacia atrás dentro de grupos definidos por columnas de orden.

    Parámetros:
    - df (DataFrame): El DataFrame en el que se realizará el llenado de valores nulos.
    - sort_columns (list, opcional): Una lista de nombres de columnas por las cuales se ordenará el DataFrame antes del llenado.
    - method (str, opcional): El método de llenado a utilizar ('bfill', 'ffill' o 'both').

    Retorna:
    - df (DataFrame): El DataFrame modificado con los valores nulos llenados.

    Ejemplo:
    fill_null_values(df, 'Valor', ['ID', 'Fecha'], method='bfill')
    """
    # Agregar una columna 'INDEX' para mantener los números de fila originales
    df['INDEX'] = df.index

    if sort_columns:
        # Convertir las columnas de orden a tipo datetime si son fechas
        for col in sort_columns:
            if col in df.columns and df[col].dtype == 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])

        # Ordenar el DataFrame por las columnas de orden
        df = df.sort_values(sort_columns)

    # Llenado hacia adelante o hacia atrás dentro de grupos
    if method == 'bfill':
        df.fillna(method=method, inplace=True)
    elif method == 'ffill':
        df.fillna(method=method, inplace=True)
    elif method == 'both':
        df.fillna(method='bfill', inplace=True)
        df.fillna(method='ffill', inplace=True)
    else:
        raise ValueError("El método debe ser 'bfill' o 'ffill'.")

    # Ordenar el DataFrame por la columna 'INDEX'
    df = df.sort_values('INDEX')

    # Eliminar la columna 'INDEX' si se desea
    df.drop('INDEX', axis=1, inplace=True)

    return df

def replace_zeros_with_nearest_valid(df, sort_columns, valid_columns, method=2, debug=False):
    """
    Reemplaza los ceros en un DataFrame por el valor válido más cercano en la misma fila.

    Parámetros:
    - df (DataFrame): El DataFrame en el que se realizarán los reemplazos.
    - sort_columns (list): Una lista de nombres de columnas por las cuales se ordenará el DataFrame.
    - valid_columns (list): Una lista de nombres de columnas que se utilizarán para buscar el valor válido más cercano.

    Retorna:
    - df (DataFrame): El DataFrame modificado con los ceros reemplazados.
    """
    # Agregar una columna 'INDEX' para mantener los números de fila originales
    df['INDEX'] = df.index

    if sort_columns:
        # Convertir las columnas de orden a tipo datetime si son fechas
        for col in sort_columns:
            if col in df.columns and df[col].dtype == 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])

        # Ordenar el DataFrame por las columnas de orden
        # Reinicio los indices porque sino no funciona
        # la utilidad esta
        df = df.sort_values(sort_columns).reset_index()

    # Debug
    if debug is True:
        print(df.head())

    for col in valid_columns:

        # Encuentra la posición de las filas que tienen un valor de 0.0
        zero_indices = df.index[df[col] == 0.0]

        # Metodo 1: Me limito a buscar en los elementos adyacentes
        if method == 1:

            # Itera sobre estas filas y reemplaza el valor de 0.0 por el valor adyacente
            for idx in zero_indices:

                # Debug
                if debug is True:
                    print('{}. {} = {}'.format(idx-1, col, df[col][idx-1]))
                    print('{}. {} = {}'.format(idx,   col, df[col][idx  ]))
                    print('{}. {} = {}'.format(idx+1, col, df[col][idx+1]))

                # Me aseguro que el elemento a reemplazar no sea el primero
                if idx > 0:
                    # Si el valor anterior no es cero, reemplaza por el valor anterior
                    if df.at[idx - 1, col] != 0.0:
                        df.at[idx, col] = df.at[idx - 1, col]
                    # Otra forma que da igual
                    #if df[col][idx-1] != 0.0:
                    #    df[col][idx] = df[col][idx-1]

                # Me aseguro que el elemento a reemplazar no sea el ultimo que tengo
                elif idx < len(df) - 1:
                    # Si el valor siguiente no es cero, reemplaza por el valor siguiente
                    if df.at[idx + 1, col] != 0.0:
                        df.at[idx, col] = df.at[idx + 1, col]
                    # Otra forma que da igual
                    #if df[col][idx+1] != 0.0:
                    #    df[col][idx] = df[col][idx+1]

        # Metodo 2: Busco alrrededor hasta encontrar un elemento no 0
        if method == 2:

            # Itera sobre estas filas y reemplaza el valor de 0.0 por el valor adyacente
            for idx in zero_indices:

                # Debug
                if debug:
                    print('{}. {} = {}'.format(idx-1, col, df[col][idx-1]))
                    print('{}. {} = {}'.format(idx,   col, df[col][idx  ]))
                    print('{}. {} = {}'.format(idx+1, col, df[col][idx+1]))

                # Inicialmente, asumimos que no hay valores válidos adyacentes
                left_idx = None
                right_idx = None

                # Buscamos el valor válido más cercano a la izquierda
                # Supongamos que que estamos en el inidice 50, vamos
                # a buscar en los indices 49, 48, 47, ..., 0
                for i in range(idx - 1, -1, -1):
                    if df.at[i, col] != 0.0:
                        left_idx = i
                        break

                # Buscamos el valor válido más cercano a la derecha
                # Supongamos que que estamos en el inidice 50, vamos
                # a buscar en los indices 51, 51, 53, ..., N-1
                # Donde N es la longitud del DF
                for i in range(idx + 1, len(df)):
                    if df.at[i, col] != 0.0:
                        right_idx = i
                        break

                # Si encontramos valores válidos a ambos lados, tomamos el más cercano
                if left_idx is not None and right_idx is not None:
                    if abs(left_idx - idx) <= abs(right_idx - idx):
                        df.at[idx, col] = df.at[left_idx, col]
                    else:
                        df.at[idx, col] = df.at[right_idx, col]
                elif left_idx is not None:
                    df.at[idx, col] = df.at[left_idx, col]
                elif right_idx is not None:
                    df.at[idx, col] = df.at[right_idx, col]

    # Ordenar el DataFrame por la columna 'INDEX'
    df = df.sort_values('INDEX').reset_index()

    # Eliminar la columna 'INDEX' si se desea
    df.drop('INDEX', axis=1, inplace=True)

    return df

def clean_channel_tables(filename_1, filename_2, save_clean=True):
    # Cargo los CSV
    df_1 = pd.read_csv(filename_1)
    df_2 = pd.read_csv(filename_2)

    # Convertir la columna 'UPDATE_DATE' a objetos de fecha
    # A df_2 en este caso no le hace falta un procesamiento particular
    df_1['UPDATE_DATE'] = pd.to_datetime(df_1['UPDATE_DATE'])

    # Si la tabla tiene campos nulos los limpio
    sort_columns = ['CHANNEL_ID','UPDATE_DATE']
    if has_rows_w_nulls(df=df_1) is True:
        df_1 = fill_null_values(df=df_1, sort_columns=sort_columns)

    # Relleno los posibles valores que sean 0
    # A df_2 en este caso no le hace falta un procesamiento particular
    sort_columns = ['CHANNEL_ID','UPDATE_DATE']
    valid_columns = ['SUBSCRIBERS', 'DAILY_SUBS','MONTHLY_SUBS','TOTAL_VIEWS','VIDEOS_COUNT']
    df_1 = replace_zeros_with_nearest_valid(df=df_1, sort_columns=sort_columns, valid_columns=valid_columns)

    # Guardo los CSV procesados
    if save_clean == True:
        df_1.to_csv( filename_1.replace('.csv','_clean.csv') )
        df_2.to_csv( filename_2.replace('.csv','_clean.csv') )

    return df_1, df_2

if __name__ == '__main__':

    # Defino el path de resultados
    CSV_PATH = r'results/db/'

    # Defino el nombre del archivo
    FILENAME_1 = r'channel_records.csv'
    FILENAME_2 = r'channel.csv'

    # Obtengo los CSV limpios
    df_1, df_2 = clean_channel_tables(
        filename_1 = CSV_PATH + FILENAME_1,
        filename_2 = CSV_PATH + FILENAME_2
    )

    # Hago los plots de las tablas de canal
    plot_channel_tables(df_1, df_2)