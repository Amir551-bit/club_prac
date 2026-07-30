from enum import IntEnum



class NotificationType(IntEnum):
    general_news = 1
    club_closure = 2
    change_in_hours = 3
    repairs = 4
    water_or_power_outage = 5
    equipment_problem = 6
    class_cancellation = 7
    special_program = 8
    event = 9
    member_notice = 10
    trainer_notice = 11


class LevelOfImportance(IntEnum):
    normal = 1
    important = 2
    urgent = 3
    critical = 4



class AudienceOfAnnouncement(IntEnum):
    public = 1
    all_members = 2
    coaches = 3
    athletes = 4


class AnnouncementStatus(IntEnum):
    active = 1
    in_active = 2