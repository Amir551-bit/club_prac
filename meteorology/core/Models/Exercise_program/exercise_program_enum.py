from enum import IntEnum



class ProgramStatus(IntEnum):
    draft = 1
    active = 2
    completed = 3
    expired = 4
    archived = 5
    cancelled = 6



class DifficulityLevelMovement(IntEnum):
    easy = 1
    intermediate = 2
    hard = 3
    very_hard = 4


class ActiveStatusMovement(IntEnum):
    yes = 1
    no = 2


class Time(IntEnum):
    min_15 = 1
    min_20 = 2
    min_25 = 3
    min_30 = 4
    min_35 = 5
    min_40 = 6
    min_45 = 7
    min_50 = 8
    min_55 = 9
    hour_1 = 10
    hour_1_5 = 11     # یک ساعت و نیم 
    hour_2 = 12

class ExeeciseIntencity(IntEnum):
    easy = 1
    intermediate = 2
    hard = 3
    very_hard = 4


