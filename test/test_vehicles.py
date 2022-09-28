from src.vehicles import *
from src.parking_slot import ParkingSlot
from src.enums import Size

import pytest


class TestVehicle:
    def test_init(self):
        vehicle1 = SmallParkingVehicle("ABC123")
        vehicle2 = MediumParkingVehicle("ABC234")
        vehicle3 = LargeParkingVehicle("ABC345")

        vehicle4 = ParkingVehicle(Size.SMALL, "ABC456")

        assert vehicle1.license_plate == "ABC123"
        assert vehicle2.license_plate == "ABC234"
        assert vehicle3.license_plate == "ABC345"
        assert vehicle4.license_plate == "ABC456"
        assert vehicle1.size == Size.SMALL
        assert vehicle2.size == Size.MEDIUM
        assert vehicle3.size == Size.LARGE
        assert vehicle4.size == Size.SMALL
