from src.vehicles import Vehicle, ParkingVehicle
from src.enums import Size
from src.db import Base

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship


class ParkingSlot(Base):
    """
    This class is used to hold ParkingSlot objects information such as the size
    and the distance from each entry points in a form of a tuple
    """

    __tablename__ = "slots"
    slot_id = Column(Integer, primary_key=True)
    vehicle_plate = Column(String, ForeignKey(Vehicle.license_plate))
    size = Column(Enum(Size))
    vehicle = relationship("ParkingVehicle", back_populates="slot")

    def __init__(self, slot_id: int, size: Size, distances: tuple, vehicle: Vehicle = None):
        super(ParkingSlot, self).__init__(slot_id=slot_id, vehicle=vehicle, size=size)
        self._distances = distances

        if vehicle:
            self._isempty = False
        else:
            self._isempty = True

    @property
    def distances(self):
        return self._distances

    @property
    def isempty(self):
        return self._isempty

    @isempty.setter
    def isempty(self, flag: bool):
        if flag is True:
            self.vehicle = None

        self._isempty = flag

