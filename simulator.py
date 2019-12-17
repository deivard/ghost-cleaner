import json
import threading
from GhostCleaner import GhostCleaner
import keyboard
import getopt
import sys

def kill(cleaners):
  for c in cleaners:
    print("Killing {}".format(c.name))
    c.activateKillswitch()

def main():
  # Command line arguments that is supported
  shortOptions = ""
  longOptions = ["cleaners=", "baseurl="]
  fullCmdArgs = sys.argv
  # The actual arguments passed 
  argList = fullCmdArgs[1:]
  try:
      args, values = getopt.getopt(argList, shortOptions, longOptions)
  except getopt.error as err:
      print(str(err))
      sys.exit(2)

  # Handle the arguments
  for currArg, currVal in args:
      if currArg in ("--cleaners"):
        numOfCleaners = int(currVal)
      if currArg in ("--baseurl"):
        baseUrl = currVal
        if baseUrl[-1] == "/":
          baseUrl = baseUrl[:-1]

  # EAFP style, "easier to ask forgiveness than permission" (https://stackoverflow.com/questions/9390126/pythonic-way-to-check-if-something-exists)
  try:
    numOfCleaners
  except NameError:
    numOfCleaners = 1
  try:
    baseUrl
  except NameError:
    baseUrl = "http://127.0.0.1:8000"
  
  f = open("export.geojson", "r")
  data = json.load(f)
  # Street is defined by a line
  lines = []
  cleaners = []

  for features in data["features"]:
    geometry = features["geometry"]
    if geometry["type"] == "LineString":
      coords = geometry["coordinates"]
      lines.append(coords)
      # print(coords)

  # Create the ghost cleaners
  for i in range(1,numOfCleaners+1):
    ghost = GhostCleaner("Harambe{}".format(i), i, baseUrl=baseUrl)
    cleaners.append(ghost)

  streetsPerCleaner = len(lines) / numOfCleaners
  threads = []

  # Create and start a thread for each cleaner
  for i, ghost in enumerate(cleaners):
    t = threading.Thread(target=ghost.startCleaning, args=(lines[int(i*streetsPerCleaner) : int((i+1)*streetsPerCleaner)],))
    threads.append(t)
    t.start()

  # Add the killswith button
  keyboard.add_hotkey("shift+esc", kill, args=(cleaners,))

  for t in threads:
    t.join()


if __name__ == "__main__":
  main()