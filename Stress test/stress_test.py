import requests

from random import choice, randint

import time

import sys

baseurl = sys.argv[1]

ACCOUNT_QTY = 1000 # Nimilistassa > 20 000 nimeä.
POST_QTY = 500

names = []
with open("nimet") as f:
    for line in f:
        names.append(line.strip("\n"))

def generateWord():
    word = choice(names)
    if randint(0, 20) == 10:
        word = "#"+word
    return word

def generateShitpost():
    result = str(time.time()) + " "
    word = generateWord()
    while len(result + " " + word) < 140:
        result = result + " " + word
        word = generateWord()
    return result.strip()

def generateName():
    name = f"{choice(names)} {choice('ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ')}. {choice('ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ')}. {choice('ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ')}."
    if len(name) <= 20:
        return name
    else:
        return generateName()

def createAccount(debug=False):
    session = requests.Session()
    name = generateName()
    password = "kissa123"
    if debug:
        print(f"Creating account '{name}'")
    text = session.post(f"{baseurl}/newaccount", {"account":name, "password":password}).text
    if debug:
        print(text)
    return session

def login(name):
    session = requests.Session()
    session.post(f"{baseurl}/login", {"account":name, "password":"kissa123"})
    return session

def postMessage(session, debug=False):
    text = session.get(f"{baseurl}/newpost").text
    payload = text.split("vote-")
    if len(payload) == 1:
        payload = {}
    else:
        payload = dict([("vote-"+x.split('"')[0], "on") for x in payload[1:]])
    payload["message"] = generateShitpost()
    session.post(f"{baseurl}/newpost", payload)
    if debug:
        print(payload)


print(f"Creating {ACCOUNT_QTY} accounts:")

t = time.time()

sessions = []

for x in range(ACCOUNT_QTY):
    print(f"{x} / {ACCOUNT_QTY}", end="\r")
    sessions.append(createAccount(False))

print(f"Done ({time.time() - t} seconds)")

t = time.time()

print(f"Creating {POST_QTY} posts:")

for x in range(POST_QTY):
    print(f"{x} / {POST_QTY}", end="\r")
    postMessage(choice(sessions))

print(f"Done ({time.time() - t} seconds)")
