import unittest
from src.driver import Driver
from src.similarweb import SimilarWebWebsite

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestDriver(unittest.TestCase):

    def test_open_google(self):
        driver = Driver()
        driver.open_driver()
        driver.open_url('https://www.google.com/')

        input('Press any key to close driver...')

    def test_wait_for_element(self):
        # Defino la URL de prueba
        url = 'https://www.similarweb.com/es/website/youtube.com/#overview'

        # Abro la pagina con el driver
        driver = Driver()
        driver.open_driver()
        driver.open_url(url)

        try:
            # Define un tiempo máximo de espera
            wait = WebDriverWait(driver.driver, 20)

            # Espera hasta que aparezca el elemento con la clase "app-section__content"
            elemento = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'app-section__content'))
                )

            # Una vez que el elemento está presente, obtén el contenido HTML
            contenido_html = elemento.get_attribute('outerHTML')

            # Obtén el contenido HTML de toda la página
            page_content = driver.driver.page_source

            # Guarda el contenido HTML en un archivo
            with open('test.html', 'w', encoding='utf-8') as archivo:
                archivo.write(page_content)

        finally:
            # Cierra el WebDriver
            driver.close_driver()

    def test_wait_for_element_2(self):
        # Defino la URL de prueba
        url = 'https://www.similarweb.com/es/website/youtube.com/#overview'

        # Abro la pagina con el driver
        driver = Driver()
        driver.open_driver()
        driver.open_url(url)

        #
        driver.save_html_after_find()

        # Obtengo la informacion a partir del contenido HTML
        web_info = SimilarWebWebsite(filename='scraped_page.html')
        web_info.fetch_data()

        # Mostrar datos de la pagina
        print('')
        print('-' * 100)
        print(str(web_info))
        print('-' * 100)

if __name__ == '__main__':
    unittest.main()