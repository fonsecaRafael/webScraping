# from scrapy import Spider
import scrapy
from selenium import webdriver
# from scrapy.http import HtmlResponse

class CpsoDoctorsSpider(scrapy.Spider):
    name = "cpso_doctors"
    start_urls = ["https://register.cpso.on.ca/Advanced-Search"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def parse(self, response):
        self.driver.get(response.url)
        # Fill the form using Selenium
        self.driver.find_element_by_name('City').send_keys('Toronto')
        self.driver.find_element_by_name('HospitalLocation').send_keys('Ajax')
        self.driver.find_element_by_name('btnSearch').click()

        # Waiting for results
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.doctor-info'))
        )

        # Send HTML to Scrapy
        html = self.driver.page_source
        yield HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')
        

    def parse_results(self, response):
        # Aqui você processa os resultados da busca
        for doctor in response.css('div.doctor-info'):  # Ajuste o seletor conforme o HTML da página
            yield {
                'name': doctor.css('h2.name::text').get(),
                'specialization': doctor.css('p.specialization::text').get(),
                'address': doctor.css('p.address::text').get(),
            }

        # Paginação (se houver)
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_results)
