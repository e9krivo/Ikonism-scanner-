import os
import json
import fitz
from tqdm import tqdm

# Параметры конфигурации
pdf_folder = "downloads"
# Порог отсечения общего веса ключевых слов книги (1 для отключения отсечения)
cutoff = 1
# Ключевые слова JSON file
keywords_file = "keywords.json"

# Вывод значения порога отсечения
if cutoff > 0:
	print("Заданный минимальный порог веса ключевых слов для книги:", cutoff)
else:
	print("Минимальный порог веса ключевых слов не задан")

# Загружаем ключевые слова JSON file
print("Загружаем ключевые слова из:", keywords_file)
keywords = json.load(open(keywords_file))

# Вывод статистики по ключевым словам
print("Загружено ключевых слов:", len(keywords))

# Обработка
print("Обрабатываем PDF файлы в папке:", pdf_folder)
# Загрузка всех файлов в папке `pdf_folder`
pdf_files = os.listdir(pdf_folder)
# Результаты
results = []

# По всем файлам в указанной папке
# tqdm wrapper используется для настройки и отображения индикатора прогресса
for filename in tqdm(pdf_files):
	# в качестве меры предосторожности обрабатываются только файлы формата PDF
	if filename.lower().endswith(".pdf"):
		# формирование пути к файлу из имени папки и имени файла (используется для открытия файла PDF)
		file_path = os.path.join(pdf_folder, filename)
		# извлечение текста из PDF с использованием PyMuPDF (fitz)
		text = ""
		with fitz.open(file_path) as pdf:
			for page in pdf:
				text += page.get_text().lower()  # преобразование в нижний регистр для сопоставления без учёта регистра
		# расчёт общей оценки для ключевых слов, найденных в тексте книги
		score = 0
		for keyword, weight in keywords.items():
			if keyword.lower() in text:
				score += text.count(keyword.lower()) * weight
		# cпроверка, не используется ли порог отсечения (1), либо превышает ли оценка файла указанный порог отсечения
		# включение файлов в список результатов только в том случае, если они проходят проверку по порогу отсечения
		if cutoff == 0 or score >= cutoff:
			results.append((filename, score))

# сортирует результаты по оценке в порядке убывания
results.sort(key=lambda x: x[1], reverse=True)

# печать результата
if len(results) == 0:
	print("Книг соотвествующих заданным параметрам не найдено")
else:
	print("Найдено книг соответсвующих заданным параметрам:", len(results))
	print("==============================================================")
	for file, score in results:
		print(f"{file}: [{score}]")
	print("==============================================================")
