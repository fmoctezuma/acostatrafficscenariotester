#!/usr/bin/env python

import random

class Controller:
    def trafficRule(self,vQueue,hQueue):
	    return 0

    def __init__(self):
        random.seed(42)
        self.epigenVect = [0.5]

    def print_version(self):
        print("0")

    def modifyEpigenVect(self,mutationRate,mutateChange):
        hi = mutateChange
        lo = -hi
        for i in xrange(len(self.epigenVect)):
            if random.random() < mutationRate:
                mutationDelta = (hi - lo) * random.random() + lo
                self.epigenVect[i] += mutationDelta
                if self.epigenVect[i] > 1.0:
                    self.epigenVect[i] = 1.0
                if self.epigenVect[i] < 0.0:
                    self.epigenVect[i] = 0.0

    def writeEpigenVect(self,filename):
        with open(filename, "a") as epiFile:
            print >> epiFile, '<crossing>'
            for i in xrange(len(self.epigenVect)):
                print >> epiFile, '<item value="'+str(self.epigenVect[i])+'"/>'
            print >> epiFile, '</crossing>'
	
