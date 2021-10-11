#!/usr/bin/python

# Author: J. Igor Melo (@jigordev)
# Usage: ./gdmaker.py 'intext:"Example"' -c 13 -a 'Your name' -d 'Description' -f example.txt

import os
import smtplib
import getpass
import argparse
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

try:
	from dotenv import load_dotenv
	load_dotenv()
except:
	pass

AUTHOR = os.environ.get("AUTHOR")
EMAIL = os.environ.get("EMAIL")
SERVER = os.environ.get("SERVER")
PORT = os.environ.get("PORT")

GHDB_EMAIL = "dorks@offensive-security.com"

CATEGORIES = {
	"1": "Footholds",
	"2": "Files Containing Usernames",
	"3": "Sensitive Directories",
	"4": "Web Server Detection",
	"5": "Vulnerable Files",
	"6": "Vulnerable Servers",
	"7": "Error Messages",
	"8": "Files Containing Juicy Info",
	"9": "Files Containing Password",
	"10": "Sensitive Online Shopping Info",
	"11": "Network or Vulnerability Data",
	"12": "Pages Containing Login Portals",
	"13": "Various Online Devices",
	"14": "Advisories and Vulnerabilities",
}

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("dork", help="Content of your google dork")
	parser.add_argument("-c", "--category", nargs="?", choices=CATEGORIES.keys(), help="Category numeric code")
	parser.add_argument("-a", "--author", default=AUTHOR, help="Author's name or nickname")
	parser.add_argument("-f", "--filename", help="File where the dork content will be saved")
	parser.add_argument("-d", "--description", help="Optional description for dork")
	parser.add_argument("-e", "--email", default=EMAIL, help="Your email address")
	parser.add_argument("-s", "--server", default=SERVER, help="SMTP server address")
	parser.add_argument("-p", "--port", default=PORT, type=int, help="SMTP server port")
	parser.add_argument("--list-cat", action="store_true", help="List all dork categories")
	parser.add_argument("--not-send", action="store_true", help="Cancel sending the email")
	parser.add_argument("--exclude-file", help="Delete dork file after upload")
	args = parser.parse_args()

	if args.list_cat:
		print_categories()

	dork = args.dork
	category = args.categoty if args.category else input("Category number: ")
	author = args.author if args.author else input("Author name: ")
	description = args.description if args.description else input("Description: ")
	filename = args.filename if args.filename else input("Dork file: ")

	create_dork_file(dork, category, author, description, filename)

	opt = not args.not_send if args.not_send else input("Send dork to GHDB? [yes/no]: ")
	if opt and opt.lower() == "yes" or opt.lower() == "y":
		email = args.email if args.email else input("Enter your email: ")
		server = args.server if args.server else input("Enter SMTP server: ")
		port = args.port if args.port else 587
		password = getpass.getpass("Enter your password: ")
		send_dork_email(dork, email, password, server, port, filename)

		if args.exclude_file:
			os.remove(filename)

def print_success(text):
	print(f"\n[+] {text}")

def print_failure(text):
	print(f"\n[-] {text}")

def print_categories():
	print("Dork Categories:\n")
	for idx, cat in CATEGORIES.items():
		print(f"{idx}: {cat}")
	print("")

def get_date():
	today = datetime.date.today()
	return today.strftime("%d/%m/%y")

def create_dork_file(dork, category, author, description, filename):
	with open(filename, "w") as dork_file:
		data = f"# Google Dork: {dork}\n"
		data += f"# {CATEGORIES[category]}\n"
		data += f"# Date: {get_date()}\n"
		data += f"# Exploit Author: {author}"
		data += f"\n\n{description}" if description else ""
		dork_file.write(data)

		print(f"\n{data}")
		print_success("Dork file successfully created\n")

def send_dork_email(dork, email, password, server, port, filename):
	with open(filename, "r") as dork_file:
		message = MIMEMultipart()
		message["From"] = email
		message["To"] = GHDB_EMAIL
		message["subject"] = dork

		dork_filename = os.path.basename(filename)
		part = MIMEApplication(dork_file.read(), Name=dork_filename)
		part["Content-Disposition"] = f"attachment; filename={dork_filename}"
		message.attach(part)
		
		session = smtplib.SMTP(server, port)
		session.starttls()
		session.login(email, password)
		session.sendmail(email, GHDB_EMAIL, message.as_string())
		session.quit()
		print_success("Email sended successfully")

if __name__ == "__main__":
	main()
