import sqlite3

import sqlalchemy.exc

from src.vehicles import ParkingVehicle, Base
from src.parking_lot import AutomatedParkingLot
from src.enums import EntryPoint, Size
from src.db import engine

import datetime

Base.metadata.create_all(engine)

slots = [Size.SMALL, Size.LARGE, Size.MEDIUM, Size.SMALL, Size.MEDIUM, Size.LARGE]
distances = [(1, 2, 3), (1, 3, 2), (3, 2, 1), (2, 1, 3), (3, 1, 2), (2, 3, 1)]
entrypoints = [EntryPoint.A, EntryPoint.B, EntryPoint.C]

parking_map = {
    "slot_sizes": slots,
    "distances": distances,
    "entrypoints": entrypoints
}

parking_lot = AutomatedParkingLot(parking_map)


def entry_point_prompt():
    while True:
        entrypoint = input("Please enter the entrypoint (A/B/C): ")

        try:
            entrypoint = EntryPoint[entrypoint.upper()]
            return entrypoint
        except Exception as e:
            print("Invalid entrypoint, please try again.")


def date_prompt():
    while True:
        date_of_entry = input("Please enter the date (YYYY-MM-DD HH:MM): ")

        try:
            date_of_entry = datetime.datetime.strptime(date_of_entry, "%Y-%m-%d %H:%M")
            return date_of_entry
        except KeyError:
            print("Invalid date format, please try again.")


def size_prompt():
    while True:
        size = input("Enter the size of the vehicle (Small/Medium/Large): ")

        try:
            size = Size[size.upper()]
            return size
        except KeyError:
            print("Invalid size, please try again.")


def prompt(action):
    if action.lower() not in ["park", "unpark"]:
        print("Invalid action input, please try again.")
        return

    license_plate = input("Enter the license plate of the vehicle: ")
    size = size_prompt()
    vehicle = ParkingVehicle(size, license_plate)

    date = date_prompt()

    if action.lower() == "park":
        entrypoint = entry_point_prompt()
        try:
            slot = parking_lot.park_vehicle(vehicle, entrypoint, date)
            print(f"Successfully parked the vehicle with license plate {vehicle.license_plate} in slot {slot.slot_id}")
        except Exception as e:
            print(e)
    elif action.lower() == "unpark":
        try:
            total_fee = parking_lot.unpark_vehicle(vehicle, date)
            print(f"Successfully unparked the vehicle with license plate {vehicle.license_plate} "
                  f"with a total fee of {total_fee}")
        except Exception as e:
            print(e)


def main():
    print("Welcome to the OOP Parking Lot!")
    while True:
        action = input("Please select an action (park/unpark): ")
        prompt(action)


if __name__ == '__main__':
    main()
