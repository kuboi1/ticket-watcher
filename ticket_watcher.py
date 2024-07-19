import requests
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

URL = 'https://vivenu.com/api/events/info/%s'

BASE_HEADERS = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json',
    'Origin': 'https://emeatickets.lolesports.com',
    'Pragma': 'no-cache',
    'Priority': 'u=1, i',
    'Referer': 'https://emeatickets.lolesports.com/',
    'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Gpc': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

SALE_STATUS_ON_SALE = 'onSale'
SALE_STATUS_SOLD_OUT = 'soldOut'

SALE_STATUSES = {
    SALE_STATUS_ON_SALE: 'on sale',
    SALE_STATUS_SOLD_OUT: 'sold out'
}


def load_config() -> dict:
    if not os.path.exists('./config.json'):
        print('ERROR: Config file does not exist. Create a config.json file based on the config.example.json.')
        exit()

    with open('./config.json') as config_f:
        return json.load(config_f)


def send_on_sale_email(config: dict, event: dict):
    smtp_user = config['smtp']['user']
    smtp_pass = config['smtp']['password']

    subject = f'Event {event["name"]} is available!'
    body = f'Event {event["name"]} is available at {event["link"]}! Be quick!'

    msg = MIMEMultipart()
    msg['From'] = config['from']
    msg['To'] = config['to']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)

        server.sendmail(config['from'], config['to'], msg.as_string())
        
        print(f'Sent a notification email to {config["to"]}')
    except Exception as e:
        print(f'ERROR: Failed to send notification email with error: {e}')
    finally:
        server.quit()


def main(config: dict):
    events = config['events']
    headers = BASE_HEADERS

    # Add the bearer token auth header
    headers['Authorization'] = f'Bearer {config["bearerToken"]}'

    # Check availability for all events
    for event in events:
        print(f'Checking availability of {event["name"]}...')

        url = URL % event['id']

        response = requests.get(
            url=url,
            headers=headers
        )

        if response.status_code == 200:
            event = response.json()
            sale_status = event['saleStatus']

            print(f'Event is {SALE_STATUSES[sale_status]}!')

            # Send email notification if event available
            if sale_status == SALE_STATUS_ON_SALE:
                send_on_sale_email(config['email'], event)
        else:
            print(f'ERROR: There was an error with a request to {url}. Request failed with status {response.status_code}: {response.text}')


if __name__ == '__main__':
    # Load config
    config = load_config()

    # Run the app
    main(config)
