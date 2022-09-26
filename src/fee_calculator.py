from abc import ABC, abstractmethod
from src.vehicles import Vehicle
from src.enums import Rates, Hours

from math import ceil


class FeeCalculator(ABC):
    @abstractmethod
    def calculate_fee(self, obj: object):
        raise NotImplementedError("You need to implement this method.")


class ParkingFeeCalculator(FeeCalculator):
    def __init__(self, flat_rate=40):
        self._flat_rate = flat_rate

    def calculate_fee(self, vehicle: Vehicle):
        """
        A function that calculates the total parking fee of the vehicle object
        :param vehicle: the Vehicle object
        :return: the total parking fee of the vehicle object
        """
        total_fee = 0

        time_diff_last_parked = vehicle.date_of_exit - vehicle.date_of_entry
        exceeding_days = time_diff_last_parked.days
        total_hours = exceeding_days * 24 + ceil(time_diff_last_parked.seconds/3600)  # round up the total hours parked

        # check if the vehicle stayed in the parking lot for more than a day and do the calculation
        if exceeding_days > 0:
            exceeding_hours = total_hours % Hours.IN_A_DAY.value  # get remainder of total_hours/hours_in_a_day(24)
            vehicle.charge_flat_rate = False  # a vehicle that stayed for more than a day will not have a flat rate
            total_fee += (Rates.DAY_OVER.value * exceeding_days)
        else:
            exceeding_hours = total_hours - vehicle.flat_rate_hours  # negative if vehicle stayed within flat rate hours

        if vehicle.charge_flat_rate:
            total_fee += self._flat_rate

        if exceeding_hours >= 0:  # calculation if vehicle has exceeded hours
            total_fee += (
                    Rates[vehicle.slot.size.name].value * exceeding_hours)
            vehicle.flat_rate_hours = 0  # if vehicle , that means it consumed the flat rate hours
        else:
            vehicle.flat_rate_hours = abs(exceeding_hours)

        return total_fee
