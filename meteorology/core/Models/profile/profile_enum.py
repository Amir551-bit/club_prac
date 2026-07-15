from enum import IntEnum


class Gender(IntEnum):
    man = 1
    woman = 2


class MembershipStatusForAthlete(IntEnum):
    yes = 1
    no = 2


class MainGoal(IntEnum):
    weight_loss = 1
    muscle_gain = 2
    fitness = 3
    strength = 4
    rehabilitation = 5
    general_health = 6
    competition = 7


class SpecialtiesEnum(IntEnum):
    body_building = 1
    weight_loss = 2
    Increase_in_volume = 3
    fitness = 4
    physical_fitness = 5
    Correct_body_shape = 6
    Powerlifting = 7
    Womens_workout = 8
    Exercise_for_the_elderly = 9
    Training_of_professional_athletes = 10


class CooperationStatusForCoach(IntEnum):
    yes = 1
    no = 2
