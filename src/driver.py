from selenium import webdriver
import time

DRIVER_PATH = r'drivers/'

class Driver:
    def __init__(self, browser="chrome"):
        """
        Inicializa el objeto Driver con el navegador especificado (por defecto, Chrome).

        Args:
            browser (str): El navegador a utilizar: 'chrome', 'firefox', o 'edge'.
        """
        if browser == "chrome":
            self.driver = webdriver.Chrome(DRIVER_PATH + '\chromedriver.exe')
        elif browser == "firefox":
            self.driver = webdriver.Firefox(DRIVER_PATH + '\chromedriver.exe')
        elif browser == "edge":
            self.driver = webdriver.Edge(DRIVER_PATH + '\chromedriver.exe')
        else:
            raise ValueError("Navegador no válido. Debe ser 'chrome', 'firefox' o 'edge.")

        # Atributos
        self.html_content = ''

    def open_url(self, url):
        """
        Carga una página web, espera un tiempo y guarda el HTML en un archivo.

        Args:
            url (str): La URL de la página web a cargar.
        """
        self.driver.get(url)

    def update_html_content(self):
        self.html_content = self.driver.page_source

    def close(self):
        """
        Cierra el navegador y finaliza la instancia del objeto Driver.
        """
        self.driver.quit()

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

        # Guardo el contenido HTML
        with open(filename, "w", encoding="utf-8") as file:
            file.write(self.driver.page_source)

# Ejemplo de uso
if __name__ == "__main__":
    driver = Driver(browser="chrome")
    # driver.open_url("https://www.ejemplo.com")
    driver.open_url("https://www.similarweb.com/top-websites/")

    # Actualizo el contenido HTML del objeto
    # y guardo la pagina
    driver.save_html_after_delay(delay=20)

    # Muestro el contenido HTML
    # print(driver.html_content)

    # Cierro la pagina
    driver.close()