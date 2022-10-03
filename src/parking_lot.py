from src.parking_slot import ParkingSlot
from src.vehicles import Vehicle, ParkingVehicle
from src.fee_calculator import ParkingFeeCalculator
from src.db import session
from src.exceptions import *
from src.enums import Size, EntryPoint, Hours

from sqlalchemy.orm import make_transient, with_polymorphic
from abc import ABC, abstractmethod
from datetime import datetime


class ParkingLot(ABC):
    """
    Abstract class of a parking lot
    """
    @abstractmethod
    def park_vehicle(self, vehicle: Vehicle):
        raise NotImplementedError("You need to implement this method.")

    @abstractmethod
    def unpark_vehicle(self, vehicle: Vehicle):
        raise NotImplementedError("You need to implement this method.")


class AutomatedParkingLot(ParkingLot):
    """
    A class for an automated parking lot that automatically assigns the nearest possible and
    available spot to a vehicle based on the entrypoint.
    """
    def __init__(self, parking_map: dict, num_of_entrypoints=3, fee_calculator=ParkingFeeCalculator(flat_rate=40)):
        """
        Constructor for the AutomatedParkingLot class

        :param parking_map: a dictionary that contains the mapping of the parking lot. Must contain a list
        of slot_sizes, a list of tuples where the entries in the tuple correspond to the distance from entrypoints,
        and a list of the possible entrypoints.
        :param num_of_entrypoints: the minimum number of entrypoints for the parking lot
        :param fee_calculator: the FeeCalculator object that will be used to calculate fees
        """
        self._num_of_entrypoints = num_of_entrypoints
        self._parking_map = parking_map
        self._fee_calculator = fee_calculator
        self._parking_slots = self._initialize_parking_slots()
        self._polymorphic_vehicle = with_polymorphic(Vehicle, '*')

    @property
    def parking_slots(self):
        return self._parking_slots

    @property
    def _parking_map(self):
        return self.__parking_map

    @_parking_map.setter
    def _parking_map(self, parking_map: dict):
        """
        A private setter method that validates the input parking map
        :param parking_map: the dictionary the contains the mapping of the parking lot
        :return:
        """
        if type(parking_map) != dict:
            raise TypeError("Parking map should be a dictionary.")

        if not parking_map.get("slot_sizes") or not parking_map.get("distances") or not parking_map.get("entrypoints"):
            raise ValueError("Parking map should contain the following fields: "
                             "slot_sizes, distances, and entrypoints")

        if any(type(field) != list for field in parking_map.values()):
            raise ValueError("The values of the parking map should be a list")

        slot_sizes = parking_map["slot_sizes"]
        distances = parking_map["distances"]
        entrypoints = sorted(parking_map["entrypoints"], key=lambda x: x.value)

        if any(len(distance) != self._num_of_entrypoints for distance in distances):
            raise ValueError("Invalid number of distances for number of entrypoints.")

        if len(slot_sizes) != len(distances):
            raise ValueError("Number of slot sizes and distances do not match.")

        if len(entrypoints) < self._num_of_entrypoints:
            raise ValueError(f"The number of entrypoints can't be less than {self._num_of_entrypoints}")

        if any(entrypoints[i].value + 1 != entrypoints[i + 1].value for i in range(len(entrypoints) - 1)):
            raise ValueError(f"The entrypoints must be in order.")

        self.__parking_map = parking_map

    def _initialize_parking_slots(self):
        """
        Initializes the parking slots of the parking lot with ParkingSlot objects
        :return: the list of initialized ParkingSlot objects
        """
        num_of_spots = len(self._parking_map["slot_sizes"])
        slot_sizes = self._parking_map["slot_sizes"]
        distances = self._parking_map["distances"]
        occupied_slots = session.query(ParkingSlot).all()  # check if there are occupied slots from the db

        slots = [ParkingSlot(i, slot_sizes[i], distances[i]) for i in range(num_of_spots)]

        if len(occupied_slots) == 0:  # if no occupied slots from the db, return the initialized slots
            return slots

        for slot in occupied_slots:  # if occupied slots exist from the db, modify the parking slot objects
            slots[slot.slot_id].vehicle = slot.vehicle
            slots[slot.slot_id].isempty = False

        return slots

    def _find_nearest_slot(self, vehicle_size: Size, entrypoint: EntryPoint):
        """
        This function finds the nearest available slot based on the vehicle size and
        the entrypoint
        :param vehicle_size: the size of the vehicle
        :param entrypoint: the entry point of the vehicle to the parking lot
        :return: the nearest available ParkingSlot object
        """
        if entrypoint not in self._parking_map["entrypoints"]:
            raise InvalidEntryPoint("Invalid entrypoint")

        # sort parking slots by distance from entrypoint and their size
        sorted_slots = sorted(self._parking_slots, key=lambda x: (x.distances[entrypoint.value], x.size.value))

        for slot in sorted_slots:
            if slot.isempty and vehicle_size.value <= slot.size.value:
                return slot

        return None

    def park_vehicle(self, vehicle: ParkingVehicle, entrypoint: EntryPoint = EntryPoint.A,
                     date_of_entry: datetime = datetime.now()):
        """
        A function that parks a vehicle object to the nearest parking spot and adds the vehicle to the
        db
        :param vehicle: the ParkingVehicle object
        :param entrypoint: the entrypoint where the vehicle came in
        :param date_of_entry: the date the vehicle came into the parking lot
        :return: the assigned ParkingSlot object for the vehicle
        """
        if not isinstance(vehicle, ParkingVehicle):
            raise VehicleIsNotAParkingVehicleObject("The vehicle is not a ParkingVehicle object.")

        nearest_slot = self._find_nearest_slot(vehicle.size, entrypoint)

        if nearest_slot is None:
            raise NoMoreAvailableSpot("No more available parking slot for the vehicle.")

        vehicle_query = session.query(self._polymorphic_vehicle).filter(Vehicle.license_plate == vehicle.license_plate)
        vehicle_parked_before = vehicle_query.one_or_none()

        if vehicle_parked_before:  # checks if the vehicle has parked before and if it came back within an hour
            if vehicle_parked_before.date_of_exit is None:
                raise VehicleAlreadyParked("The vehicle is already in the parking lot.")

            time_diff_last_parked = date_of_entry - vehicle_parked_before.date_of_exit

            if time_diff_last_parked.days < 0:  # check for proper date values
                raise ValueError("Date of entry cannot be lower than the last date of exit.")

            time_diff_hours = time_diff_last_parked.seconds/3600

            # if car came back within an hour, don't charge flat rate anymore and keep remaining flat rate hours
            if time_diff_hours <= Hours.WITHIN_CONTINUOUS.value:
                vehicle.charge_flat_rate = False
                vehicle.hour_paid = vehicle_parked_before.hour_paid
                vehicle.total_hours_stayed = vehicle_parked_before.total_hours_stayed
                #vehicle.flat_rate_hours = vehicle_parked_before.flat_rate_hours

            vehicle_parked_before.slot = None
            session.delete(vehicle_parked_before)  # delete the existing vehicle from the db so we can add the vehicle from the parameter
        else:
            vehicle.date_of_first_entry = date_of_entry

        vehicle.date_of_entry = date_of_entry

        make_transient(nearest_slot)
        nearest_slot.vehicle = vehicle  # assign vehicle to the parking slot
        nearest_slot.isempty = False

        session.add(vehicle)  # add the vehicle to the db
        session.add(nearest_slot)  # add parking slot with the assigned vehicle to the db

        session.commit()

        return nearest_slot

    def unpark_vehicle(self, vehicle: Vehicle, date_of_exit: datetime = datetime.now()):
        """
        A function that unparks a vehicle object from it's parking slot and modifies the vehicle entry
        within the db.
        :param vehicle: the ParkingVehicle object
        :param date_of_exit: the date the vehicle left the parking slot
        :return: the total parking fee for the vehicle
        """
        vehicle_query = session.query(self._polymorphic_vehicle).filter(self._polymorphic_vehicle.license_plate
                                                                        == vehicle.license_plate)
        parked_vehicle = vehicle_query.one()

        if parked_vehicle.slot is None:  # makes sure that a vehicle being unparked has a parking slot
            raise VehicleNotParked("The vehicle being unparked is currently not parked in a parking slot.")

        if date_of_exit < parked_vehicle.date_of_entry:  # check for proper date values
            raise ValueError("Date of exit can't be lower than the date of entry.")

        parked_vehicle.date_of_exit = date_of_exit

        total_fee = self._fee_calculator.calculate_fee(parked_vehicle)  # get the total fee

        slot_id = parked_vehicle.slot.slot_id

        session.delete(parked_vehicle.slot)

        self._parking_slots[slot_id].isempty = True  # empty the parking slot
        #self._parking_slots[slot_id].vehicle = None

        vehicle_query.update({
            ParkingVehicle.date_of_exit: date_of_exit,
            ParkingVehicle.hour_paid: parked_vehicle.hour_paid,
            ParkingVehicle.total_hours_stayed: parked_vehicle.total_hours_stayed
        })  # update the date of exit and remaining flat rate hours of the vehicle in the db

        session.commit()

        return total_fee
