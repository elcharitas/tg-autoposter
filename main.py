from datetime import date
from app import ChatUI

STATES = {
  "paused": False,
  "code": False,
  "codeText": "",
  "delay": "3",
  "messages": "Logs for " + str(date.today())
}

def setState(state, status):
  STATES[state] =  status

def getState(state):
  return STATES[state]

if __name__ == '__main__':
  ChatUI(setState, getState).exec_()
