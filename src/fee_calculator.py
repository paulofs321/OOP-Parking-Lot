from abc import ABC, abstractmethod
from src.vehicles import ParkingVehicle
from src.enums import Rates, Hours
from src.exceptions import FeeCannotBeCalculated

from math import ceil, floor


class FeeCalculator(ABC):
    @abstractmethod
    def calculate_fee(self, obj: object):
        raise NotImplementedError("You need to implement this method.")


class ParkingFeeCalculator(FeeCalculator):
    def __init__(self, flat_rate=40):
        self._flat_rate = flat_rate

    def calculate_fee(self, vehicle: ParkingVehicle):
        """
        A function that calculates the total parking fee of the vehicle object
        :param vehicle: the Vehicle object
        :return: the total parking fee of the vehicle object
        """
        total_fee = 0

        if vehicle.date_of_entry is None or vehicle.date_of_exit is None:
            raise FeeCannotBeCalculated("Parking fee cannot be calculated. The vehicle must contain a date of entry "
                                        "and a date of exit.")

        time_diff_from_first_entry = vehicle.date_of_exit - vehicle.date_of_first_entry
        exceeding_days = time_diff_from_first_entry.days
        hours_stayed = exceeding_days * 24 + time_diff_from_first_entry.seconds/3600
        total_hours = exceeding_days * 24 + ceil(time_diff_from_first_entry.seconds/3600)  # round up the total hours parked

        vehicle.total_hours_stayed = hours_stayed

        if hours_stayed <= vehicle.hour_paid:
            return 0

        # check if the vehicle stayed in the parking lot for more than a day and do the calculation
        if exceeding_days > 0:
            exceeding_hours = total_hours % Hours.IN_A_DAY.value  # get remainder of total_hours/hours_in_a_day(24)
            vehicle.charge_flat_rate = False  # a vehicle that stayed for more than a day will not have a flat rate
            total_days_paid = floor(vehicle.hour_paid/24)
            unpaid_days = exceeding_days - total_days_paid
            total_fee = (Rates.DAY_OVER.value * unpaid_days)
            vehicle.hour_paid = unpaid_days * 24
        else:
            exceeding_hours = total_hours

            if vehicle.charge_flat_rate:
                total_fee += self._flat_rate
                vehicle.hour_paid = Hours.WITHIN_FLAT_RATE.value

            exceeding_hours -= vehicle.hour_paid

        if exceeding_hours >= 0:  # calculation if vehicle has exceeded hours
            total_fee += (
                    Rates[vehicle.slot.size.name].value * exceeding_hours)
            vehicle.hour_paid += exceeding_hours

        return total_fee
