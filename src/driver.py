from selenium import webdriver
import time

class Driver:
    def __init__(self, browser="chrome", driver_path=r'drivers/',results_path='results/similarweb/'):
        """
        Inicializa el objeto Driver con el navegador especificado (por defecto, Chrome).

        Args:
            browser (str): El navegador a utilizar: 'chrome', 'firefox', o 'edge'.
        """

        # Atributos
        self.driver_path = driver_path
        self.results_path = results_path
        self.browser = browser
        self.html_content = ''

    def __del__(self):
        """
        Destructor para cerrar el navegador cuando se libera la instancia de la clase.
        """
        self.close_driver()

    def open_driver(self):
        """
        """
        try:
            if self.browser == "chrome":
                # Deshabilito la lectura de puertos USB
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--disable-usb-device-detection")
                chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # Este es el que funciona
                # Abro el driver
                self.driver = webdriver.Chrome(
                    self.driver_path + '\chromedriver.exe',
                    options = chrome_options
                    )
            elif self.browser == "firefox":
                self.driver = webdriver.Firefox(self.driver_path + '\chromedriver.exe')
            elif self.browser == "edge":
                self.driver = webdriver.Edge(self.driver_path + '\chromedriver.exe')
            else:
                raise ValueError("Navegador no válido. Debe ser 'chrome', 'firefox' o 'edge.")
        except Exception as e:
            print(f"Error al abrir el navegador: {e}")

    def close_driver(self):
        """
        Cierra el navegador y finaliza la instancia del objeto Driver.
        """
        self.driver.quit()

    def open_url(self, url):
        """
        Carga una página web, espera un tiempo y guarda el HTML en un archivo.

        Args:
            url (str): La URL de la página web a cargar.
        """
        try:
            self.driver.get(url)
        except Exception as e:
            print(f"Error al cargar la URL: {e}")

    def update_html_content(self):
        self.html_content = self.driver.page_source

    def save_html_after_delay(self, delay=5, filename="scraped_page.html"):
        """
        Carga una página web, espera un tiempo y guarda el HTML en un archivo.

        Args:
            delay (int): El tiempo de espera en segundos antes de guardar el HTML (por defecto, 5 segundos).
            filename (str): El nombre del archivo en el que se guardará el HTML (por defecto, "scraped_page.html").
        """
        # Seteo el delay
        self.update_html_content()

        # Actualizo el contenido HTML
        time.sleep(delay)  # Espera el tiempo especificado

        try:
            # Guardo el contenido HTML
            with open(f'{self.results_path}/{filename}', "w", encoding="utf-8") as file:
                file.write(self.driver.page_source)
        except Exception as e:
            print(f"Error al intentar guardar contenido HTML en el archivo {filename}")
            print(f"Codigo de error: {e}")

    def scrap_url(self, url, alias, delay=20):

        # Abro un driver
        self.open_driver()

        # Obtengo la pagina objetivo
        self.open_url(url)

        # Creo el nombre del archivo
        filename = f'html_{alias}.dat'

        # Actualizo el contenido HTML del objeto
        # y guardo la pagina
        self.save_html_after_delay(delay=delay, filename=filename)

        # Cierro el navegador para liberar recursos
        self.close_driver()

        return filename

    def scrap_url_list(self, input_list, delay=20):
        """
        Args:
            list of url to scrap. Format --> (url, alias)
        """

        for input_element in input_list:
            url = input_element[0]
            alias = input_element[1]

            self.scrap_url(url, alias, delay=delay)

# Ejemplo de uso
if __name__ == "__main__":
    # Creo el objeto de tipo driver
    driver = Driver(browser="chrome")

    # Armo una lista de webs a visitar
    url_list =[
        ('https://www.similarweb.com/website/youtube.com/', 'youtube'),
        ('https://www.similarweb.com/website/google.com/', 'google'),
    ]

    # Otros ejemplos
    # driver.open_url("https://www.ejemplo.com")
    # driver.open_url("https://www.similarweb.com/top-websites/")

    # Obtengo el codigo HTML para esas paginas
    driver.scrap_url_list(url_list, 20)

    # Cierro la pagina
    driver.close_driver()
