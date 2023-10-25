import unittest
from src.utils import process_unit_suffix
import re

class TestUtils(unittest.TestCase):

    def test_get_suffix_pattron(self):
        cadena = '{"iconName":"LIKE","title":"104\xa0k","onTap":{"serialCommand":{"commands":[{"logGestureCommand":{"gestureType":"GESTURE_EVENT_TYPE_LOG_GENERIC_CLICK",'

        patron = r'"LIKE","title":"([^"]+)"'

        resultado = re.search(patron, cadena)

        if resultado:
            titulo = resultado.group(1)
            print(titulo)
        else:
            print("No se encontró el patrón en la cadena.")

    def test_process_unit_suffix(self):
        texto1 = '104k'
        resultado1 = process_unit_suffix(texto1)
        print(resultado1)  # Resultado: 104000.0

        texto2 = '104 K'
        resultado2 = process_unit_suffix(texto2)
        print(resultado2)  # Resultado: 104000.0

        texto3 = '2.5m'
        resultado3 = process_unit_suffix(texto3)
        print(resultado3)  # Resultado: 2500000.0

        texto4 = '123 XYZ'
        resultado4 = process_unit_suffix(texto4)
        print(resultado4)  # Resultado: 123.0 (sin sufijo válido)

if __name__ == '__main__':
    unittest.main()