import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Параметры конфигурации
url_site = "https://liconism.com"
url_sitemap = "/karta-sajta.html"
book_link_prefix = "/biblioteka-library/"
output_folder = "downloads"

# Извлечение ссылок на страницы книг из карты сайта
# URL всех необходимых ссылок начинаются с /biblioteka-library prefix
print("Соединение с", url_site + url_sitemap)
response = requests.get(url_site + url_sitemap)
response.raise_for_status()

print("Парсинг списка ссылок на книги по префиксу:", book_link_prefix)

soup = BeautifulSoup(response.text, "html.parser")
library_links = [
	a['href']
	for a in soup.find_all('a', href=True)
	if a['href'].startswith(book_link_prefix)
]
print("Найдено совпадающих ссылок:", len(library_links))
library_links_total = len(library_links)

# Обрезка до первых 20 элементов для текпшестов (чтобы избежать скачивания всей библиотеки)
# library_links = library_links[:10]

# Посещение каждой страницы по ссылке из полученных ссылок, одна за одной, и извлечение
# a местонахождение файла книги в формате PDF на странице
pdf_links = []
print("Сканируем", library_links_total, "страниц на наличие сслылок на PDF-файлы")

# Перебор всех ссылок библиотеки
# tqdm wrapper используется для отображения прогресса
for library_link in tqdm(library_links):
	url_bookpage = url_site + library_link
	try:
		res = requests.get(url_bookpage)
		res.raise_for_status()
		page_soup = BeautifulSoup(res.text, "html.parser")
		# Find all <a> tags с href заканчивающихся .pdf
		for a in page_soup.find_all('a', href=True):
			# поиск всех HTML-ссылок, заканчивающихся на ".pdf" (без учета регистра)
			href = a['href']
			if href.lower().endswith('.pdf'):
				full_pdf_url = urljoin(url_bookpage, href)
				pdf_links.append(full_pdf_url)
				# commented out - uncomment for debug
				# print(f"Link: {library_link}")
	except requests.RequestException as e:
		print(f"ОШИБКА обработки {url_bookpage}: {e}")

print("Парсинг библиотеки завершен")
print("Найдено ссылок на PDF-книги:", len(pdf_links))

# Создание папок для загрузок
os.makedirs(output_folder, exist_ok=True)

print("Скачиваем книги в папку:", output_folder)

# Последовательная загрузка всех найденных файлов PDF и сохранение их в локальную папку
# tqdm используется для настройки и отображения полосы прогресса
for pdf_url in tqdm(pdf_links):
	try:
		filename = os.path.basename(urlparse(pdf_url).path)
		filepath = os.path.join(output_folder, filename)
		pdf_response = requests.get(pdf_url)
		pdf_response.raise_for_status()
		with open(filepath, 'wb') as f:
			f.write(pdf_response.content)
		# закомментировано — раскомментируйте для отладки
		# print(f"Downloading: {filename}")
	except requests.RequestException as e:
		print(f"ОШИБКА скачивания {pdf_url}: {e}")

# Печать OK
print("Скачивание завершено")
