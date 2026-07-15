from enum import IntEnum



class Permission(IntEnum):
    none = 0
    General_visitor = 1 << 0
    athlete = 1 << 1
    coach = 1 << 2
    club_manager = 1 << 3
    club_owner = 1 << 4



ALL_PERMISSION = (1 << 5) - 1