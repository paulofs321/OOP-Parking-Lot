import sqlalchemy.exc

from src.vehicles import Vehicle, Base
from src.parking_lot import ParkingLot
from src.parking_slot import ParkingSlot
from src.enums import VehicleSize, EntryPoint, Rates, Size
from src.db import engine, session

import datetime


def main():
    Base.metadata.create_all(engine)
    car = Vehicle(Size.LARGE, "ABC135")
    car2 = Vehicle(Size.LARGE, "ABC136")
    car3 = Vehicle(Size.MEDIUM, "ABC137")
    car4 = Vehicle(Size.SMALL, "ABC138")

    slots = [Size.SMALL, Size.SMALL, Size.MEDIUM, Size.MEDIUM, Size.LARGE, Size.LARGE]
    distances = [(1, 2, 3), (1, 3, 2), (3, 2, 1), (2, 1, 3), (3, 1, 2), (2, 3, 1)]

    parking_lot = ParkingLot(slots, distances)

    parking_lot.park_vehicle(car, EntryPoint.C, datetime.datetime(2022, 9, 26, 12, 0))
    parking_lot.park_vehicle(car2, EntryPoint.C, datetime.datetime(2022, 9, 26, 12, 0))
    parking_lot.park_vehicle(car3, EntryPoint.C, datetime.datetime(2022, 9, 26, 12, 0))
    parking_lot.park_vehicle(car4, EntryPoint.C, datetime.datetime(2022, 9, 26, 12, 0))

    #print(car.slot)
    for slot in parking_lot.parking_slots:
        if not slot.isempty:
            #print(slot.slot_id, Rates[Size(slot.size).name])
            parking_lot.unpark_vehicle(slot.vehicle, datetime.datetime(2022, 9, 26, 15, 30))
            # parking_lot.unpark_vehicle(car2, datetime.datetime(2022, 9, 26, 0, 30))
            # parking_lot.unpark_vehicle(car3, datetime.datetime(2022, 9, 26, 0, 30))
            # parking_lot.unpark_vehicle(car4, datetime.datetime(2022, 9, 26, 0, 30))




    #print(car.__dict__)
    #
    # print("After leaving")
    # print(slot.vehicle)
    # print(car.__dict__)
    # for slot in parking_lot._parking_slots:
    #     print(slot.__dict__)
    # print(parking_lot._parking_slots[5].vehicle_plate)
    # print(slot.__dict__)

    # #print(car._size)
    # #quer = session.query(Vehicle).filter(Vehicle.license_plate == "ABC123").one_or_none()
    #
    # session.add(car)
    # session.commit()


if __name__ == '__main__':
    main()
