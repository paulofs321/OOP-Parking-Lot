from src.vehicles import Vehicle
from src.parking_slot import ParkingSlot
from src.parking_lot import ParkingLot
from src.enums import VehicleSize

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class TestParkingLot:
    def test_init(self, session):
        slots = [1, 1, 2, 2, 3, 3]
        distances = [(1, 2, 3), (1, 3, 2), (3, 2, 1), (2, 1, 3), (3, 1, 2), (2, 3, 1)]

        parking_lot = ParkingLot(slots, distances)

        parking_slots = parking_lot.parking_slots

        for slot in parking_slots:
            assert type(slot) == ParkingSlot