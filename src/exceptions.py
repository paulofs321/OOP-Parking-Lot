class NoMoreAvailableSpot(Exception):
    """Raised when there are no more available spots in the parking lot"""
    pass


class VehicleNotParked(Exception):
    """Raised when unparking a vehicle that is not parked"""
    pass