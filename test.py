import requests
import os
import argparse
import random
import time
import csv

tokenSlack = str(os.environ.get("slack_hichannel_token"))

# Formación del token
if tokenSlack == None:
    sys.exit("No hay variable de entorno `slack_hichannel_token` ni se ha proporcionado como parámetro")
    input("Pulse una ecla para continuar.")
    quit
token = tokenSlack

urlSlack = "https://slack.com/api/users.profile.set"
ctype = "application/json; charset=utf-8"
auth = "Bearer " + token

response = requests.post(urlSlack, headers = {'Content-type' : ctype, 'Authorization' : auth}, json = {
    "profile": {
        "status_text": "zzzzz",
        "status_emoji": "",
        "status_expiration": 0
        }
})

print(response.text)



'''
POST /api/users.profile.set
Host: slack.com
Content-type: application/json; charset=utf-8
Authorization: Bearer xoxp_secret_token
{
    "profile": {
        "status_text": "riding a train",
        "status_emoji": ":mountain_railway:",
        "status_expiration": 0
    }
}
'''

