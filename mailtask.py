import os
from dotenv import load_dotenv
import imaplib

load_dotenv()

EMAIL = os.getenv("EMAIL_LOGIN")
PASSWORD = os.getenv("EMAIL_PASSWORD")

imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(EMAIL, PASSWORD)
