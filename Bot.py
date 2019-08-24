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


# This takes a string, in this case the formatted string with all of the new transactions found, and prepares the
# string with necessary info before sending the string through email. The email and password variables will need
# to be changed if the sending email account is different.
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


# This will return a request made to the necessary api. If the request fails, it will call itself to try to make the
# request again.
def initial_requesting():
    try:
        return requests.post('https://api.omniexplorer.info/v1/address/addr/details/', headers=headers, data=data).json()['transactions'][0]
    except:
        print("Error, trying again.")
        time.sleep(20)
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

minimum_transaction_amount = 10000.0

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
        # This just checks to see if the most recent transaction is the same as the initial transaction, if they
        # aren't, then the code knows that there are potentially new transactions available.
        if transaction_txid != initial_transaction:
            num = find_transaction_amount(response_json)
            str = ''
            # The for loop will iterate through the new transactions found and prepare them all into a string.
            # This will leave out transactions that do not meet requirements.
            for index in range(0, num):
                new_transaction = response_json['transactions'][index]
                if new_transaction['propertyname'] in accepted_currencies and float(new_transaction['amount']) >= minimum_transaction_amount:
                    transaction = formatter(new_transaction)
                    str = f'{str}{transaction}'

            # If there is at least one transaction that meets requirements, the str variable should not be blank,
            # which means that there is a new transaction available to email out. If the str is blank, then
            # there aren't any new transactions we care about, so the program will let us know there are
            # no new transactions available, hence no email will be sent out.
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

