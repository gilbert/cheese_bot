#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout


class Fleet:
  def __init__(self, owner, num_ships, source_planet, destination_planet, \
   total_trip_length, turns_remaining):
    self.owner = owner
    self.num_ships = num_ships
    self.source = source_planet
    self.dest = destination_planet
    self.total_trip_length = total_trip_length
    self.turns_left = turns_remaining


class Planet:
  _planets = {}
  @classmethod
  def read(cls, planet_id, owner, num_ships, growth_rate, x, y):
    p = cls._planets.get(planet_id)
    if p == None:
      p = cls._planets[planet_id] = Planet()
      p.update(planet_id, owner, num_ships, growth_rate, x, y)
    else:
      p.update(planet_id, owner, num_ships, growth_rate, x, y)
    return p
  
  def update(self,planet_id, owner, num_ships, growth_rate, x, y):
    self.pid = planet_id
    self.owner = owner
    self.num_ships = num_ships
    self.growth_rate = growth_rate
    self._x = x
    self._y = y
    self.excess = 0

  def PlanetID(self):
    return self.pid

  def Owner(self, new_owner=None):
    if new_owner == None:
      return self.owner
    self._owner = new_owner

  def NumShips(self, new_num_ships=None):
    if new_num_ships == None:
      return self.num_ships
    self.num_ships = new_num_ships

  def GrowthRate(self):
    return self.growth_rate

  def X(self):
    return self._x

  def Y(self):
    return self._y

  def AddShips(self, amount):
    self.num_ships += amount
    self.excess += amount

  def RemoveShips(self, amount):
    self.num_ships -= amount
    self.excess -= amount
    if self.excess > self.num_ships: self.excess = self.num_ships
  
  def HelpOut(self, amount):
    self.excess += amount
    if self.excess > self.num_ships: self.excess = self.num_ships


