"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """
    def __init__(self, max_floor: int, num_people: int) -> None:
        ArrivalGenerator.__init__(self, max_floor, num_people)

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        random_arrivals = {}
        for i in range(self.num_people):
            starting_floor = random.randint(1, self.max_floor)
            target_floor = random.randint(1, self.max_floor)
            while starting_floor == target_floor:
                target_floor = random.randint(1, self.max_floor)
            if random_arrivals.get(starting_floor) is None:
                random_arrivals[starting_floor] = [Person(starting_floor,
                                                          target_floor)]
            else:
                random_arrivals[starting_floor].append(Person(starting_floor,
                                                              target_floor))
        return random_arrivals


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.
    """
    arrival_data: List[List[int]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """

        ArrivalGenerator.__init__(self, max_floor, None)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.

        csv_data = []
        line_counter = 0
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                # TODO: complete this. <line> is a list of strings corresponding
                # to one line of the original file.
                # You'll need to convert the strings to ints and then process
                # and store them.
                csv_data.append([int(line[0])])
                for j in range(len(line) - 1):
                    csv_data[line_counter].append(int(line[j + 1]))
                line_counter += 1
        self.arrival_data = csv_data

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        arrivals = {}
        for data in self.arrival_data:
            if data[0] == round_num:
                for j in range(1, (len(data)), 2):
                    if arrivals.get(data[j]) is None:
                        arrivals[data[j]] = [Person(data[j], data[j+1])]
                    else:
                        arrivals[data[1]].append(Person(data[j], data[j+1]))
        return arrivals


###############################################################################
# Elevator moving algorithms
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError

    def move_to_lowest(self,
                       elevator: Elevator,
                       waiting: Dict[int, List[Person]]) -> Direction:

        for floor in waiting:
            if len(waiting[floor]) != 0:
                if elevator.current_floor > floor:
                    elevator.current_floor -= 1
                    return Direction.DOWN
                else:
                    elevator.current_floor += 1
                    return Direction.UP
        return Direction.STAY

    def move_to_closest(self,
                        elevator: Elevator,
                        closest_above: int,
                        closest_below: int) -> Direction:

        if abs(elevator.current_floor - closest_above) > \
                abs(elevator.current_floor - closest_below):
                elevator.current_floor -= 1
                return Direction.DOWN

        elif abs(elevator.current_floor - closest_above) \
                < abs(elevator.current_floor - closest_below):
                elevator.current_floor += 1
                return Direction.UP
        else:  # in the case of ties
            elevator.current_floor -= 1
            return Direction.DOWN


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        direction = []
        for elevator in elevators:
            if elevator.current_floor == 1:
                direction.append(Direction.UP)
                elevator.current_floor = 2
            elif elevator.current_floor == max_floor:
                direction.append(Direction.DOWN)
                elevator.current_floor = max_floor - 1
            else:
                n = random.randint(-1, 1)
                if n == -1:
                    direction.append(Direction.DOWN)
                    elevator.current_floor -= 1
                elif n == 0:
                    direction.append(Direction.STAY)
                else:
                    direction.append(Direction.UP)
                    elevator.current_floor += 1
        return direction


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        direction = []
        for elevator in elevators:
            if len(elevator.passengers) == 0:
                move = self.move_to_lowest(elevator, waiting)
                direction.append(move)
            else:  # elevator is not empty
                if elevator.current_floor > elevator.passengers[0].target:
                    direction.append(Direction.DOWN)
                    elevator.current_floor -= 1
                else:
                    direction.append(Direction.UP)
                    elevator.current_floor += 1
        return direction


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        direction = []
        for elevator in elevators:
            if len(elevator.passengers) == 0:
               closest_above = self.get_closest_floor_above(elevator, waiting,
                                                             max_floor)
               closest_below = self.get_closest_floor_below(elevator, waiting)
               if closest_below != 0 and closest_above != 0:
                   direction.append(self.move_to_closest(elevator,
                                                         closest_above,
                                                         closest_below))
               elif closest_below == 0 and closest_above == 0:
                   direction.append(Direction.STAY)

               elif closest_below == 0:  # there's no one waiting below
                   direction.append(Direction.UP)
                   elevator.current_floor += 1

               elif closest_above == 0:  # there's no one waiting above
                   direction.append(Direction.DOWN)
                   elevator.current_floor -= 1
            else:  # elevator is not empty
                closest_above = self.get_closest_target_floor_above(elevator,
                                                                    max_floor)
                closest_below = self.get_closest_target_floor_below(elevator)
                if closest_below != 0 and closest_above != 0:
                    direction.append(self.move_to_closest(elevator,
                                                          closest_above,
                                                          closest_below))
                elif closest_below == 0:  # there's no target floor below
                    direction.append(Direction.UP)
                    elevator.current_floor += 1

                elif closest_above == 0:  # there's no target floor above
                    direction.append(Direction.DOWN)
                    elevator.current_floor -= 1

        return direction

    def get_closest_target_floor_below(self, elevator):
        for floor in reversed(range(1, elevator.current_floor)):
            for person in elevator.passengers:
                if person.target == floor:
                    return floor
        return 0

    def get_closest_target_floor_above(self, elevator, max_floor):
        for floor in (range(elevator.current_floor+1, max_floor+1)):
            for person in elevator.passengers:
                if person.target == floor:
                    return floor
        return 0

    def get_closest_floor_below(self, elevator, waiting):
        for floor in reversed(range(1, elevator.current_floor)):
            if len(waiting[floor]) != 0:
                closest_floor_below = floor
                return closest_floor_below
        return 0

    def get_closest_floor_above(self, elevator, waiting, max_floor):
        for floor in (range(elevator.current_floor+1, max_floor+1)):
            if len(waiting[floor]) != 0:
                closest_floor_above = floor
                return closest_floor_above
        return 0


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201']
    })
