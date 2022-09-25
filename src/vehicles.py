# from src.parking_slot import ParkingSlot
from sqlalchemy.orm import relationship

from src.enums import VehicleSize, Size

from sqlalchemy import Column, String, Enum, DateTime, Boolean
from src.db import Base


class Vehicle(Base):
    """
    Model class for vehicles
    """
    __tablename__ = "vehicles"
    license_plate = Column(String, primary_key=True)
    size = Column(Enum(Size))
    date_of_entry = Column(DateTime)
    date_of_exit = Column(DateTime, nullable=True)
    charge_flat_rate = Column(Boolean)
    slot = relationship("ParkingSlot", back_populates="vehicle", uselist=False, cascade='all, delete-orphan')

    def __init__(self, size: Size, license_plate: str, charge_flat_rate: bool = True):
        """
        The constructor for the Vehicle class
        :param size: size of the vehicle
        :param license_plate: license plate of the vehicle
        :param charge_flat_rate: boolean flag if vehicle should be charged the flat rate
        """
        super(Vehicle, self).__init__(size=size, license_plate=license_plate, charge_flat_rate=charge_flat_rate)