class PlanetWars:
  def __init__(self, gameState):
    self._fleets = []
    self.production = {0:0,1:0,2:0}
    self.ParseGameState(gameState)
    self.helpNeeded = []

  def CreateFleet(self,p,dest,amount):
    dist = self.Distance(p,dest)
    self._fleets.append(Fleet(p.owner,amount,p.pid,dest.pid,dist,dist))

  def NumPlanets(self):
    return len(Planet._planets)

  def GetPlanet(self, planet_id):
    return Planet._planets[planet_id]

  def NumFleets(self):
    return len(self._fleets)

  def GetFleet(self, fleet_id):
    return self._fleets[fleet_id]

  def Planets(self):
    return Planet._planets
  
  def AllPlanets(self):
    mine, opp, neut = ([],[],[])
    for pid, p in Planet._planets.items():
      if p.owner == 0:
        neut.append(p)
      elif p.owner == 1:
        mine.append(p)
      else:
        opp.append(p)
    growSort = lambda x,y: cmp(y.growth_rate,x.growth_rate)
    sizeSort = lambda x,y: cmp(y.num_ships,x.num_ships)
    mine.sort(cmp=sizeSort)
    opp.sort(cmp=growSort)
    neut.sort(cmp=growSort)
    
    # precalculate excess
    for p in mine:
      turns_left_until_death, excess = self.liferate(p)
      p.excess = excess
      if excess < 0:
        # halp! haalp!
        self.helpNeeded.append((turns_left_until_death,p))
      elif excess > p.num_ships:
        p.excess = p.num_ships
    self.helpNeeded.sort(cmp=lambda x,y: cmp(y[1].growth_rate,x[1].growth_rate))
    return (mine,opp,neut)

  # if death is detected at any point, returns the number of turns
  #   left to live and the extra number of ships needed (negative number).
  # if no death is detected, then returns the number of turns left for
  #   the last enemy to reach this planet, and the excess number of ships
  def liferate(self,p):

    turn = 0
    excess = p.num_ships
    fleets = [f for f in self.Fleets() if f.dest == p.pid]
    fleets.sort(cmp=lambda x,y: cmp(x.turns_left,y.turns_left))

    for f in fleets:
      if f.turns_left != turn:
        if excess < 0: return [turn,excess-p.growth_rate]
        prev = turn
        turn = f.turns_left
        excess += p.growth_rate * (f.turns_left - prev)
  
      if f.owner == 1:
        excess += f.num_ships
      elif f.owner == 2:
        excess -= f.num_ships

    return [turn,excess-p.growth_rate]

  def MyPlanets(self):
    r = []
    for p in Planet._planets:
      if p.Owner() != 1:
        continue
      r.append(p)
    return r

  def NeutralPlanets(self):
    r = []
    for p in Planet._planets:
      if p.Owner() != 0:
        continue
      r.append(p)
    return r

  def EnemyPlanets(self):
    r = []
    for p in Planet._planets:
      if p.Owner() <= 1:
        continue
      r.append(p)
    return r

  def NotMyPlanets(self):
    r = []
    for p in Planet._planets:
      if p.Owner() == 1:
        continue
      r.append(p)
    return r

  def Fleets(self):
    return self._fleets

  def MyFleets(self):
    r = []
    for f in self._fleets:
      if f.Owner() != 1:
        continue
      r.append(f)
    return r

  def EnemyFleets(self):
    r = []
    for f in self._fleets:
      if f.Owner() <= 1:
        continue
      r.append(f)
    return r

  def ToString(self):
    s = ''
    for p in Planet._planets:
      s += "P %f %f %d %d %d\n" % \
       (p.X(), p.Y(), p.Owner(), p.NumShips(), p.GrowthRate())
    for f in self._fleets:
      s += "F %d %d %d %d %d %d\n" % \
       (f.Owner(), f.NumShips(), f.SourcePlanet(), f.DestinationPlanet(), \
        f.TotalTripLength(), f.TurnsRemaining())
    return s

  def Distance(self, source_planet, destination_planet):
    source = Planet._planets[source_planet.pid]
    destination = Planet._planets[destination_planet.pid]
    dx = source.X() - destination.X()
    dy = source.Y() - destination.Y()
    return int(ceil(sqrt(dx * dx + dy * dy)))

  def IssueOrder(self, source_planet, destination_planet, num_ships):
    if num_ships <= 0: return
    # print "ISSUING ",num_ships,"SHIPS FROM",source_planet,"TO",destination_planet
    stdout.write("%d %d %d\n" % \
     (source_planet, destination_planet, num_ships))
    stdout.flush()

  def IsAlive(self, player_id):
    for p in Planet._planets:
      if p.Owner() == player_id:
        return True
    for f in self._fleets:
      if f.Owner() == player_id:
        return True
    return False

  def ParseGameState(self, s):
    self._fleets = []
    self.helpNeeded = []
    # self.capturing = []
    lines = s.split("\n")
    planet_id = 0

    for line in lines:
      line = line.split("#")[0] # remove comments
      tokens = line.split(" ")
      if len(tokens) == 1:
        continue
      if tokens[0] == "P":
        if len(tokens) != 6:
          return 0
        p = Planet.read(planet_id, # The ID of this planet
                   int(tokens[3]), # Owner
                   int(tokens[4]), # Num ships
                   int(tokens[5]), # Growth rate
                   float(tokens[1]), # X
                   float(tokens[2])) # Y
        if p.owner in [0,1,2]:
          self.production[p.owner] += p.growth_rate
        planet_id += 1
      elif tokens[0] == "F":
        if len(tokens) != 7:
          return 0
        f = Fleet(int(tokens[1]), # Owner
                  int(tokens[2]), # Num ships
                  int(tokens[3]), # Source
                  int(tokens[4]), # Destination
                  int(tokens[5]), # Total trip length
                  int(tokens[6])) # Turns remaining
        self._fleets.append(f)
      else:
        return 0
    # print "production:",self.production
    return 1

  def FinishTurn(self):
    stdout.write("go\n")
    stdout.flush()
