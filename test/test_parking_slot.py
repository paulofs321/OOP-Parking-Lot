from src.vehicles import Vehicle
from src.parking_slot import ParkingSlot
from src.enums import VehicleSize


class TestParkingSlot:
    def test_init(self):
        vehicle = Vehicle(VehicleSize.MEDIUM, "ABC123")
        slot1 = ParkingSlot(slot_id=0, size=1, distances=(1, 2, 3))
        slot2 = ParkingSlot(slot_id=1, size=2, distances=(2, 1, 3), vehicle=vehicle)

        assert type(slot1) == ParkingSlot, type(slot2) == ParkingSlot
        assert slot1.size == 1, slot2.size == 2
        assert slot1.vehicle is None and slot1.isempty is True
        assert slot2.vehicle == vehicle and type(slot2.vehicle) == Vehicle and slot2.isempty is False

    def test_isempty(self):
        slot1 = ParkingSlot(slot_id=0, size=1, distances=(1, 2, 3))

        assert slot1.isempty is True

        slot1.isempty = False

        assert slot1.isempty is False

