from enum import IntEnum


class NotificationsRequiredEnum(IntEnum):
    new_training_program = 1
    new_diet_plan = 2
    change_training_program = 3
    change_diet_plan = 4
    new_coach_message_or_note = 5
    important_club_announcement = 6
    approaching_the_end_of_the_program = 7
    new_information_recorded_by_the_athlete = 8
    change_coach = 9
    activate_or_deactivate_account = 10