import asyncio
from time import sleep
from typing import List

# platform specific imports
from os import getenv as env, path
from random import randint

# telethon specific imports
from telethon import TelegramClient as Client
from telethon.events import NewMessage
from telethon.tl.functions.messages import ImportChatInviteRequest

# logic enhancing deps
import requests
from dotenv import load_dotenv

# config paths
GROUPS_PATH = "./groups.txt"
NUMBERS_PATH = "./numbers.txt"
MESSAGES_PATH = "./messages.txt"
GREETING_PATH = "./greetings.txt"
SESSION_PATH = "sessions/"

# load the env in example.env
load_dotenv("./example.env")

# load the messages
messages = open(MESSAGES_PATH).readlines()

def getenv(key, default = "") -> str:
  return env(key) or default

def get_message(curMessage: str)-> List[str]: 
  msgList = curMessage.split(":")
  msgRef = msgList[-1] if len(msgList) > 1 else ""
  return [curMessage.replace(":" + msgRef, ""), msgRef.strip()]

def get_ref(msg: str):
  for message in messages:
    message = get_message(msg)
    if message[0].lower().strip() == msg.lower().strip():
      return message[1]

def get_reply(ref: str) -> List[str]:
  return messages[int(ref) - 1] if ref else get_rnd_msg()

def get_rnd_msg():
  rnd = randint(0, len(messages))
  message = get_message(messages[rnd - 1])
  return message[0]

# start sending messages on behalf of accounts
async def start(phoneNumber: str, getState, setStatus, getCode) -> None:
  setStatus(phoneNumber + " logging in now")
  if getState("paused"): return
  try:
    client = Client(
      SESSION_PATH + phoneNumber,
      getenv("API_ID"),
      getenv("API_HASH"),
      timeout=20
    )
    await client.start(phoneNumber, code_callback=lambda: getCode(phoneNumber), max_attempts=7)
    setStatus(phoneNumber + " has been logged in!")

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
    async def send_msg(message) -> None:
      def reply(msg, rnd = randint(0, 1)):
        sleep(float(getState("delay")))
        return (message.reply(msg) if rnd == 0 else client.send_message(message.chat_id, msg))
      if getState("paused") == False:
        # read all numbers and start task
        setStatus(phoneNumber + " has started typing...")
        mRef = get_ref(message.raw_text)
        msg = get_reply(mRef).capitalize()
        try:
          if path.exists(msg):
            await client.send_file(message.chat_id, msg)
          elif mRef: await reply(msg)
          else: await reply(msg, 1)
        except: pass
  except: setStatus("An error occurred while logging in " + phoneNumber)

def start_app(setState, getState):
  def setStatus(status):
    sleep(0.5)
    setState("messages", getState("messages") + "\n" + status)
    return getState("messages")
  def getCode(phone):
    setState("code", False)
    setStatus("Requesting code for "+phone+".. please check Telegram")
    sleep(12)
    if code := getState("codeText"):
      setStatus(" Code Received is: " + code)
      setState("codeText", "")
      setState("code", True)
      return code
  setStatus("Starting the script....")
  setStatus("Reading phone numbers...")
  loop = asyncio.new_event_loop()
  # read all numbers and start task
  with open(NUMBERS_PATH) as numbers:
    while number := numbers.readline().strip():
      loop.create_task(start(number, getState, setStatus, getCode))
  loop.run_forever()

