#!/usr/bin/env python
"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own. Check out the tutorials and articles on the contest website at
// http://www.ai-contest.com/resources.
"""

from PlanetWars import PlanetWars

# early game constants
CASH_RETURN_TIME_CAP = 13
SUPPORT_DISTANCE = 11
MAGIC_ABANDON_NUMBER = 15

def DoTurn(pw):
  global CASH_RETURN_TIME_CAP, FIRST_TURN
  mine, opp, neut = pw.AllPlanets();
  
  if len(mine) == 1 and len(opp) == 1:
    print "1 2 0 Excess:",mine[0].excess
    CASH_RETURN_TIME_CAP = pw.Distance(mine[0],opp[0]) + mine[0].excess / mine[0].growth_rate + 1
  
  # choose strat based on game state
  if pw.production[1] > pw.production[2]:
    all_out(mine,opp,neut,pw)
  elif len(mine) + len(opp)  <= 5:
    early_game(mine,opp,neut,pw)
  else:
    CASH_RETURN_TIME_CAP = 11
    standard(mine,opp,neut,pw)

def all_out(mine,opp,neut,pw):
  attack(mine,opp,pw)

def early_game(mine,opp,neut,pw):
  expand(mine,neut,opp,pw)
  attack(mine,opp,pw)

def standard(mine,opp,neut,pw):
  attack(mine,opp,pw)
  expand(mine,neut,opp,pw)

"""
retRate():
returns the number of turns it takes for a planet p to get a
full return from capturing a neutral planet n
"""
def retRate(p,n,dist): return (n.NumShips() + 1) / max(n.growth_rate,1) + dist

def canKill(a,b,pw):
  # a, b are planets
  dist = pw.Distance(a,b)
  req = b.NumShips() + ((dist+2) * b.growth_rate) + 2
  req += sum([f.num_ships for f in pw.Fleets() if f.dest == b.pid and f.owner == 2])
  req -= sum([f.num_ships for f in pw.Fleets() if f.dest == b.pid and f.owner == 1])
  return req

def attack(mine,opp,pw):
  global MAGIC_ABANDON_NUMBER
  
  fun = lambda p: lambda x,y: cmp(retRate(p,x,pw.Distance(p,x)), retRate(p,y,pw.Distance(p,y)))
  
  for p in mine:
    # print "1 2 0 NORMALNESS[0] id=",p.pid,"num_ships =",p.num_ships,"excess =",p.excess
    if p.excess < 0 and p.growth_rate <= 2 and abs(p.excess) > MAGIC_ABANDON_NUMBER * p.growth_rate:
      # ABANDON SHIP.
      # print "1 2 0 ABANDON SHIP",p.pid
      # print "ABANDON SHIP",p.pid
      # p.excess = p.num_ships
      help_others(p,pw)
      continue
    elif p.excess < 0:
      # print "1 2 0 ABANDON SHIP[2]",p.pid
      # halp! haalp!
      # print "HALP",p.pid,map(lambda x:(x[0],x[1].excess), pw.helpNeeded)
      continue
    # print "NORMALNESS 1",p.pid
    # we got some ships to spare. oh yeah.
    if p.growth_rate <= 2:
      # no one cares about you.
      # go help a bigger planet
      help_others(p,pw)
    
    opp.sort(cmp=fun(p))
    
    for e in opp:
      req = canKill(p, e, pw)
      
      if req > 0 and req <= p.excess:
        # print "1 2 0 NORMALNESS [3]",p.pid
        # p.excess -= req
        p.RemoveShips(req)
        pw.IssueOrder(p.pid, e.pid, req)
        pw.CreateFleet(p,e,req)
        if p.excess <= 0: break
      elif req == 0 and p.excess > 0:
        # print "1 2 0 NORMALNESS [4]",p.pid,"with req = ",req,"and excess = ",p.excess,"targeting",e.pid
        # can't kill, but let's toss some excess for pressure
        amount = (p.excess - 10) / 5
        if amount < e.growth_rate + (e.growth_rate / 5) + 1:
          # useless.
          # print "1 2 0 useless",p.pid
          continue
        # p.excess -= amount
        p.RemoveShips(amount)
        pw.IssueOrder(p.pid, e.pid, amount)
        pw.CreateFleet(p,e,amount)
        if p.excess <= 0: break
      # print "NORMALNESS 5",p.pid
    if p.excess > 0:
      help_others(p,pw)

def expand(mine,neut,opp,pw):
  global CASH_RETURN_TIME_CAP
  # print "expanding"
  expanded = False
  # search for some quick cash
  fun = lambda p: lambda x,y: cmp(retRate(p,x,pw.Distance(p,x)), retRate(p,y,pw.Distance(p,y)))
  for p in mine:
    closest = sorted(neut, cmp=fun(p))
    
    for n in closest:
      if retRate(p,n,pw.Distance(p,n)) > CASH_RETURN_TIME_CAP:
        break
      
      n_ships = canKill(p,n,pw)
      n_ships -= ((pw.Distance(p,n)+2) * n.growth_rate)
      if n_ships >= 0 and p.excess >= n_ships:
        p.RemoveShips(n_ships)
        pw.IssueOrder(p.pid, n.pid, n_ships)
        pw.CreateFleet(p,n,n_ships)
        expanded = True
  
  if not expanded:
    CASH_RETURN_TIME_CAP += 3
  
def help_others(p,pw):
  # first pass: help someone you can fully save
  for (turns_left,dyingPlanet) in pw.helpNeeded:
    if dyingPlanet.pid == p.pid: continue
    # print "1 2 0 ER WHAT[0]",p.pid
    # tup is in format: (turns_until_death, Planet)
    amount = abs(dyingPlanet.excess)
    if turns_left <= pw.Distance(p,dyingPlanet) and p.excess >= amount:
      # print "1 2 0 ER WHAT[1]",p.pid
      pw.IssueOrder(p.pid, dyingPlanet.pid, amount)
      p.RemoveShips(amount)
      dyingPlanet.HelpOut(amount)
  
  # second pass: just help whoever you can
  for (turns_left,dyingPlanet) in pw.helpNeeded:
    if dyingPlanet.pid == p.pid: continue
    # print "1 2 0 ER WHAT[2]",p.pid
    # tup is in format: (turns_until_death, Planet)
    amount = abs(dyingPlanet.excess)
    if amount > p.excess: amount = p.excess
    pw.IssueOrder(p.pid, dyingPlanet.pid, amount)
    p.RemoveShips(amount)
    dyingPlanet.HelpOut(amount)

def incoming(p,pw): return sum([f.num_ships for f in pw.Fleets() if f.dest == p.pid and f.owner == 2])

def main():
  map_data = ''
  while(True):
    current_line = raw_input()
    if len(current_line) >= 2 and current_line.startswith("go"):
      pw = PlanetWars(map_data)
      DoTurn(pw)
      pw.FinishTurn()
      map_data = ''
    else:
      map_data += current_line + '\n'


if __name__ == '__main__':
  try:
    import psyco
    psyco.full()
  except ImportError:
    pass
  try:
    main()
  except KeyboardInterrupt:
    print 'ctrl-c, leaving ...'
