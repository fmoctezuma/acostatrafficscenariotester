#!/usr/bin/env python
"""
@file    runnerExternal.py
@author  Lena Kalleske
@author  Daniel Krajzewicz
@author  Michael Behrisch
@author  Jakob Erdmann
@author  Esteban Ricalde
@date    2016-06-15

Tutorial for traffic light control via the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2015 DLR/TS, Germany

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""

import os
import sys
import optparse
import subprocess
import random
import struct
import xml.etree.ElementTree

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
# the port used for communicating with your sumo instance
PORT = 8873

import lightConfig
import controller
import light

def run(epigen,lights_2_opt):
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0

    trafficLightsIDs = traci.trafficlights.getIDList()
                        
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        #for all the lights to optimize
        for opt_light in lights_2_opt:
                        
            #check if light is in decision phase and a decision has not been made recently
            if traci.trafficlights.getPhase(opt_light.id) in opt_light.decision_phases and step > opt_light.lastChange + 4:                
                
                currentPhase = traci.trafficlights.getPhase(opt_light.id)

                #Store last change
                opt_light.lastChange = step 
                
                verQueue = 0
                horQueue = 0
                
                for b_det in opt_light.bottom_det:
                    verQueue +=  traci.multientryexit.getLastStepHaltingNumber(b_det.id) * b_det.mult
                
                for t_det in opt_light.top_det:
                    verQueue +=  traci.multientryexit.getLastStepHaltingNumber(t_det.id) * t_det.mult
                
                for l_det in opt_light.left_det:
                    horQueue += traci.multientryexit.getLastStepHaltingNumber(l_det.id) * l_det.mult

                for r_det in opt_light.right_det:
                    horQueue += traci.multientryexit.getLastStepHaltingNumber(r_det.id) * r_det.mult
                    
                modif = opt_light.control.trafficRule(verQueue,horQueue) * 1000
                
                if modif != 0:
                    verIncrement = modif > 0
                    
                    # modify all the vertical phases
                    for vertPhase in opt_light.vertical_phases:
                        new_duration = opt_light.phases[vertPhase].duration + modif
                        
                        if new_duration > opt_light.phases[vertPhase].minDur:
                            if new_duration < opt_light.phases[vertPhase].maxDur:
                                opt_light.phases[vertPhase].duration = new_duration
                            else:
                                opt_light.phases[vertPhase].duration = opt_light.phases[vertPhase].maxDur
                        else:
                            opt_light.phases[vertPhase].duration = opt_light.phases[vertPhase].minDur
                            
                    # modify all the horizontal phases
                    for horPhase in opt_light.horizontal_phases:
                        new_duration = opt_light.phases[horPhase].duration - modif

                        if new_duration > opt_light.phases[horPhase].minDur:
                            if new_duration < opt_light.phases[horPhase].maxDur:
                                opt_light.phases[horPhase].duration = new_duration
                            else:
                                opt_light.phases[horPhase].duration = opt_light.phases[horPhase].maxDur
                        else:
                            opt_light.phases[horPhase].duration = opt_light.phases[horPhase].minDur
                    
                    # redefine the phases to traci
                    phases = []
                    for phaseDef in opt_light.phases:
                        phases.append(traci.trafficlights.Phase(phaseDef.duration,phaseDef.duration,phaseDef.duration,phaseDef.state))
                    
                    logic = traci.trafficlights.Logic("utopia", "static", 0, currentPhase, phases)
                    traci.trafficlights.setCompleteRedYellowGreenDefinition(opt_light.id,logic)
                                                       
#                    print("Step: "+str(step)+", Crossing: "+str(opt_light.id)+" Phase: "+str(traci.trafficlights.getPhase(opt_light.id))+", Modifier: "+str(modif))
            
                if epigen:
                    opt_light.epigen_operation(verQueue,horQueue)
        step += 1
    
    if epigen:
        with open("updatedEpigenVect.xml", "w") as epiFile:
            print >> epiFile, '<output>'
            
        for opt_light in lights_2_opt:
            opt_light.control.writeEpigenVect("updatedEpigenVect.xml")

        with open("updatedEpigenVect.xml", "a") as epiFile:
            print >> epiFile, '</output>'
            
#    with open("finalConfig.txt", "w") as ligthFile:
#       for lightID in trafficLightsIDs:
#          lightToPrint = traci.trafficlights.getCompleteRedYellowGreenDefinition(lightID)
#          print >> ligthFile, lightToPrint
    traci.close()
    sys.stdout.flush()


def separated_args(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("-n","--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("-e","--epigen", action="store_true",
                         default=False, help="use epigenetic modifications")  
    optParser.add_option("-f","--fileName", type="string", default="optimized", help="Name of SUMO config file to use") 
    optParser.add_option("-d","--detFile", type="string", default="", help="Name of detectors asociated with each intersection to optimize") 
    optParser.add_option("-p","--phasesFile", type="string", default="", help="Name of file containing initial program of phases ")
    optParser.add_option("-g","--goalFile", type="string", default="", help="Name of file containing phases to be optimized")     
    optParser.add_option("-l","--lights", type='string', action='callback', callback=separated_args, help="List of light indices to be optimized")                       
    optParser.add_option("-t","--executionType", type="int", default="0", help="Type of execution: Static - 0, Human designed - 1, GP - 3, EpiGp - 4") 
    options, args = optParser.parse_args()
    return options

def load_xml_file(fileName):
    if not fileName:
        return null
    e = xml.etree.ElementTree.parse(fileName).getroot()
    return e

# this is the main entry point of this script
if __name__ == "__main__":
    
    options = get_options()
    
    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    detectors_tree = load_xml_file(options.detFile)
    opt_tree = load_xml_file(options.goalFile) 
    program_tree = load_xml_file(options.phasesFile) 
    
    lights_2_opt = []
    id_controllers = []
    i = 0
    
    for light_opt in options.lights:    
        obj = light.Light(light_opt,detectors_tree,opt_tree,program_tree)
        lights_2_opt.append(obj)
        if options.executionType < 3:
            id_controllers.append(options.executionType)
        else: 
            id_controllers.append(i)
        i += 1
    
    test = lightConfig.LightConfig(lights_2_opt,id_controllers)
    
    for test_light in lights_2_opt:
        test_light.control.print_version()    
    
    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    sumoProcess = subprocess.Popen([sumoBinary, "-c", "data/{:s}.sumocfg".format(options.fileName), "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    run(options.epigen, lights_2_opt)
#    sumoProcess.wait()
