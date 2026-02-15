# Copyright (c) 2025-2026 Farix Embedded LLC
# Licensed under the Apache License, Version 2.0

### Start boilerplate preamble
# Setup for imports
import os.path, sys
python_scripts_folder = os.path.join(scripting.getScriptsDirectory().toString(),'')
sys.path.append(python_scripts_folder)

# Import local modules. Done this way to get code completion
try:
    from . import util
except:
    import util

import traceback
import time

# Get rid of warnings for using the implicit vars
machine = machine
config = config
gui = gui
### End boilerplate preamble


from org.openpnp.util import VisionUtils, OpenCvUtils
from org.openpnp.model import Location
from org.openpnp.model import LengthUnit

def main():
    """
    Sets the location and part offset for all feeders to zero (with a safe Z height of 30)
    """
    # TODO: Could base this on a search of tape hole
    # TODO: Could get info about tape width
    feeders = util.get_photon_feeders(machine)
    default_loc = Location(LengthUnit.Millimeters, 0, 0, 30, 0)

    for feeder in feeders.values():
        feeder.getSlot().setLocation(default_loc)
        feeder.setOffset(default_loc)


# Execute script in a thread so GUI Stay responsive
from java.lang import Thread, Runnable
class Worker(Runnable):
    def run(self):
        try:
            main()
        except Exception as e:
            print(traceback.format_exc(e))
            raise (e)
Thread(Worker()).start()
