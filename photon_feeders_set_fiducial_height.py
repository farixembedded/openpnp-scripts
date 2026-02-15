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

from org.openpnp.model import Location
from org.openpnp.model import LengthUnit
from org.openpnp.spi.base import AbstractHead

from java.lang import Boolean


def main():
    """
    For all install photons, uses nozzle and vacuum sense to set height

    Pre reqs:
    * Must scan all feeders first in the GUI
    * Fiducial location must be set correctly
    * N045 must be installed and calibrated on Nozzle 1 (should check this in code via the machine)
    """
    # Vars that might need tweaking (mm)
    z_start_search = 4
    z_end_search = 1
    z_step = 0.1
    vac_threshold = 232

    feeders = util.get_photon_feeders(machine)

    head = machine.getDefaultHead()
    nozzle = head.getNozzles()[0]

    feeders_scanned = 0
    for slot, feeder in feeders.items():
        def do_z_probe():
            head.moveToSafeZ()

            nozzle_loc = nozzle.getLocation()
            feeder_loc = feeder.getSlot().getLocation()
            feeder_loc_xy_only = Location(LengthUnit.Millimeters, feeder_loc.getX(), feeder_loc.getY(), nozzle_loc.getZ(), nozzle_loc.getRotation())

            nozzle.moveTo(feeder_loc_xy_only)

            search_loc = Location(LengthUnit.Millimeters, feeder_loc.getX(), feeder_loc.getY(), z_start_search, 0)
            vac = nozzle.getExpectedVacuumActuator()
            vac.actuate(Boolean(True))

            while search_loc.getZ() >= z_end_search:
                nozzle.moveTo(search_loc)
                vac_val = int(vac.read())
                print("slot {} vac: {}".format(slot, vac_val))
                if vac_val <= vac_threshold:
                    print("Z probe success for slot {}, setting to height {}".format(slot, search_loc.getZ()))
                    feeder.getSlot().setLocation(Location(LengthUnit.Millimeters, feeder_loc.getX(), feeder_loc.getY(), search_loc.getZ(), feeder_loc.getRotation()))

                    # Note: this loses the sort order which is annoying, deal without it for now
                    # # update the GUI if we are currently looking at the changed feeder
                    # selection = gui.getFeedersTab().getSelection()
                    # if selection == feeder:
                    #     # Also save any sorting
                    #     gui.getFeedersTab().getTable()
                    #     gui.getFeedersTab().updateView()
                    #     gui.getFeedersTab().selectFeederInTable(selection)
                    break
                search_loc = search_loc.subtract(Location(LengthUnit.Millimeters, 0, 0, z_step, 0))

            if search_loc.getZ() < z_end_search:
                print('WARNING: no z height found for feeder {}'.format(slot))

            vac.actuate(Boolean(False))

        machine.execute(do_z_probe)
        head.moveToSafeZ()

        feeders_scanned += 1
        # for debugging
        # if feeders_scanned == 2:
        #     break


    # Note: Start 6mm, stop 1mm

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
