import xml.etree.ElementTree

class Detector:
	def __init__(self,id,mult):
		self.id = id
		self.mult = mult
	
	def print_self(self):
		print(self.id,self.mult)
		
class Phase:
    def __init__(self,state,duration,minDur,maxDur):
		self.state = state
		self.duration = duration
		self.minDur = minDur
		self.maxDur = maxDur
	
    def print_self(self):
        print(self.state,self.duration)

class Light:
    def __init__(self,id,detTree,optTree,programTree):
        self.id = id
        self.bottom_det = []
        self.top_det = []
        self.left_det = []
        self.right_det = []
        
        self.phases = []
        
        self.vertical_phases = []
        self.horizontal_phases = []
        self.decision_phases = []

        self.lastChange = 0
        self.cyclesCount = 0
        self.trafficStabylityAccum = 0.0
        
        # load detectors related to the crossing        
        crossing = detTree.find(".//intersection[@id='"+self.id+"']");
        for option in crossing:
			
			if option.get("dir") == "bottom":
				for detector in option:
					det = Detector(detector.get("id"),int(detector.get("multiplier")))
					self.bottom_det.append(det)

			if option.get("dir") == "top":
				for detector in option:
					det = Detector(detector.get("id"),int(detector.get("multiplier")))
					self.top_det.append(det)

			if option.get("dir") == "left":
				for detector in option:
					det = Detector(detector.get("id"),int(detector.get("multiplier")))
					self.left_det.append(det)

			if option.get("dir") == "right":
				for detector in option:
					det = Detector(detector.get("id"),int(detector.get("multiplier")))
					self.right_det.append(det)

        # load phases program to be used for the crossing
        crossing = programTree.find(".//tlLogic[@id='"+self.id+"']");
        for child in crossing:
			phase = Phase(child.get("state"),int(child.get("duration"))*1000,int(child.get("minDur"))*1000,int(child.get("maxDur"))*1000)
			self.phases.append(phase)

        # load phases to be optimized in the crossing
        crossing = optTree.find(".//intersection[@id='"+self.id+"']");
        for child in crossing:
			if child.tag == "horizontal":
				self.horizontal_phases.append(int(child.get("phase")))
			
			if child.tag == "vertical":
				self.vertical_phases.append(int(child.get("phase")))

			if child.tag == "decision":
				self.decision_phases.append(int(child.get("phase")))
	
    def	set_controller(self, control):
        self.control = control

    def epigen_operation(self,vQueue,hQueue):
         self.cyclesCount += 1
         trafficStabilityLast = vQueue - hQueue
         self.trafficStabylityAccum += trafficStabilityLast
     
         if self.cyclesCount == 10 :
             averageTrafficStability = self.trafficStabylityAccum * 1.0 / self.cyclesCount
             adaptiveFactor = (trafficStabilityLast - averageTrafficStability) / 50.0             
            
             if adaptiveFactor < 0.0:
                 adaptiveFactor = adaptiveFactor * -1.0
				 
             if adaptiveFactor > 1.0:
                 adaptiveFactor = 1.0
		     
             if adaptiveFactor > 0.0:
                 self.control.modifyEpigenVect(adaptiveFactor, 0.1)
			 
             self.cyclesCount = 0
             self.trafficStabylityAccum = 0

    def print_self(self):
		for phase in self.phases:
			phase.print_self()
		print("bottom")
		for bottom in self.bottom_det:
			bottom.print_self()
		print("top")
		for top in self.top_det:
			top.print_self()
		print("left")
		for left in self.left_det:
			left.print_self()
		print("right")
		for right in self.right_det:
			right.print_self()
		print(self.horizontal_phases)
		print(self.vertical_phases)
		print(self.decision_phases)
		
