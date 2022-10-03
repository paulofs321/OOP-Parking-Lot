#from src.parking_slot import ParkingSlot
from sqlalchemy.orm import relationship

from src.enums import Size

from sqlalchemy import Column, String, Enum, DateTime, Integer, Float, Boolean
from src.db import Base


class Vehicle(Base):
    """
    Model class for vehicles
    """
    __tablename__ = "vehicles"
    license_plate = Column(String, primary_key=True)
    type = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "vehicle",
        "polymorphic_on": type
    }


class SizedVehicle(Vehicle):
    __mapper_args__ = {"polymorphic_identity": "sized_vehicle"}
    size = Column(Enum(Size))


class ParkingVehicle(SizedVehicle):
    date_of_first_entry = Column(DateTime)
    date_of_entry = Column(DateTime)
    date_of_exit = Column(DateTime, nullable=True)
    charge_flat_rate = Column(Boolean, default=True)
    #flat_rate_hours = Column(Integer, default=3)
    total_hours_stayed = Column(Float, default=0)
    hour_paid = Column(Integer, default=0)
    slot = relationship("ParkingSlot", back_populates="vehicle", uselist=False, cascade='all, delete-orphan')

    __mapper_args__ = {"polymorphic_identity": "parking_vehicle"}

    def __init__(self, size, license_plate):
        super().__init__(size=size, license_plate=license_plate)


class SmallParkingVehicle(ParkingVehicle):
    __mapper_args__ = {"polymorphic_identity": "small_parking_vehicle"}

    def __init__(self, license_plate):
        super().__init__(size=Size.SMALL, license_plate=license_plate)


class MediumParkingVehicle(ParkingVehicle):
    __mapper_args__ = {"polymorphic_identity": "medium_parking_vehicle"}

    def __init__(self, license_plate):
        super().__init__(size=Size.MEDIUM, license_plate=license_plate)


class LargeParkingVehicle(ParkingVehicle):
    __mapper_args__ = {"polymorphic_identity": "large_parking_vehicle"}

    def __init__(self, license_plate):
        super().__init__(size=Size.LARGE, license_plate=license_plate)
