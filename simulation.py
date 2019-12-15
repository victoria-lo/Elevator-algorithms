"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any
import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    """
    elevators: List[Elevator]
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    total_people: int
    total_completed: int
    timings: List
    iterations: int

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.elevators = []
        for i in range(config['num_elevators']):
            self.elevators.append(Elevator(config['elevator_capacity']))
        self.waiting = {}
        for i in range(1, config['num_floors']+1):
            self.waiting[i] = []
        self.num_floors = config['num_floors']
        self.arrival_generator = config['arrival_generator']
        self.moving_algorithm = config['moving_algorithm']
        self.visualizer = Visualizer(self.elevators,
                                     self.num_floors,
                                     config['visualize'])
        self.total_people = 0
        self.total_completed = 0
        self.timings = []
        self.iterations = 0

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """

        for i in range(num_rounds):

            self.iterations += 1

            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)

            self._update_wait_time()

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        arrivals = self.arrival_generator.generate(round_num)
        for floor in arrivals:
            self.total_people += len(arrivals[floor])
            self.waiting[floor].extend(arrivals[floor])
            for person in arrivals[floor]:
                person.wait_time = 0
        self.visualizer.show_arrivals(arrivals)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        for elevator in self.elevators:
            for person in elevator.passengers:
                if elevator.current_floor == person.target:
                    elevator.passengers.remove(person)
                    self.total_completed += 1
                    self.timings.append(person.wait_time)
                    self.visualizer.show_disembarking(person, elevator)
                    elevator.current_capacity -= 1

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for elevator in self.elevators:
            while elevator.current_capacity < elevator.capacity and \
                    len(self.waiting[elevator.current_floor]) != 0:
                self._boarding_people(elevator,
                                      self.waiting[elevator.current_floor][0])
                elevator.current_capacity += 1

    def _boarding_people(self,  elevator: Elevator, person: Person):
            elevator.passengers.append(person)
            self.visualizer.show_boarding(person, elevator)
            self.waiting[elevator.current_floor].remove(person)

    def _update_wait_time(self):
        for people in self.waiting.values():
            for person in people:
                person.wait_time += 1
        for elevator in self.elevators:
            for person in elevator.passengers:
                person.wait_time += 1

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        self.visualizer.show_elevator_moves(self.elevators,
                                            self.moving_algorithm.
                                            move_elevators(self.elevators,
                                                           self.waiting,
                                                           self.num_floors))

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """

        if len(self.timings) != 0:
            max_time = max(self.timings)
            min_time = min(self.timings)
            avg_time = int(round(sum(self.timings) / len(self.timings)))
        else:
            max_time = -1
            min_time = -1
            avg_time = -1

        return {
            'num_iterations': self.iterations,
            'total_people': self.total_people,
            'people_completed': self.total_completed,
            'max_time': max_time,
            'min_time': min_time,
            'avg_time': avg_time
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 5,
        'num_elevators': 2,
        'elevator_capacity': 1,
        'num_people_per_round': 2,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.FileArrivals(5, 'sample_arrivals.csv'),
        # algorithms.FileArrivals(1, 'sample_arrivals.csv')
        'moving_algorithm': algorithms.RandomAlgorithm(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(10)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4
    })
