# Abre el archivo en modo lectura (por defecto)
filename = "scripts/0015_query_1.sql"

try:
    with open(filename, "r") as archivo:
        query = archivo.read()  # Lee todo el contenido del archivo y lo almacena en la cadena 'contenido'

    # Ahora 'contenido' contiene el contenido del archivo como una cadena
    print(query)

except FileNotFoundError:
    print(f"El archivo '{filename}' no fue encontrado.")
except Exception as e:
    print(f"Ocurrió un error: {e}")
