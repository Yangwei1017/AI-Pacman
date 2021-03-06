# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState) 
    self.numFood = len(self.getFood(gameState).asList())
    self.foodNum0 = len(self.getFood(gameState).asList())
    self.beliefs = [util.Counter(), util.Counter(), util.Counter(), util.Counter()]
    if self.red:
      count = 0
      self.opponentZeroPos = [(30, 14), (30, 13), (30, 12)]
      for index in self.getOpponents(gameState):
        self.beliefs[index][(30, 13 + count)] = 1
        count += 1
      self.pacman_land = 15
      self.ghost_land = 16
      self.going_left = -1
    else:
      count = 1
      self.opponentZeroPos = [(1, 1), (1, 2), (1, 3)]
      for index in self.getOpponents(gameState):
        self.beliefs[index][(1, 1 + count)] = 1
        count -= 1
      self.pacman_land = 16
      self.ghost_land = 15
      self.going_left = 1

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def getBeliefs(self, index):
    x = 0.0
    y = 0.0
    count = 0.0
    for p in self.beliefs[index]:
      x += p[0]
      y += p[1]
      count += 1.0
    return (round(x / count), round(y / count))


  def getNearestLegalLocation(self, location, gameState):
    if gameState.hasWall(int(location[0]), int(location[1])) == False:
        return location
    else:
      adjacencies = []
      adjacencies.append((location[0]-1, location[1]))
      adjacencies.append((location[0]+1, location[1]))
      adjacencies.append((location[0], location[1]-1))
      adjacencies.append((location[0], location[1]+1))
      for pos in adjacencies:
        if gameState.hasWall(int(pos[0]), int(pos[1])) == False:
          return pos
      return self.getNearestLegalLocation(random.choice(adjacencies), gameState)

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  ghostPosition = None
  elapseTime = 0

  def getFeatures(self, gameState, action):
    # features = util.Counter()
    # successor = self.getSuccessor(gameState, action)
    # features['successorScore'] = self.getScore(successor)

    # # Compute distance to the nearest food
    # foodList = self.getFood(successor).asList()
    # if len(foodList) > 0: # This should always be True,  but better safe than sorry
    #   myPos = successor.getAgentState(self.index).getPosition()
    #   minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    #   features['distanceToFood'] = minDistance
    # return features

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    foodList = self.getFood(successor).asList()
    capsules = self.getCapsules(successor)
    agentPosition = successor.getAgentState(self.index).getPosition()
    
    if len(foodList) > 0:
        averageDist = 0
        minDist =  float("infinity")
        for food in foodList:
            curDist = self.getMazeDistance(agentPosition, food)
            averageDist += curDist
            minDist = min(minDist, curDist)
        averageDist /= len(foodList)
        features['averageDist'] = averageDist
        features['minDist'] = minDist
    features['foodRemaining'] = len(foodList)
    opponentsInd = self.getOpponents(gameState)

    enemyPosition = None
    scaredTime = 0
    # for ind in opponentsInd:
    #     if not gameState.getAgentState(ind).isPacman:
    #         ghostAgent = gameState.getAgentState(ind)
    #         enemyPosition = ghostAgent.getPosition()
    #         scaredTime = ghostAgent.scaredTimer
    
    ghostAgent = gameState.getAgentState(opponentsInd[-1])
    enemyPosition = ghostAgent.getPosition()
    scaredTime = ghostAgent.scaredTimer

    if enemyPosition != None:
        self.elapseTime = 0
        self.ghostPosition = enemyPosition
    else:
        self.elapseTime += 1
        self.ghostPosition = self.inferencePos(gameState, action, self.elapseTime)

    features['scaredTime'] = scaredTime

    dist2enemy = float("infinity")
    if self.ghostPosition != None:
        dist2enemy = self.getMazeDistance(agentPosition, self.ghostPosition)

    if dist2enemy < 2:
        features['dist2enemy'] = -100
    elif dist2enemy < 5:
        features['dist2enemy'] = -100/dist2enemy
    else:
        features['dist2enemy'] = 0
    
    if scaredTime > 0:
        features['dist2enemy'] *= -1
        if dist2enemy == 0:
            features['dist2enemy'] = 1


    dist2Capsules = float("infinity")
    for capsule in capsules:
        dist2Capsules = min(self.getMazeDistance(agentPosition, capsule), dist2Capsules)

    features['dist2Capsules'] = 0 if dist2Capsules == float("infinity") else dist2Capsules

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'averageDist': 0, 'minDist': -1, 'dist2enemy': 1, 'scaredTime': 1, 'dist2Capsules': -5, 'foodRemaining': -40}

  def inferencePos(self, gameState, action, elapseTime):
    if self.ghostPosition == None:
        return None
    walls = gameState.getWalls().asList()
    x, y = self.ghostPosition
    ghostNextPosList = []
    n = (x, y+1)
    s = (x, y-1)
    w = (x-1, y)
    e = (x+1, y)
    if n not in walls:
        ghostNextPosList.append(n)
    if s not in walls:
        ghostNextPosList.append(s)
    if w not in walls:
        ghostNextPosList.append(w)
    if e not in walls:
        ghostNextPosList.append(e)
    for pos in ghostNextPosList:
        if self.overBound(gameState, pos):
            ghostNextPosList.pop(ghostNextPosList.index(pos))

    if elapseTime > 4 and elapseTime < 6:
        return random.choice(ghostNextPosList)
    elif elapseTime >= 6:
        return None
    dist2enemy = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), pos) for pos in ghostNextPosList]
    mindist = min(dist2enemy)

    nextPos = [pos for pos, dist in zip(ghostNextPosList, dist2enemy) if dist == mindist]

    return random.choice(nextPos)

  def overBound(self, gameState, position):
    x, y = position
    if gameState.isOnRedTeam(self.index):
        if x < 15:
            return True
    else:
        if x > 15:
            return True
    return False

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    if 'Stop' in actions:
        actions.pop(actions.index('Stop'))
    values = [self.miniMax(gameState, a, 1, -float("infinity"), float("infinity")) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

  def miniMax(self, state, action, depth, alpha, beta):
    successor = self.getSuccessor(state, action)

    opponentsInd = self.getOpponents(successor)
    ghostAgent = None
    ghostInd = 0
    for ind in opponentsInd:
        if not state.getAgentState(ind).isPacman:
            ghostAgent = state.getAgentState(ind)
            ghostInd = ind

 
    if ghostAgent == None or ghostAgent.getPosition() == None:
        return self.evaluate(state, action)
    else:
        return self.AlphaBetaMinValue(state, action, 1, alpha, beta, ghostInd)


  def AlphaBetaMinValue(self, state, action, depth, alpha, beta, ghostInd):
    # if state.isWin() == True or state.isLose() == True:
    #     return self.evaluate(state, action)
    if depth == 4:
        return self.evaluate(state, action)
    score = float("infinity")
    depth += 1

    state = state.generateSuccessor(self.index, action)
    ghostAction = state.getLegalActions(ghostInd)
    for ac in ghostAction:
      score = min(score, self.AlphaBetaMaxValue(state, ac, depth, alpha, beta, ghostInd))
      if score <= alpha:
        return score
      beta = min(beta, score)
    return score
    
    
  def AlphaBetaMaxValue(self, state, action, depth, alpha, beta, ghostInd):
    # if state.isWin() or state.isLose():
    #     return self.evaluate(state, action)
    score = -float("infinity")
    state = state.generateSuccessor(ghostInd, action)
    agentAction = state.getLegalActions(self.index)
    if 'Stop' in agentAction:
        agentAction.pop(agentAction.index('Stop'))
    for ac in agentAction:
        score = max(score, self.AlphaBetaMinValue(state, ac, depth, alpha, beta, ghostInd))
        if score >= beta:
            return score
        alpha = max(alpha, score)
    return score

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  def getClosestOpponent(self, gameState, action):
    nearest = 100
    successor = self.getSuccessor(gameState, action)
    myPos = successor.getAgentState(self.index).getPosition()
    opponentIdx = self.getOpponents(gameState)
    for index in opponentIdx:
      opponentPos = self.getBeliefs(index)
      nearest = min(nearest, self.getMazeDistance(myPos, self.getNearestLegalLocation(opponentPos, gameState)))
    return nearest


  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    features['noisyDistanceToInvader'] = self.getClosestOpponent(gameState, action)

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    capsuleList = self.getCapsulesYouAreDefending(successor)
    if len(capsuleList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])
      features['distanceToCapsule'] = minDistance

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      if myState.scaredTimer ==0:
        features['invaderDistance'] = min(dists)
      else: 
        features['invaderDistance'] = min(dists)*-1

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
