import time
from math import ceil

from src.parking_slot import ParkingSlot
from src.vehicles import Vehicle
from src.db import session
from src.exceptions import NoMoreAvailableSpot, VehicleNotParked
from src.enums import VehicleSize, Size, EntryPoint, Rates, Hours

from datetime import datetime


class ParkingLot:
    """
    This class holds the information of the ParkingLot object. It contains the ParkingSlot objects
    and the number of entry points.
    """

    def __init__(self, slot_sizes: list, distances: list, entrypoints: int = 3, flat_rate=40):
        if any(len(distance) != entrypoints for distance in distances):
            raise ValueError("Invalid number of distances for number of entrypoints.")

        if len(slot_sizes) != len(distances):
            raise ValueError("Number of slot sizes and distances do not match.")

        self._entrypoints = entrypoints
        self._parking_slots = self.initialize_parking_slots(slot_sizes, distances)
        self._flat_rate = 40

    @property
    def parking_slots(self):
        return self._parking_slots

    @staticmethod
    def initialize_parking_slots(slot_sizes: list, distances: list):
        """
        A function that initializes the ParkingLot object with the ParkingSlot objects
        :param slot_sizes: list of sizes of the parking slots
        :param distances: list of the distances of the parking slots from the entry point
        :return: a list of ParkingSlot objects
        """
        num_of_spots = len(slot_sizes)
        occupied_slots = session.query(ParkingSlot).all()  # check if there are occupied slots from the db

        slots = [ParkingSlot(i, slot_sizes[i], distances[i]) for i in range(num_of_spots)]

        if len(occupied_slots) == 0:  # if no occupied slots from the db, return the initialized slots
            return slots

        for slot in occupied_slots:  # if occupied slots exist from the db, modify the parking slot objects
            slots[slot.slot_id].vehicle = slot.vehicle
            slots[slot.slot_id].isempty = False

        return slots

    def find_nearest_slot(self, vehicle_size: Size, entrypoint: EntryPoint):
        """
        This function finds the nearest available slot based on the vehicle size and
        the entrypoint
        :param vehicle_size: the size of the vehicle
        :param entrypoint: the entry point of the parking lot
        :return: the nearest available ParkingSlot object
        """
        nearest_slot = None

        for slot in self._parking_slots:
            if slot.isempty and vehicle_size.value <= slot.size.value:
                if nearest_slot is None or slot.distances[entrypoint.value] < nearest_slot.distances[entrypoint.value]:
                    nearest_slot = slot

        return nearest_slot

    def park_vehicle(self, vehicle: Vehicle, entrypoint: EntryPoint, date_of_entry: datetime):
        """
        A function that parks a vehicle object to the nearest parking spot and adds the vehicle to the
        db
        :param vehicle: the Vehicle object
        :param entrypoint: the entrypoint where the vehicle came in
        :param date_of_entry: the date the vehicle came into the parking lot
        :return: a ParkingSlot object where the vehicle has parked
        """
        nearest_slot = self.find_nearest_slot(vehicle.size, entrypoint)

        if nearest_slot is None:
            raise NoMoreAvailableSpot("No more available parking slot for the vehicle.")

        vehicle_query = session.query(Vehicle).filter(Vehicle.license_plate == vehicle.license_plate)
        vehicle_parked_before = vehicle_query.one_or_none()

        if vehicle_parked_before and vehicle_parked_before.date_of_exit is not None:  # checks if the vehicle has parked before and if it came back within an hour
            time_diff_last_parked = date_of_entry - vehicle_parked_before.date_of_exit

            if time_diff_last_parked.days < 0:  # check for proper date values
                raise ValueError("Date of entry cannot be lower than the last date of exit.")

            if time_diff_last_parked.seconds/3600 <= Hours.WITHIN_CONTINUOUS.value:
                vehicle.charge_flat_rate = False  # don't charge flat rate if vehicle came back within an hour

            vehicle_query.delete()  # delete the existing vehicle from the db so we can add the vehicle from the parameter

        vehicle.date_of_entry = date_of_entry
        nearest_slot.vehicle = vehicle  # assign vehicle to the parking slot
        nearest_slot.isempty = False

        session.add(vehicle)  # add the vehicle to the db
        session.add(nearest_slot)  # add parking slot with the assigned vehicle to the db
        session.commit()

        print("Car parked")
        return nearest_slot

    def unpark_vehicle(self, vehicle: Vehicle, date_of_exit: datetime):
        """
        A function that unparks a vehicle object from it's parking slot and modifies the vehicle entry
        within the db.
        :param vehicle: the Vehicle object
        :param date_of_exit: the date the vehicle left the parking slot
        :return: the total parking fee for the vehicle
        """
        vehicle_query = session.query(Vehicle).filter(Vehicle.license_plate == vehicle.license_plate)
        slot_query = session.query(ParkingSlot).filter(ParkingSlot.vehicle_plate == vehicle.license_plate)

        vehicle_slot = slot_query.one_or_none()

        if vehicle_slot is None:  # makes sure that a vehicle being unparked is currently in the parking lot
            raise VehicleNotParked("The vehicle being unparked is currently not parked in a parking slot.")

        date_of_entry = vehicle_query.one().date_of_entry  # get the date of entry from the db

        if date_of_exit < date_of_entry:  # check for proper date values
            raise ValueError("Date of exit can't be lower than the date of entry.")

        vehicle.slot = vehicle_slot
        vehicle.date_of_entry = date_of_entry
        vehicle.date_of_exit = date_of_exit

        total_fee = self.calculate_parking_fee(vehicle)

        self._parking_slots[vehicle_slot.slot_id].vehicle = None  # empty the parking slot
        self._parking_slots[vehicle_slot.slot_id].isempty = True

        session.delete(vehicle_slot)  # delete slot entry in the db

        vehicle_query.update({Vehicle.date_of_exit: date_of_exit})  # update the date of exit of the vehicle in the db

        session.commit()
        print(f"Car left the parking with total fee of {total_fee}")

        return total_fee

    def calculate_parking_fee(self, vehicle: Vehicle):
        """
        A function that calculates the total parking fee of the vehicle object
        :param vehicle: the Vehicle object
        :return: the total parking fee of the vehicle object
        """
        total_fee = 0
        exceeding_hours = 0

        time_diff_last_parked = vehicle.date_of_exit - vehicle.date_of_entry
        exceeding_days = time_diff_last_parked.days
        total_hours = exceeding_days * 24 + ceil(time_diff_last_parked.seconds / 3600)  # round up the hours

        if vehicle.charge_flat_rate:
            total_fee += self._flat_rate
            exceeding_hours = total_hours - Hours.WITHIN_FLAT_RATE.value

        if exceeding_hours > 0:
            print(f"{vehicle.size.name} sized vehicle with license plate {vehicle.license_plate} "
                  f"exceeded for {exceeding_hours} hour/s")
            total_fee += (Rates[vehicle.slot.size.name].value * exceeding_hours)  # if parked vehicle has exceeding hours

        if exceeding_days > 0:
            total_fee += (exceeding_days * Rates.DAY_OVER.value)  # if parked vehicle stayed more than a day

        return total_fee
