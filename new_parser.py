from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

trending_courses = []
new_courses = []

def get_text(by, selector):
    '''
    Из элемента в обычный текст чтобы каждый раз не делать текстстрип а еще он пишет какой элемент по классу не получилось достать
    '''
    try:
        return card.find_element(by, selector).text.strip()
    except Exception as e:
        print(f"Не удалось получить текст из эелемента {selector}")
        return None

def get_price():
    '''
    Доставание цены если есть вообще или если скидка есть то цену со скидкой а если нет то бесплатно
    '''
    discount_price = get_text(By.CSS_SELECTOR, ".display-price__price_discount")
    regular_price = get_text(By.CSS_SELECTOR, ".display-price__price_regular")
    if discount_price:
        return discount_price
    elif regular_price:
        return regular_price
    else:
        return "бесплатно"

def parse_card():
    '''
    Парсинг одной карточки в словарь
    '''
    course = {
        "title": get_text(By.CSS_SELECTOR, "a.course-card__title"),
        "author": get_text(By.CSS_SELECTOR, "a.course-card__author"),
        "rating": get_text(By.CSS_SELECTOR, 'span[data-type="rating"] span:last-child'),
        "learners": get_text(By.CSS_SELECTOR, 'span[data-type="learners"] span:last-child'),
        "workload": get_text(By.CSS_SELECTOR, 'span[data-type="workload"] span:last-child'),
        "has_certificate": bool(
            card.find_elements(By.CSS_SELECTOR, 'span[data-type="certificate"]')
        ),
        "price": get_price()
    }
    return course

def print_course(course):
    '''
    Вывод карточки курса в консоль
    '''
    print("="*30)
    print(f"Название: {course["title"]}")
    print(f"Автор: {course["author"]}")
    print(f"Рейтинг: {course["rating"]}")
    print(f"Количество студентов: {course["learners"]}")
    print(f"Время прохождения: {course["workload"]}")
    print("Есть сертификат") if course["has_certificate"] else print("Нет сертификата")
    print(f"Цена: {course["price"]}")
    print("="*30)



# Настройки для headless режима
options = Options()
options.add_argument("--headless")

# Инициализация драйвера Chrome
service = ChromeService()
driver = webdriver.Chrome(service=service, options=options)

# URL целевой страницы
url = "https://stepik.org/catalog"

# Пдключаемся к степику
try:
    driver.get(url)
    driver.set_window_size(1480, 1000)
    # Ждем загрузки карточек
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "course-cards__item")))
    time.sleep(2)
except Exception as e:
    print(f'Не удалось подключиться к сайту: {e}')

# Берем первые шесть карточек
try:
    cards = driver.find_elements(By.CLASS_NAME, "course-cards__item")
    print(f"Всего найдено карточек {len(cards)}")
    print("-"*40)

    for i in range(6):
        card = cards[i]
        trending_courses.append(parse_card())
except Exception as e:
    print(f"Не обнаружено карточек: {e}")

# Нажимаем стрелочку
try:
    btn = driver.find_element(By.XPATH, '/html/body/main/div/div[3]/div/div/section[1]/div/div/button[2]')
    btn.click()
    time.sleep(10)
except Exception as e:
    print(f"Не удалось найти или кликнуть кнопку: {e}")

# Берем остальные карточки я тут полностью все скопировал из первых шести 
# но наверное cards можно не доставать еще раз...
try:
    cards = driver.find_elements(By.CLASS_NAME, "course-cards__item")
    for i in range(5):
        card = cards[i + 6]
        trending_courses.append(parse_card())
except Exception as e:
    print(f"Не обнаружено карточек: {e}")

# Смотрим что все досталось
for i in trending_courses:
    print_course(i)

# Переходим на новые курсы
try:
    btn = driver.find_element(By.XPATH, '/html/body/main/div/div[3]/div/div/ul/li[2]/button')
    btn.click()
    time.sleep(10)
except Exception as e:
    print(f"Не удалось найти или кликнуть кнопку: {e}")

driver.save_screenshot("new_courses.png")

print("="*50)
print("Перешли в новые курсы")
print("="*50)

# Берем первые шесть карточек из новых курсов то есть 12ю карточку из всех
try:
    cards = driver.find_elements(By.CLASS_NAME, "course-cards__item")
    for i in range(6):
        card = cards[i+12]
        new_courses.append(parse_card())
except Exception as e:
    print(f"Не обнаружено карточек: {e}")

# Нажимаем стрелочку в новых курсах
try:
    btn = driver.find_element(By.XPATH, '/html/body/main/div/div[3]/div/div/section[2]/div/div/button[2]')
    btn.click()
    time.sleep(10)
except Exception as e:
    print(f"Не удалось найти или кликнуть кнопку: {e}")

# Забираем остальные  карточки из новых курсов
try:
    cards = driver.find_elements(By.CLASS_NAME, "course-cards__item")
    for i in range(5):
        card = cards[i+18]
        new_courses.append(parse_card())
except Exception as e:
    print(f"Не обнаружено карточек: {e}")

for i in new_courses:
    print_course(i)

