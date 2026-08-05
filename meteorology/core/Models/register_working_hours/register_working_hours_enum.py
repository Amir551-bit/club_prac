from enum import IntEnum


class StatusOpenning(IntEnum):
    is_open = 1
    closed = 2
    temporarily_closed = 3
    maintenance = 4
    special_schedule = 5