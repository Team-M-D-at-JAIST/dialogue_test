import socket
import time
import requests
import json
import threading
import boto3
from boto3 import Session
import re
import string

access_token = ''
message = ""
lock = False


# get access to COTOHA webAPI
def get_access_to_COTOHA():
    headers = {
        'Content-Type': 'application/json',
    }

    data = '{\
                "grantType": "client_credentials", \
                "clientId": "XcfxEBpUO4H1E6l6GkrIEcP9varJAuma", \
                "clientSecret": "DYeyWcJr2PHLy89U"\
            }'

    response = requests.post('https://api.ce-cotoha.com/v1/oauth/accesstokens', headers=headers, data=data)

    print(response.json())  # JSON files about access information
    global access_token
    access_token = response.json()['access_token']

# invoke similarity API
def similarity_caculation(input_Sentence1, input_Sentence2):
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Authorization': 'Bearer ' + access_token,  # access_token is valid only for 24 hours
    }

    data = '{\
        "s1":"' + input_Sentence1 + '",\
        "s2":"' + input_Sentence2 + '",\
        "type": "default"}'
    response = requests.post('https://api.ce-cotoha.com/api/dev/nlp/v1/similarity', headers=headers, data=data.encode('utf-8'))

    return response.json()

def free_question_classifier(message):
    # Origin is necessary for all queries
    origin = ''
    destination = ''
    query_sentence={
        "time_cost":"どれくらい時間かかりますか",
        "distance":"距離はどのくらいですか",
        "cost":"料金はいくらですか",
    }

    query_dict=[
        {"time_cost": "時間"},
        {"distance":"距離"},
        {"cost":"料金"},
    ]

    input_Sentence1 = message
    similarity = 0
    for query in query_sentence:
        input_Sentence2 = query_sentence[query]
        if similarity < similarity_caculation(input_Sentence1, input_Sentence2)['result']['score']:
            similarity = similarity_caculation(input_Sentence1, input_Sentence2)['result']['score']
            query_type = query
    print(query_type)


message="料金について教えてほしいです"
get_access_to_COTOHA()
free_question_classifier(message)

