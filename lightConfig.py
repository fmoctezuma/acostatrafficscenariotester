import random
import controller
import light

class Controller1(controller.Controller):
    def trafficRule(self,vQueue,hQueue):
	    if vQueue > hQueue + 4:
		    return 1
	    else:
		    if hQueue > vQueue + 4:
			    return -1
	    return 0
	
    def print_version(self):
        print("1")

    def __init__(self):
        random.seed(42)
        self.epigenVect = [0.5]		

class Controller2(controller.Controller):
    def trafficRule(self,vQueue,hQueue):
	    if vQueue > hQueue + 4:
		    return 1
	    else:
		    if hQueue > vQueue + 4:
			    return -1
	    return 0
	
    def print_version(self):
        print("2")

    def __init__(self):
        random.seed(42)
        self.epigenVect = [0.5]        

class Controller3(controller.Controller):
    def trafficRule(self,vQueue,hQueue):
	    if vQueue > hQueue + 4:
		    return 1
	    else:
		    if hQueue > vQueue + 4:
			    return -1
	    return 0
	
    def print_version(self):
        print("3")
        
    def __init__(self):
        random.seed(42)
        self.epigenVect = [0.5]


class Controller4(controller.Controller):
    def trafficRule(self,vQueue,hQueue):
	    if vQueue > hQueue + 4:
		    return 1
	    else:
		    if hQueue > vQueue + 4:
			    return -1
	    return 0
	
    def print_version(self):
        print("4")

    def __init__(self):
        random.seed(42)
        self.epigenVect = [0.5]

class LightConfig:
	
    def __init__(self,lightArray, controllerIdArray):
		i = 0
		while i < len(controllerIdArray):
			if controllerIdArray[i] == 0:
				control = controller.Controller()
				lightArray[i].set_controller(control)
			if controllerIdArray[i] == 1:
				control = Controller1()
				lightArray[i].set_controller(control)
			if controllerIdArray[i] == 2:
				control = Controller2()
				lightArray[i].set_controller(control)
			if controllerIdArray[i] == 3:
				control = Controller3()
				lightArray[i].set_controller(control)
			if controllerIdArray[i] == 4:
				control = Controller4()
				lightArray[i].set_controller(control)
			i += 1
		
