from enum import IntEnum


class CoachTypeEnum(IntEnum):
    main = 1
    assistant = 2


class ConnectionStatusEnum(IntEnum):
    active = 1
    inactive = 2