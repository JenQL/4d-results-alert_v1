#!/usr/bin/env python
# coding: utf-8

#final
import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import datetime

# Get today’s date in YYYY-MM-DD format
today = datetime.date.today().strftime("%Y-%m-%d")
target_numbers = ["1814", "4272", "8292", "3603","6232"]

names = ['Magnum', 'DaMaCai']
urls = [f"https://www.4dpredict.app/magnum4d/?d={today}", f"https://www.4dpredict.app/damacai4d/?d={today}"]
body_dict = {}

for url, name in zip(urls,names):
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")


    # Find prize rows safely
    prize_rows = soup.find_all("tr", class_="is-size-2 has-text-weight-bold")

    if not prize_rows:
        print(f"No results available for {today}. Skipping alert.")
        exit()  # Stop script if no results
    else:
        prizes = prize_rows[0].find_all("td")
        first, second, third = [td.text.strip() for td in prizes]


    def extract_section(soup, header_text):
        section = []
        # Find header cell by checking text content (strip whitespace, uppercase)
        header = soup.find("td", class_="titlebet mu",
                           string=lambda t: t and t.strip().upper().startswith(header_text.upper()))


        if header:
            # Walk through sibling rows after the header row
            for row in header.find_parent("tr").find_next_siblings():
                # Stop when another header row appears
                if row.find("td", class_="titlebet mu"):
                    break
                # Collect only valid 4-digit numbers
                for td in row.find_all("td"):
                    val = td.text.strip()
                    if val.isdigit() and len(val) == 4:
                        section.append(val)
        return section

    special_prizes = extract_section(soup, "SPECIAL")
    consolation_prizes = extract_section(soup, "CONSOLATION")

    if special_prizes==[]:
        special_prizes = extract_section(soup, "STARTER")


    
    #Monitor numbers
    results = [first, second, third] + special_prizes + consolation_prizes   # add special/consolation if needed

    matched = [num for num in results if num in target_numbers]

    if matched:
        alert_message = f"Your numbers appeared: {', '.join(matched)}"
    else:
        alert_message = "No target numbers appeared today."
#         exit()  # Stop script if no hit



    
    
    
    email_body = f"""
    4D Results Alert - {url}

    {name} 1st: {first}
    {name} 2nd: {second}
    {name} 3rd: {third}

    {alert_message}
    """
    
    
    # store into dictionary
    body_dict[name] = {
        f"4D Results Alert - {name}": url,
        "first": first,
        "second": second,
        "third": third,
        "special": special_prizes,
        "consolation": consolation_prizes,
        "alert": alert_message
    }

def send_email(subject, body, to_email):

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = to_email

    # Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_USER_PASS"])  # use App Password
        server.send_message(msg)       
        
# Example: compile results before sending
def compile_results(magnum, damacai):
    body = []
    body.append("🎲 Daily 4D Results\n")

    # Magnum
    body.append("Magnum:")
    body.append(f"1st: {magnum['first']}, 2nd: {magnum['second']}, 3rd: {magnum['third']}")
    body.append(f"Special: {', '.join(magnum['special'])}")
    body.append(f"Consolation: {', '.join(magnum['consolation'])}")
    body.append(f"**Alert**: {magnum['alert']}")


    # Damacai
    body.append("Damacai:")
    body.append(f"1st: {damacai['first']}, 2nd: {damacai['second']}, 3rd: {damacai['third']}")
    body.append(f"Special: {', '.join(damacai['special'])}")
    body.append(f"Consolation: {', '.join(damacai['consolation'])}")
    body.append(f"**Alert**: {damacai['alert']}")

    return "\n".join(body)

# Usage
email_body = compile_results(body_dict['Magnum'], body_dict['DaMaCai'])
send_email(f"4D Results Alert {today}", email_body, os.environ["EMAIL_RECIPIENT"])

print("done!")

