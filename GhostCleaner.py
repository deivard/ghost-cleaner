import time
import requests
import math
import numpy as np
import random
from datetime import datetime

class GhostCleaner():
  def __init__(self, name, driverId, speed = 800, baseUrl = "http://127.0.0.1:8000", jobType = 0):
    self.name = name
    self.driverId = driverId
    self.streets = None
    self.sessionId = 0
    self.subSessionId = 0
    self.subSessionDistance = 0
    self.baseUrl = baseUrl
    self.location =  [0, 0] # lat, lon for Google. lon lat for geojson
    self.speed = speed / 1000000
    self.killswitch = 0
    self.jobType = jobType
    # Check if the jobType should be randomized
    if (jobType == 0):
      self.jobType = random.randint(1,3)


  def activateKillswitch(self):
    self.updateActiveStatus(0)
    self.killswitch = 1


  def updateActiveStatus(self, status):
    url = "{}/api/driver/{}/status".format(self.baseUrl, self.driverId)
    data = { 'active': int(status)}
    r = requests.post(url = url, data = data)
    # print(r)

  def sendLocationToDB(self):
    timestamp = int(time.time())
    url = "{}/api/location".format(self.baseUrl)
    data = { 
      'driver_id': self.driverId,
      'lat': self.location[1],
      'lng': self.location[0],
      'sent_at' : timestamp,
      'job_id' : self.jobType,
      'meters_in_sub_session' : float(self.subSessionDistance),
      'session_id': self.sessionId,
      'sub_session_id': self.subSessionId
    }
    print("{} - Sending location {} to api ({})".format(datetime.now(), self.location, url))
    r = requests.post(url = url, data = data)

  

  def calculateNextPosition(self, wpStart, wpEnd):
    # Find out delta lon and lat for wpStart and wpEnd
    dWpLat = wpEnd[0] - wpStart[0]
    dWpLon = wpEnd[1] - wpStart[1]

    vector = [dWpLon, dWpLat]
    vectorLength = math.sqrt(vector[0]**2 + vector[1]**2)
    # New vector with speed as length
    speedVector = [vector[0]*(self.speed / vectorLength), vector[1]*(self.speed / vectorLength)]
    # print(speedVector)

    xVector = np.array([1,0])
    yVector = np.array([0,1])
    # Project speedVector onto x and y
    speedVProjX =  np.dot(speedVector, xVector) / np.dot(xVector, xVector)
    # print(speedVProjX)
    speedVProjY =  np.dot(speedVector, yVector) / np.dot(yVector, yVector)
    # print(speedVProjY)
    # print("---")

    newLat = round(self.location[0] + speedVProjY, 7)
    newLon = round(self.location[1] + speedVProjX, 7)

    # print("New lon: {}".format(newLon))
    # print("New lat: {}".format(newLat))

    # Check if we overstepped
    if dWpLon > 0:
      if newLon > wpEnd[1]:
        newLon = wpEnd[1]
        # print("Overstepped lon")
    else:
      if newLon < wpEnd[1]:
        newLon = wpEnd[1]
        # print("Overstepped lon")
    if dWpLat > 0:
      if newLat > wpEnd[0]:
        newLat = wpEnd[0]
        # print("Overstepped lat")
    else:
      if newLat < wpEnd[0]:
        newLat = wpEnd[0]
        # print("Overstepped lat")


    
    return [newLat, newLon]

  # Stolen from https://stackoverflow.com/a/4913653
  def haversine(self, lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6372.8 # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000



  # Sets the ghost's position to the new position and sends an update to the database
  def updateLocation(self, location):
    distance = self.haversine(self.location[1], self.location[0], location[1], location[0])
    self.subSessionDistance += distance
    self.location = location
    self.sendLocationToDB()


  # Moves slowly from wpStart to wpEnd and then returns 
  def creepToWaypoint(self, wpStart, wpEnd):
    while (1):
      newLocation = self.calculateNextPosition(wpStart, wpEnd)
      # print("Start locatn: {}".format(wpStart))
      # print("End   locatn: {}".format(wpEnd))
      # print("New location: {}".format(newLocation))
      self.updateLocation(newLocation)
      time.sleep(4.5)
      if newLocation == wpEnd or self.killswitch:
        return


  def startCleaning(self, streets):
    self.streets = streets
    self.sessionId += 1
    self.subSessionId = 0

    # print(self.streets)
    # Loop the list of streets (a street is defined by a list of waypoints (coordinates))
    for waypoints in self.streets:
      self.location = waypoints[0]
      # print(waypoints)
      self.updateActiveStatus(1)
      self.subSessionId += 1
      self.subSessionDistance = 0
      # Loop each waypoint that makes up the street
      for wp in range(len(waypoints)-1):
        if self.killswitch:
          return
        # Move from waypoint to the next waypoint
        self.creepToWaypoint(waypoints[wp], waypoints[wp+1])
        # print(self.location)

      # When a streets is cleaned, simulate a pause while the ghost cleaner drives to the new street
      self.updateActiveStatus(0)
      time.sleep(2)
