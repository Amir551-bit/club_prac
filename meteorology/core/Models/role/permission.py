from enum import IntEnum



class Permission(IntEnum):
    none = 0
    general_visitor = 1 << 0
    athlete = 1 << 1
    coach = 1 << 2
    club_manager = 1 << 3
    club_owner = 1 << 4



ALL_PERMISSION = (1 << 5) - 1
GENERAL_VISITOR = Permission.general_visitor
ATHLETE = Permission.athlete
COACH = Permission.coach
CLUB_MANAGER = Permission.club_manager
CLUB_OWNER = Permission.club_owner