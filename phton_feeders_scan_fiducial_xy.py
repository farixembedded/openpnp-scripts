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
    Scans for the fiducial location of installed photon feeders and uses vision to set the location exactly.

    Note: This currents needs the following to work (a bit hacky but it works):
    1. A Fidel Pipeline named FIDUCIAL-1X2 that matches the main Photon Fiducial
    """
    feeders = util.get_photon_feeders(machine)

    # Get the fiducial vision pipeline
    fid_vis_setting = next(x for x in config.getVisionSettings() if x.getName() == "FIDUCIAL-1X2")

    # Scan over all feeder fiducial and correct location with vision
    head = machine.getDefaultHead()
    camera = head.getDefaultCamera()

    feeders_scanned = 0
    for slot, feeder in feeders.items():
        print("Scanning slot {}".format(slot))
        rough_loc = util.rough_slot_location(machine, slot)
        camera.moveTo(rough_loc)

        pipeline = fid_vis_setting.getPipeline()
        pipeline.setProperty("camera", camera)
        def run_pipeline():
            # run the vision pipeline
            pipeline.process()
            result = pipeline.getExpectedResult("results")
            x = result.model[0].pt.x
            y = result.model[0].pt.y
            fid_loc = VisionUtils.getPixelLocation(camera, x, y)
            return fid_loc

        fid_loc = run_pipeline()
        # move to new location and re-run pipeline
        camera.moveTo(fid_loc)
        fid_loc = run_pipeline()

        # Now set the location of the feeder based on the above CV scan
        feeder_location = feeder.getSlot().getLocation()
        # for now, just do rotation based on slot (0 or 180)
        # TODO: Scan the sub-fiducial and determine feeder size and rotation
        rotation = 0
        if slot >= 26:
            rotation = 180
        # Update, don't blow away Z
        feeder_location = Location(LengthUnit.Millimeters, fid_loc.getX(), fid_loc.getY(), feeder_location.getZ(), rotation)
        feeder.getSlot().setLocation(feeder_location)

        # Show the CV detection results for a bit in the camera view
        gui.get().getCameraViews().getCameraView(camera).showFilteredImage(OpenCvUtils.toBufferedImage(pipeline.getWorkingImage()), 250)

        feeders_scanned += 1
        # for debugging
        # if feeders_scanned == 2:
        #     break


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
