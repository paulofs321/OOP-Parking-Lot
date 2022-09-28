from src.vehicles import *
from src.parking_slot import ParkingSlot
from src.parking_lot import AutomatedParkingLot, ParkingLot
from src.enums import Size, EntryPoint
from src.exceptions import *

from datetime import datetime

import pytest


class TestParkingLot:
    slots = [Size.SMALL, Size.LARGE, Size.MEDIUM, Size.SMALL, Size.MEDIUM, Size.LARGE]
    distances = [(1, 2, 3), (1, 3, 2), (3, 2, 1), (2, 1, 3), (3, 1, 2), (2, 3, 1)]
    entrypoints = [EntryPoint.A, EntryPoint.B, EntryPoint.C]

    parking_map = {
        "slot_sizes": slots,
        "distances": distances,
        "entrypoints": entrypoints
    }

    def test_init(self, session):
        parking_lot = AutomatedParkingLot(self.parking_map)

        parking_slots = parking_lot.parking_slots

        for slot in parking_slots:
            assert type(slot) == ParkingSlot

        assert type(parking_lot) == AutomatedParkingLot
        assert isinstance(parking_lot, ParkingLot)

    def test_invalid_init(self, session):
        invalid_parking_map = {
            "slot_sizes": self.slots,
            "distances": [(1, 2), (1, 3, 2), (3, 2, 1), (2, 1, 3), (3, 1, 2), (2, 3, 1)],  # element 0 only has 2 elem
            "entrypoints": self.entrypoints
        }
        with pytest.raises(ValueError):
            AutomatedParkingLot({})

        with pytest.raises(ValueError):
            AutomatedParkingLot({"slot_sizes": 1, "distances": 1, "entrypoints": 1})

        with pytest.raises(ValueError):
            AutomatedParkingLot(invalid_parking_map)

        with pytest.raises(TypeError):
            AutomatedParkingLot([1,2,3,4,5])

    def test_park_vehicle(self, session):
        parking_lot = AutomatedParkingLot(self.parking_map)

        vehicle_small = SmallParkingVehicle(license_plate="ABC456")
        vehicle_medium = MediumParkingVehicle(license_plate="MED123")
        vehicle_large = LargeParkingVehicle(license_plate="LRG123")

        slot_1 = parking_lot.park_vehicle(vehicle_small, EntryPoint.A, datetime(2022, 9, 25, 15, 30))
        slot_2 = parking_lot.park_vehicle(vehicle_medium, EntryPoint.B, datetime(2022, 9, 25, 15, 30))
        slot_3 = parking_lot.park_vehicle(vehicle_large, EntryPoint.C, datetime(2022, 9, 25, 15, 30))

        assert slot_1.slot_id == 0
        assert slot_2.slot_id == 4
        assert slot_3.slot_id == 5

        vehicle_large = ParkingVehicle(size=Size.LARGE, license_plate="ABC123")
        slot_4 = parking_lot.park_vehicle(vehicle_large, EntryPoint.C, datetime(2022, 9, 25, 15, 30))

        assert slot_4.slot_id == 1

        # there are only two available large slots so this one will fail
        vehicle_no_space = ParkingVehicle(size=Size.LARGE, license_plate="EFG123")

        with pytest.raises(NoMoreAvailableSpot):
            parking_lot.park_vehicle(vehicle_no_space, EntryPoint.C, datetime(2022, 9, 25, 15, 30))

        vehicle_small = ParkingVehicle(size=Size.SMALL, license_plate="ABC234")
        vehicle_medium = ParkingVehicle(size=Size.MEDIUM, license_plate="MED345")

        parking_lot.park_vehicle(vehicle_small, EntryPoint.A, datetime(2022, 9, 25, 15, 30))
        parking_lot.park_vehicle(vehicle_medium, EntryPoint.B, datetime(2022, 9, 25, 15, 30))

        # check the all available slots are taken
        for slot in parking_lot.parking_slots:
            assert slot.isempty is False

        # all the slots are already occupied, so this one should fail
        vehicle_no_space = ParkingVehicle(size=Size.SMALL, license_plate="EFG123")

        with pytest.raises(NoMoreAvailableSpot):
            parking_lot.park_vehicle(vehicle_no_space, EntryPoint.A, datetime(2022, 9, 25, 15, 30))

    def test_unpark_vehicle(self, session):
        parking_lot = AutomatedParkingLot(self.parking_map)

        vehicle = SmallParkingVehicle("SML123")

        parking_lot.park_vehicle(vehicle, EntryPoint.A, datetime(2022, 9, 25, 15, 30))
        total_fee = parking_lot.unpark_vehicle(vehicle, datetime(2022, 9, 25, 16, 30))

        assert total_fee == 40
        assert vehicle.flat_rate_hours == 2

        parking_lot.park_vehicle(vehicle, EntryPoint.A, datetime(2022, 9, 25, 16, 30))
        total_fee = parking_lot.unpark_vehicle(vehicle, datetime(2022, 9, 25, 17, 30))

        assert total_fee == 0
        assert vehicle.flat_rate_hours == 1

        parking_lot.park_vehicle(vehicle, EntryPoint.A, datetime(2022, 9, 25, 17, 30))
        total_fee = parking_lot.unpark_vehicle(vehicle, datetime(2022, 9, 25, 18, 30))

        assert total_fee == 0
        assert vehicle.flat_rate_hours == 0

        vehicle_in_medium_slot = ParkingVehicle(Size.MEDIUM, "QWE123")
        vehicle_in_large_slot = LargeParkingVehicle("QWE234")

        parking_lot.park_vehicle(vehicle, EntryPoint.A, datetime(2022, 9, 25, 18, 30))
        parking_lot.park_vehicle(vehicle_in_medium_slot, EntryPoint.B, datetime(2022, 9, 25, 18, 30))
        parking_lot.park_vehicle(vehicle_in_large_slot, EntryPoint.C, datetime(2022, 9, 25, 18, 30))

        total_fee_small_slot = parking_lot.unpark_vehicle(vehicle, datetime(2022, 9, 27, 19, 30))
        total_fee_medium_slot = parking_lot.unpark_vehicle(vehicle_in_medium_slot, datetime(2022, 9, 27, 19, 30))
        total_fee_large_slot = parking_lot.unpark_vehicle(vehicle_in_large_slot, datetime(2022, 9, 27, 19, 30))

        assert total_fee_small_slot == 10020
        assert total_fee_medium_slot == 10060
        assert total_fee_large_slot == 10100

