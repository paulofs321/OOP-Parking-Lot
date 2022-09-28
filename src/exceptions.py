class NoMoreAvailableSpot(Exception):
    """Raised when there are no more available spots in the parking lot"""
    pass


class VehicleNotParked(Exception):
    """Raised when unparking a vehicle that is not parked"""
    pass


class InvalidEntryPoint(Exception):
    """Raised when a vehicle enters in an invalid entrypoint"""
    pass


class VehicleAlreadyParked(Exception):
    """Raised when parking a vehicle that is already parked"""
    pass
