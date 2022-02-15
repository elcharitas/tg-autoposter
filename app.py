import sys, pip
from typing import List
from pkgutil import iter_modules

# platform specific imports
from os import getenv as env, path
from asyncio import get_event_loop
from random import randint

# a set of installed modules
modules = {x[1] for x in iter_modules()}
dependency = ["telethon", "bs4", "requests", "python-dotenv"]

def install_dep(package):
  if hasattr(pip, 'main'):
    pip.main(['install', package])
  else:
    pip._internal.main(['install', package])

def launch_app():
  # telethon specific imports
  from telethon import TelegramClient as Client
  from telethon.events import NewMessage
  from telethon.tl.functions.messages import ImportChatInviteRequest

  # logic enhancing deps
  import requests
  from dotenv import load_dotenv

  # load the env in example.env
  load_dotenv("./example.env")

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
        print(message)
        return message[1]

  def get_reply(ref: str) -> List[str]:
    return messages[int(ref) - 1] if ref else get_rnd_msg()

  def get_rnd_msg():
    rnd = randint(0, len(messages))
    message = get_message(messages[rnd - 1])
    return message[0]

  # start sending messages on behalf of accounts
  async def start(phoneNumber: str) -> None:
    client = Client(
      SESSION_PATH + phoneNumber,
      API_ID,
      API_HASH
    )
    await client.start(phoneNumber)
    print(phoneNumber + " has been logged in!")

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
        return (message.reply(msg) if rnd == 0 else client.send_message(message.chat_id, msg))
      # read all numbers and start task
      print(phoneNumber + " has started typing...")
      mRef = get_ref(message.raw_text)
      msg = get_reply(mRef).capitalize()
      try:
        if path.exists(msg):
          await client.send_file(message.chat_id, msg)
        elif mRef: await reply(msg)
        else: await reply(msg, 1)
      except: pass

  # env variables
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

  # load the messages
  messages = open(MESSAGES_PATH).readlines()

  # read all numbers and start task
  with open(NUMBERS_PATH) as numbers:
    while number := numbers.readline().strip():
      async_jobs.create_task(start(number))

  async_jobs.run_forever()

for dep in dependency:
  if dep not in modules:
    install_dep(dep)

sys.exit(launch_app())
