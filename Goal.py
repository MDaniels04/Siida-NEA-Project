
import Tag

#A goal is something with prerequisite "tags" needed to be fulfilled for it to be considered "met"
class Goal():
    

    def __init__(self, GivenPrerequisiteTags, Given_GoalName, GivenPriority = 0):
      self._Prereqs = GivenPrerequisiteTags
      self._Priority = GivenPriority


      #Flavour text printed to console when talking about this
      self._GoalName = Given_GoalName


#Goals can all be children of the main class as they all have the same functionality...
