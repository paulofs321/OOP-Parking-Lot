# OOP-Parking Lot (Python)
A parking system that pre-assigns a slot for every vehicle coming into the complex. No vehicle can freely choose a parking slot and no vehicle is reserved or assigned a slot until they arrive at the entry point of the complex. 
## Description
The system must assign a parking slot that satisfies the following constraints:

1. There are initially three (3) entry points, and there can be no less than three (3) leading into the parking complex. A vehicle must be assigned a possible and available slot closest to the parking entrance. The mall can decide to add new entrances later.

2. There are three types of vehicles: small (S), medium (M), and large (L), and there are three types of parking slots: small (SP), medium (MP), and large (LP).
(a) S vehicles can park in SP, MP, and LP parking spaces;
(b) M vehicles can park in MP and LP parking spaces; and
(c) L vehicles can park only in LP parking spaces.

3. Your parking system must also handle the calculation of fees, and must meet the following pricing structure:
(a) All types of car pay the flat rate of 40 pesos for the first three (3) hours;
(b) The exceeding hourly rate beyond the initial three (3) hours will be charged as follows:
20/hour for vehicles parked in SP;
60/hour for vehicles parked in MP; and
100/hour for vehicles parked in LP
Take note that exceeding hours are charged depending on parking slot size regardless of vehicle size.

For parking that exceeds 24 hours, every full 24-hour chunk is charged 5,000 pesos regardless of the parking slot.

The remainder hours are charged using the method explained in (b).

Parking fees are calculated using the rounding up method, e.g. 6.4 hours must be rounded to 7.

(c) A vehicle leaving the parking complex and returning within one hour based on their exit time must be charged a continuous rate, i.e. the vehicle must be considered as if it did not leave. Otherwise, rates must be implemented as described. For example, if a vehicle exits at 10:00 and returns at 10:30, continuous rate must apply.

## SRC Files
**parking_lot.py** - Contains the AutomatedParkingLot class that implements the requirements from the description.

**vehicles.py** - Contains the Vehicle base model and its subclasses.

**parking_slot.py** - Contains the ParkingSlot base model.

**fee_calculator.py** - Contains the ParkingFeeCalculator class that computes the
parking fee of a ParkingVehicle object.

**db.py** - Contains the sqlalchemy db session used by the system.

**enums.py** - Contains the enums for constants for the system.

**exceptions.py** - Contains the custom exceptions for the system.

## Installation
Before running the command below, make sure to have a Python 3.6+ interpreter and pip installed in your system.

```commandline
pip install requirements.txt
```

## Usage
Run the command below to execute main.py and run the interactive command line program.

```commandline
python main.py
```

You can also change the mapping of the parking lot by modifying this part of main.py file:

```
slots = [Size.SMALL, Size.LARGE, Size.MEDIUM, Size.SMALL, Size.MEDIUM, Size.LARGE]
distances = [(1, 2, 3), (1, 3, 2), (3, 2, 1), (2, 1, 3), (3, 1, 2), (2, 3, 1)]
entrypoints = [EntryPoint.A, EntryPoint.B, EntryPoint.C]
```

## Output
### AutomatedParkingLot Class

The automated parking lot has two main functions. The `park_vehicle` and `unpark_vehicle`.

The `park_vehicle` function takes a ParkingVehicle object, the entrypoint, and the date of entry as a datetime object.
When parking a vehicle, the function will assign the nearest possible ParkingSlot object from the
entrypoint to the vehicle. The function will then return the assigned parking slot.

The `unpark_vehicle` function takes a Vehicle object and the date of exit as a datetime object.
The function will remove the vehicle from it's assigned parking slot and return the total fee for 
the vehicle.