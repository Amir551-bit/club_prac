from enum import IntEnum


class MealStatus(IntEnum):
    draft = 1
    active = 2
    completed = 3
    expired = 4
    archived = 5
    cancelled = 6



class Meals(IntEnum):
    break_fast = 1
    first_snack = 2
    lunch= 3
    second_snack = 4
    dinner = 5
    before_practice = 6
    after_practice = 7
    before_sleep = 8



