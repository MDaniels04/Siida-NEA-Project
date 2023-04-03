
class Tag():

    def __init__(self, GivenTagName):
        #What do we identify this tag as?
        self.__TagName = GivenTagName

    def _GetTagName(self):
        return self.__TagName
