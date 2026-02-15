# Copyright (c) 2025-2026 Farix Embedded LLC
# Licensed under the Apache License, Version 2.0

"""
Utilities for use in Matt's Scripts
"""
from org.openpnp.machine.photon import PhotonFeeder
from org.openpnp.model import Location
from org.openpnp.model import LengthUnit


def rough_slot_location(machine, slot):
    """
    Get the rough location of a feeder's fiducial based on slot #
    """
    feeders = get_photon_feeders(machine)

    # Hack: Hard code the locations for feeders 1 and 26. Used for dead reckoning
    slot1_loc = Location(LengthUnit.Millimeters, 30.618, 65.054, 0, 0)
    slot26_loc = Location(LengthUnit.Millimeters, 408.315, 382.343, 0, 0)

    # # Alternative: Read slot 1 and 26 locations from the settings
    # slot1_loc = feeders[1].getSlot().getLocation()
    # slot26_loc = feeders[26].getSlot().getLocation()

    # One feeder to the next
    offset = Location(LengthUnit.Millimeters, 15.625, 0, 0, 0)
    # Extra offset between 12->13 and 37->38
    extra_offset = Location(LengthUnit.Millimeters, 2.11, 0, 0, 0)

    if slot <= 25:
        loc = Location(slot1_loc)
        loc = loc.add(offset.multiply(slot - 1))
        if slot > 12:
            loc = loc.add(extra_offset)
    else:
        loc = Location(slot26_loc)
        loc = loc.subtract(offset.multiply(slot - 1 - 25))
        if slot > 37:
            loc = loc.subtract(extra_offset)

    return loc


def get_photon_feeders(machine):
    """
    Returns a dict of [slot -> photon feeders] for all present preset feeders.
    Note: You really should scan feeders first.
    """
    feeders = {} # map slot(int) -> feeder
    for feeder in machine.getFeeders():
        if type(feeder) == PhotonFeeder:
            slot = feeder.getSlotAddress()
            if slot:
                feeders[slot] = feeder

    return feeders