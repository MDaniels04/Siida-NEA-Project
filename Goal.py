
import Tag

#A goal is something with prerequisite "tags" needed to be fulfilled for it to be considered "met"
class Goal():
    

    def __init__(self, GivenPrerequisiteTags, GivenGoalName, GivenPriority = 0):
      self.Prereqs = GivenPrerequisiteTags
      self.Priority = GivenPriority


      #Flavour text printed to console when talking about this
      self.GoalName = GivenGoalName


#Goals can all be children of the main class as they all have the same functionality...
