import os
from time import timezone
from dotenv import load_dotenv
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, tzinfo
import matplotlib.pyplot as plt
from collections import Counter

load_dotenv()


# Данные для gmail
GMAIL_SERVER = "imap.gmail.com"
GMAIL_LOGIN = os.getenv("GMAIL_LOGIN")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

from datetime import datetime, timedelta

today = datetime.now()
one_month_ago = today - timedelta(days=31)

# Функция для gmail
def gmail_spam_parse(login, password):
    date_list = []
    week_list = []
    mail = imaplib.IMAP4_SSL(GMAIL_SERVER)
    mail.login(login, password)

    status, mailboxes = mail.list()
    # for m in mailboxes:
    #     print(m)

    for m in mailboxes:
        if b'\\Junk' in m:
            spam_folder = m.decode().split(' "/" ')[1]
            break

    spam_folder = spam_folder.strip('"')

    status, _ = mail.select(f'"{spam_folder}"')
    if status != "OK":
        raise Exception("Не удалось выбрать папку спама")


    # Получаем все письма из папки
    status, response = mail.search(None, 'ALL')
    if status == 'OK':
        email_ids = response[0].split()  # Список ID всех писем
        print(f"Темы писем из папки spam':")
        
        for email_id in email_ids:
            # Получаем сообщение по ID
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            if status == 'OK':
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg.get("Subject"))[0]
                        # Если тема закодирована в base64 или другой кодировке
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or 'utf-8')
                        date_str = msg.get("Date")
                        if date_str:
                            try:
                                date_obj = parsedate_to_datetime(date_str)
                            except Exception:
                                date_obj = None
                        if date_obj == None:
                            try:
                                date_obj = datetime.strptime(date_str, "%m-%d-%Y")
                            except ValueError:
                                date_obj = parsedate_to_datetime(date_str)
                        
                        year, week, day = date_obj.isocalendar()
                        
                        if date_obj is not None:
                            date_obj = date_obj.replace(tzinfo=None)

                        if date_obj >= one_month_ago:
                            week_list.append(week)
                            date_list.append(date_obj)

                        sender = msg.get("From")

                        print(f"Тема: {subject}\nОт: {sender}\nДата: {date_obj}")
                        with open("log.txt", "a") as f:
                            f.write(f"Тема: {subject}\nОт: {sender}\nДата: {date_obj}\n\n")

    days = [d.date() for d in date_list if d is not None]
    day_counts = Counter(days)


    dates = list(day_counts.keys())
    counts = list(day_counts.values())

    plt.figure(figsize=(12,6))
    plt.bar(dates, counts)
    plt.xticks(rotation=45)
    plt.xlabel("Дата")
    plt.ylabel("Количество писем")
    plt.title("СПАМ письма за последний месяц")
    plt.tight_layout()
    plt.savefig("spam_by_day.png")
    plt.show()

    week_counts = Counter(week_list)

    labels = list(week_counts.keys())
    values = list(week_counts.values())

    plt.figure(figsize=(10,6))
    plt.bar(labels, values)
    plt.xlabel("Неделя")
    plt.ylabel("Количество писем")
    plt.title("СПАМ письма по неделям за последний месяц")
    plt.tight_layout()
    plt.savefig("spam_by_week.png")
    plt.show()


gmail_spam_parse(GMAIL_LOGIN, GMAIL_PASSWORD)