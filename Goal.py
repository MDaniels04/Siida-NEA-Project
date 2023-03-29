
import Tag

#A goal is something with prerequisite "tags" needed to be fulfilled for it to be considered "met"
class Goal():
    

    def __init__(self, GivenPrerequisiteTags, GivenGoalName, GivenPriority = 0):
      self.__Prereqs = GivenPrerequisiteTags
      self.__Priority = GivenPriority


      #Flavour text printed to console when talking about this
      self.__GoalName = GivenGoalName


#Goals can all be objects of the main class as they all have the same functionality...

#
#   Gs N Ss
#

    def _GetPrereqs(self):
        return self.__Prereqs

    def _GetPriority(self):
        return self.__Priority

    def _GetGoalName(self):
        return self.__GoalName