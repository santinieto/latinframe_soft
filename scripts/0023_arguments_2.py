import argparse

# Paso 1: Crear un objeto ArgumentParser
parser = argparse.ArgumentParser(description="Mi programa de línea de comandos")

"""
name o flags: Estos parámetros definen cómo se debe reconocer el argumento en la línea de comandos
name es un enfoque más explícito, mientras que flags es una lista de cadenas que representan diferentes
formas de especificar el argumento (por ejemplo, '-f' y '--file').
"""
parser.add_argument('-f', '--file', help="Nombre del archivo")

"""
action: Este parámetro define qué debe hacer argparse cuando se encuentra el argumento. Algunas de las opciones comunes son:
'store': Almacena el valor del argumento para su posterior uso.
'store_true' y 'store_false': Almacenan True o False para indicar la presencia o ausencia del argumento.
'append': Almacena varios valores para el mismo argumento en una lista.
'count': Cuenta el número de veces que aparece un argumento.
"""
parser.add_argument('-v', '--verbose', action='store_true', help="Modo verbose")

"""
type: Define el tipo de dato esperado para el argumento. argparse convertirá automáticamente el valor del argumento
en el tipo especificado. Por ejemplo, puedes usar int, float, str, etc.
"""
parser.add_argument('-n', '--number', type=int, help="Número entero")

"""
default: Especifica el valor predeterminado del argumento si no se proporciona en la línea de comandos.
"""
parser.add_argument('-o', '--output', default='output.txt', help="Nombre del archivo de salida")

"""
required: Un argumento booleano que indica si el argumento es obligatorio o no.
"""
parser.add_argument('-i', '--input', required=True, help="Nombre del archivo de entrada (obligatorio)")

"""
choices: Define una lista de valores válidos para el argumento. argparse generará un error si el valor
proporcionado no está en la lista.
"""
parser.add_argument('--color', choices=['red', 'green', 'blue'], help="Color válido")

"""
help: Proporciona una descripción textual del argumento que se mostrará en la ayuda del programa cuando
se ejecute con la opción --help.
"""
parser.add_argument('-f', '--file', help="Nombre del archivo de entrada")

"""
metavar: Define el nombre del argumento que se muestra en la ayuda del programa. Es útil para personalizar
la apariencia de la ayuda sin afectar el código del programa.
"""
parser.add_argument('-f', '--file', metavar='archivo', help="Nombre del archivo de entrada")
