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