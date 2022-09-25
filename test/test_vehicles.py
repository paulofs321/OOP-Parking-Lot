from src.vehicles import Vehicle
from src.parking_slot import ParkingSlot
from src.enums import VehicleSize

import pytest


class TestVehicle:
    def test_init(self):
        vehicle1 = Vehicle(VehicleSize.SMALL, "ABC123")
        vehicle2 = Vehicle(VehicleSize.MEDIUM, "ABC234")
        vehicle3 = Vehicle(VehicleSize.LARGE, "ABC345")

        assert vehicle1.license_plate == "ABC123"
        assert vehicle2.license_plate == "ABC234"
        assert vehicle3.license_plate == "ABC345"
        assert vehicle1.size.value == VehicleSize.SMALL.value
        assert vehicle2.size.value == VehicleSize.MEDIUM.value
        assert vehicle3.size.value == VehicleSize.LARGE.value
