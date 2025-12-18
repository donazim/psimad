import requests
from  bs4 import BeautifulSoup

url = "https://stepik.org/catalog"
response = requests.get(url)

'''
if response.status_code == 200:
    print("Код 200")
    soup = BeautifulSoup(response.text, "html.parser")
    course_cards = soup.find_all("li", class_="course-cards__item")
    for card in course_cards:
        name = card.find("a", class_="course-card__title")
        if name:
            name_text = name.text.strip()
            print(name_text, '\n')
            
else:
    print("Ошибка! Код ответа:", response.status_code)
'''

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    course_lists = soup.find_all("section", class_="catalog-block-full-course-lists__tabpanel")

    for course_list in course_lists:
        course_list_title = course_list.find("h1").text.strip()
        
        print("="*20)
        print(course_list_title)
        print("="*20)

        #if course_list_title in ("В тренде", "Новые курсы"):

        if course_list_title == "В тренде":
            print(course_list)
            course_cards = course_list.find_all("li", class_="course-cards__item")
            for card in course_cards:
                name = card.find("a", class_="course-card__title")
                if name:
                    name_text = name.text.strip()
                    print(name_text, '\n')
    



else:
    print("Ошибка! Код ответа:", response.status_code)

