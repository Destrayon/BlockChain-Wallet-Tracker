import requests
import time
import datetime
import smtplib
import os


# This will go through the most recent transaction to the initial transaction, and will return the amount of
# new transactions as an int. Ex: If there are 3 new transactions found in the wallet, this will return 3.
def find_transaction_amount(json):
    num = 0
    for txid in json['transactions']:
        if txid['txid'] != initial_transaction:
            num = num + 1
        else:
            return num


# This will parse the provided dictionary for amount and propertyname, returning a string of readable words for
# the email. Ex: The dictionary transaction has a key amount with a value of 10000.00 and a key propertyname
# with the value TetherUS, this will return:
# "(the date and time now) - A new transaction was found:
# 10000.00, paid with TetherUs."
def formatter(transaction):
    amount = transaction['amount']
    type = transaction['propertyname']
    return f'{datetime.datetime.now()} - A new transaction was found:\n{amount}, paid with {type}.\n\n'


def email(str):
    email = os.environ.get("TEST_EMAIL")
    password = os.environ.get("TEST_PASS")
    email_message = f"Subject: New BlockChain Alert!\n\n{str}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(email, password)
        server.sendmail(email, email, email_message)


def initial_requesting():
    try:
        return requests.post('https://api.omniexplorer.info/v1/address/addr/details/', headers=headers, data=data).json()['transactions'][0]
    except:
        print("Error, trying again.")

        return initial_requesting()


headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'addr': '1Po1oWkD2LmodfkBYiAktwh76vkF93LKnh'
}

accepted_currencies = {
    "TetherUS",
    "MaidSafeCoin",
    "Omni Token"
}

initial_request = initial_requesting()

initial_transaction = initial_request['txid']

print("Running")

time.sleep(20)

while True:
    response = requests.post('https://api.omniexplorer.info/v1/address/addr/details/', headers=headers, data=data)
    try:
        response_json = response.json()
        transaction = response_json['transactions'][0]
        transaction_txid = transaction['txid']
        if transaction_txid != initial_transaction:
            num = find_transaction_amount(response_json)
            str = ''
            for index in range(0, num):
                new_transaction = response_json['transactions'][index]
                if new_transaction['propertyname'] in accepted_currencies:
                    transaction = formatter(new_transaction)
                    str = f'{str}{transaction}'

            if str != '':
                email(str)
                print("Email has been sent!")
            else:
                print("No new transaction available.")

            initial_transaction = transaction_txid
        else:
            print("No new transaction available.")
    except:
        print("Error, trying again.")


    time.sleep(20)

