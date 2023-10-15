import pandas as pd
import os, sys

# Obtiene el directorio actual donde se encuentra mi_script.py
cur_dir = os.path.dirname(os.path.abspath(__file__))

# Agrega el directorio 'src' al sys.path
directorio_src_1 = os.path.join(cur_dir, "..")
directorio_src_2 = os.path.join(cur_dir, "..", "src")
sys.path.append(directorio_src_1)
sys.path.append(directorio_src_2)

# Importo mi modulo
from db import Database

# Conectarse a la base de datos SQLite
db = Database()

# Nombre de la tabla que deseas exportar
tablename = 'CHANNEL'

# Consulta SQL para seleccionar todos los registros de la tabla
query = f"SELECT * FROM {tablename}"

# Exportar a un archivo CSV
archivo_csv = 'exportacion.csv'
df = pd.read_sql_query(query, db.conn)
df.to_csv(archivo_csv, index=False)  # Exporta a un archivo CSV sin el índice

# Exportar a un archivo Excel (XLSX)
archivo_excel = 'exportacion.xlsx'
df.to_excel(archivo_excel, index=False)  # Exporta a un archivo Excel sin el índice

#
print(df)

# Cerrar la conexión a la base de datos
db.db_close()