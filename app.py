
from time import sleep
import requests

# platform specific imports
from os import getenv as env, path
from asyncio import get_event_loop
from random import randint

# telethon specific imports
from telethon import TelegramClient as Client
from telethon.events import NewMessage
from telethon.tl.functions.messages import ImportChatInviteRequest

def getenv(key, default = ""):
  return env(key) or default

# start sending messages on behalf of accounts
async def start(phoneNumber: str) -> None:
  client = Client(
    SESSION_PATH + phoneNumber,
    API_ID,
    API_HASH
  )
  await client.start(phoneNumber)
  print(phoneNumber + " has been authenticated!")

  with open(GROUPS_PATH) as groups:
    while group := groups.readline().strip():
      site = requests.get(group)
      try:
        await client(ImportChatInviteRequest(site.url.split("/")[-1]))
        # send first messsage
        group = await client.get_entity(site.url)
        greetings = open(GREETING_PATH).readlines()
        greeting = greetings[randint(0, len(greetings)) - 1]
        await client.send_message(group, greeting)
      except: pass
  
  # profile = await client.get_me()
  @client.on(NewMessage())
  async def send_msg(message):
    # read all numbers and start task
    print(phoneNumber + " has started typing...")
    msgs = open(MESSAGES_PATH).readlines()
    msg = msgs[randint(0, len(msgs)) - 1] if msgs else "Hello"
    try:
      if path.exists(msg):
        await client.send_file(message.chat_id, msg)
      else:
        await client.send_message(message.chat_id, msg)
    except: pass

API_ID = getenv("API_ID")
API_HASH = getenv("API_HASH")

# config paths
GROUPS_PATH = "./groups.txt"
NUMBERS_PATH = "./numbers.txt"
MESSAGES_PATH = "./messages.txt"
GREETING_PATH = "./greetings.txt"
SESSION_PATH = "sessions/"

# create the loop handle
async_jobs = get_event_loop()

# read all numbers and start task
with open(NUMBERS_PATH) as numbers:
  while number := numbers.readline().strip():
    async_jobs.create_task(start(number))

async_jobs.run_forever()
