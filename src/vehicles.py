#from src.parking_slot import ParkingSlot
from sqlalchemy.orm import relationship

from src.enums import Size

from sqlalchemy import Column, String, Enum, DateTime, Integer, Boolean
from src.db import Base


class Vehicle(Base):
    """
    Model class for vehicles
    """
    __tablename__ = "vehicles"
    license_plate = Column(String, primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "vehicle",
    }


class SizedVehicle(Vehicle):
    __mapper_args__ = {"polymorphic_identity": "sized_vehicle"}
    size = Column(Enum(Size))


class ParkingVehicle(SizedVehicle):
    __mapper_args__ = {"polymorphic_identity": "parking_vehicle"}
    date_of_entry = Column(DateTime)
    date_of_exit = Column(DateTime, nullable=True)
    charge_flat_rate = Column(Boolean, default=True)
    flat_rate_hours = Column(Integer, default=3)
    slot = relationship("ParkingSlot", back_populates="vehicle", uselist=False, cascade='all, delete-orphan')

    def __init__(self, size, license_plate):
        super().__init__(size=size, license_plate=license_plate)


class SmallParkingVehicle(ParkingVehicle):
    __mapper_args__ = {"polymorphic_identity": "small_vehicle"}

    def __init__(self, license_plate):
        super().__init__(size=Size.SMALL, license_plate=license_plate)


class MediumParkingVehicle(ParkingVehicle):
    __mapper_args__ = {"polymorphic_identity": "medium_vehicle"}

    def __init__(self, license_plate):
        super().__init__(size=Size.MEDIUM, license_plate=license_plate)


class LargeParkingVehicle(ParkingVehicle):
    __mapper_args__ = {"polymorphic_identity": "large_vehicle"}

    def __init__(self, license_plate):
        super().__init__(size=Size.LARGE, license_plate=license_plate)
