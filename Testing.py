import requests
import json

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'addr': '1Po1oWkD2LmodfkBYiAktwh76vkF93LKnh'
}

response = requests.post('https://api.omniexplorer.info/v1/address/addr/details/', headers=headers, data=data)



print(response)