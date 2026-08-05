from fastapi import Depends, Path
from core.Models.profile.profile_athlete_model import ProfileAthlete, AthleteSportsInfo
from core.Models.profile.profile_coach_model import ProfileCoach, Specialties
from sqlalchemy.orm import Session
from sqlite.database import get_db
from core.execptions.execption import raise_bad_request, raise_not_found
from core.Models.connection_coach_to_athlete.coach_to_athlete import CoachAthleteConnection
from core.Models.Exercise_program.exercise_program import (ExerciseProgram, DailyPractice, InformationForMovement, 
                                                           MovementBank, RegistrationDailyPractice)
from core.Models.meal_plan.meal_plan import MealPlan, MealPlanDaily, FoodItems
from core.Models.notification_system.notification_system_model import NotificationSystem
from core.Models.measurement_and_progress.progress_process import ProgressPicture, ProgressProcess
from core.Models.user.user_model import User
from core.Models.user_role.user_role_model import UserRole

# connect coach to athlete

def check_active_coach(profile_id: int,
                       db: Session):
    check = db.query(ProfileCoach).filter(ProfileCoach.id==profile_id).first()
    if check.cooperation_status == 2:
        raise_bad_request("coach is inactive") 



def check_active_athlete(profile_id: int,
                   db: Session):
    check = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if check.membership_status == 2:
        raise_bad_request("athlete is inactive")



def get_profile_athlete_or_404(profile_id: int,
                                 db: Session = Depends(get_db)):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if not exists:
        raise_not_found("profile is not found")
    return exists

def get_profile_coach_or_404(profile_id: int,
                               db: Session = Depends(get_db)):
    
    exists = db.query(ProfileCoach).filter(ProfileCoach.id==profile_id).first()
    if not exists:
        raise_not_found("profile coach is not found")
    return exists


def get_coach_to_athlete_for_path(id: int = Path(...),
                                  db: Session = Depends(get_db)):

    exists = db.query(CoachAthleteConnection).filter(CoachAthleteConnection.id==id).first()
    if not exists:
        raise_not_found("is not found")
    return exists


def build_get_response_coach_to_athlete(connect: CoachAthleteConnection):

    profile_athlete = connect.athlete
    return {
        "profile_coach_id": connect.profile_coach_id,
        "profile_athlete_id": connect.profile_athlete_id,
        "start_date": connect.start_date,
        "status": connect.status,
        "coach_role": connect.coach_role,
        "manager_notes": connect.manager_notes,
        "end_date": connect.end_date,
        "profile_athlete" : profile_athlete
    }



# exercise program


def get_profile_coach(user_id: int, db: Session):
    exists = db.query(ProfileCoach).filter(ProfileCoach.user_id==user_id).first()
    if not exists:
        raise_not_found("profile coach is not found")
    return exists

def get_profile_athlete_for_path(profile_id: int = Path(...), 
                        db: Session = Depends(get_db)):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if not exists:
        raise_not_found("profile athlete is not found")
    return exists

def get_profile_athlete(profile_id: int, db: Session):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if not exists:
        raise_not_found("profile athlete is not found")
    return exists


def get_profile_athlete_with_user_id(user_id: int,
                                     db: Session):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.user_id==user_id).first()
    if not exists:
        raise_not_found("profile is not found")
    return exists

def accepted_coach_to_athlete(coach_id: int, athlete_id: int, db: Session):
    accepted = db.query(CoachAthleteConnection).filter(CoachAthleteConnection.profile_coach_id==coach_id,
                                                           CoachAthleteConnection.profile_athlete_id==athlete_id,
                                                           CoachAthleteConnection.status==1).first()
    if not accepted:
        raise_bad_request("you have not coach this athlete")
    return accepted


def get_exercise_program_for_path(program_id: int = Path(...),
                                  db: Session = Depends(get_db)):
    exists = db.query(ExerciseProgram).filter(ExerciseProgram.id==program_id).first()
    if not exists:
        raise_not_found("program is not found")
    return exists


def get_daily_practice_for_path(daily_practice_id: int = Path(...),
                                db: Session = Depends(get_db)):
    exists = db.query(DailyPractice).filter(DailyPractice.id==daily_practice_id).first()
    if not exists:
        raise_not_found("daily practice is not found")
    return exists




def get_movement_bank_for_path(movement_bank_id: int = Path(...),
                               db: Session = Depends(get_db)):
    exists = db.query(MovementBank).filter(MovementBank.id==movement_bank_id).first()
    if not exists:
        raise_not_found("movement bank is not found")
    return exists


def get_movement_bank(movement_bank_id: int, db: Session):
    exists = db.query(MovementBank).filter(MovementBank.id==movement_bank_id).first()
    if not exists:
        raise_not_found("movement bank is not found")
    return exists


def get_information_for_movement_for_path(information_movement_id: int = Path(...),
                                 db: Session = Depends(get_db)):
    exists = db.query(InformationForMovement).filter(InformationForMovement.id==information_movement_id).first()
    if not exists:
        raise_bad_request("movement information is not found")
    return exists


def get_registration_daily_practice_for_path(registration_daily_practice_id: int = Path(...),
                                             db: Session = Depends(get_db)):

    exists = db.query(RegistrationDailyPractice).filter(RegistrationDailyPractice.id==registration_daily_practice_id).first()
    if not exists:
        raise_not_found("this not found")
    return exists


def build_daily_practice(daily_practice: DailyPractice, total: int):
    exercise_program = daily_practice.exercise_program
    return {
        "exercise_program_id" : exercise_program.id,
        "title_session" : daily_practice.title_session,
        "day_number": daily_practice.day_number,
        "description": daily_practice.description,
        "warm_up": daily_practice.warm_up,
        "cardio":  daily_practice.cardio,
        "cool_down": daily_practice.cool_down,
        "created_date": daily_practice.created_date,
        "update_date": daily_practice.update_date,
    }


def build_daily_practice_with_information_practice(daily_practice: DailyPractice):
    information_movement = daily_practice.movements_info
    return {
            "title_session" : daily_practice.title_session,
            "day_number": daily_practice.day_number,
            "description": daily_practice.description,
            "warm_up": daily_practice.warm_up,
            "cardio":  daily_practice.cardio,
            "cool_down": daily_practice.cool_down,
            "created_date": daily_practice.created_date,
            "update_date": daily_practice.update_date,
            "movement_info" : information_movement
        }


def build_information_movement(information_movement: InformationForMovement):
    movement = information_movement.move_bank
    return {
        "move_name": information_movement.move_name,
        "move_picture": information_movement.move_picture,
        "link_video": information_movement.link_video,
        "set_number": information_movement.set_number,
        "number_of_repeat": information_movement.number_of_repeat,
        "suggested_weight": information_movement.suggested_weight,
        "practice_time": information_movement.practice_time,
        "rest_time": information_movement.rest_time,
        "tempo": information_movement.tempo,
        "exercise_intensity": information_movement.exercise_intensity,
        "description_coach": information_movement.description_coach,
        "display_order": information_movement.display_order,
        "alternate_move": information_movement.alternate_move,
        "being_a_superset_or_a_dropset": information_movement.being_a_superset_or_a_dropset,
        "guide_movement" : movement
    }


def build_registration_daily_practice(registration: RegistrationDailyPractice, db: Session):
    information_for_movement = registration.movements_info
    daily_practice = db.query(DailyPractice).filter(DailyPractice.id==information_for_movement.daily_practice_id).first()
    return {
        "done_status" : registration.done_status,
        "done_date" : registration.done_date,
        "actual_weight_used" : registration.actual_weight_used,
        "actual_number_repeat" : registration.actual_number_repeat,
        "difficulty_exercise" : registration.difficulty_exercise,
        "time_practice" : registration.time_practice,
        "description_for_coach" : registration.description_for_coach,
        "problem_during_exercise" : registration.problem_during_exercise,
        "information_for_movement" : information_for_movement,
        "daily_practice" : daily_practice
    }


def build_get_all_information_for_movement(limit: int, offset: int, daily_practice: DailyPractice, db: Session):
    movements = db.query(InformationForMovement).filter(InformationForMovement.daily_practice_id==daily_practice.id)
    total = movements.count()
    items = movements.order_by(InformationForMovement.created_date.desc()).offset(offset).limit(limit).all()
    return {
    "items" : items,
    "total" : total,
    "limit" : limit,
    "offset" : offset,
    "daily_practice" : daily_practice
    }  




# meal plan


def get_meal_plan_for_path(meal_plan_id: int = Path(...),
                           db: Session = Depends(get_db)):

    exists = db.query(MealPlan).filter(MealPlan.id==meal_plan_id).first()
    if not exists:
        raise_not_found("meal plan is not exist")
    return exists


def get_meal_plan(obj_id: int,
                  db: Session):
    
    meal_plan = db.query(MealPlan).filter(MealPlan.id==obj_id).first()
    if not meal_plan:
        raise_not_found("meal plan is not found")
    return meal_plan

def get_meal_plan_daily_for_path(meal_plan_daily_id: int = Path(...),
                                db: Session = Depends(get_db)):

    exists = db.query(MealPlanDaily).filter(MealPlanDaily.id==meal_plan_daily_id).first()
    if not exists:
        raise_not_found("this meal plan daily is not found")
    return exists


def get_food_items_path(food_items: int = Path(...),
                        db: Session = Depends(get_db)):

    exists = db.query(FoodItems).filter(FoodItems.id==food_items).first()
    if not exists:
        raise_not_found("food items is not found")
    return exists


def build_meal_plan_response(meal_plan: MealPlan):
    coach_profile = meal_plan.coach
    athlete_profile = meal_plan.athlete
    return {
        "athlete_id" : meal_plan.athlete_id,
        "coach_id" : meal_plan.coach_id,
        "title" : meal_plan.title,
        "start_date" : meal_plan.start_date,
        "end_date" : meal_plan.end_date,
        "purpose_program" : meal_plan.purpose_program,
        "number_meal" : meal_plan.number_meal,
        "status" : meal_plan.status,
        "target_calories_needed" : meal_plan.target_calories_needed,
        "description" : meal_plan.description,
        "coach_profile" : coach_profile,
        "athlete_profile" : athlete_profile
    }


def build_meal_plan_daily_response(meal_plan_daily: MealPlanDaily):
    meal_plan = meal_plan_daily.meal_plans
    return {
        "meal_plan_id" : meal_plan_daily.meal_plan_id,
        "title" : meal_plan_daily.title,
        "meal" : meal_plan_daily.meal,
        "suggested_hours" : meal_plan_daily.suggested_hours,
        "description" : meal_plan_daily.description,
        "alternative_option" : meal_plan_daily.alternative_option,
        "meal_plan" : meal_plan
    }


def build_meal_plan_daily_responses(offset: int, limit: int, meal_plan: MealPlan, db: Session):

    meal_plan_dailys = db.query(MealPlanDaily).join(MealPlan).filter(MealPlanDaily.meal_plan_id==meal_plan.id)
    total = meal_plan_dailys.count()
    items = meal_plan_dailys.order_by(MealPlanDaily.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset,
        "meal_plan" : meal_plan
    }



def build_food_item_with_meal_plan_daily(food_item: FoodItems):
    meal_plan_daily = food_item.meal_daily
    return {
        "meal_plan_daily_id" : food_item.meal_plan_daily_id, 
        "name_food_item" : food_item.name_food_item,
        "amount" : food_item.amount,
        "unit" : food_item.unit,
        "protein" : food_item.protein,
        "carbohydrates" : food_item.carbohydrates,
        "fat" : food_item.fat,
        "calories_on_record" : food_item.calories_on_record, 
        "description" : food_item.description,
        "alternatives" : food_item.alternatives,
        "meal_plan_daily" : meal_plan_daily
    }


def build_food_item_with_meal_plan_daily_all(limit: int, offset: int, meal_plan_daily: MealPlanDaily, db: Session):

        food_items = db.query(FoodItems).filter(FoodItems.meal_plan_daily_id==meal_plan_daily.id)
        total = food_items.count()
        items = food_items.order_by(FoodItems.id.desc()).offset(offset).limit(limit).all()
        return {
            "items" : items,
            "total" : total,
            "limit" : limit,
            "offset" : offset,
            "meal_plan_daily" : meal_plan_daily
        }



# notification 

def get_notification_for_path(notification_id: int = Path(...),
                              db: Session = Depends(get_db)):

    exists = db.query(NotificationSystem).filter(NotificationSystem.id==notification_id).first()
    if not exists:
        raise_bad_request("this notification is not found")
    return exists




# profile athlete

def get_profile_athlete_or_404(profile_id: int,
                                 db: Session):
    exists = db.query(ProfileAthlete).filter(ProfileAthlete.id==profile_id).first()
    if not exists:
        raise_not_found("profile is not found")
    return exists



def get_athlete_sport_info_for_path(athlete_sport_info_id: int = Path(...),
                           db: Session = Depends(get_db)):
    exists = db.query(AthleteSportsInfo).filter(AthleteSportsInfo.id==athlete_sport_info_id).first()
    if not exists:
        raise_not_found("sport info for this user is not found")
    return exists

def get_athlete_sport_info_or_404(athlete_sport_info_id: int,
                           db: Session):
    exists = db.query(AthleteSportsInfo).filter(AthleteSportsInfo.id==athlete_sport_info_id).first()
    if not exists:
        raise_not_found("sport info for this user is not found")
    return exists



# profile coach


def get_user_for_path(user_id: int = Path(...),
                      db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.id==user_id).first()
    if not exists:
        raise_not_found("user is not exists")
    return exists


def get_profile_coach_for_path(profile_id: int = Path(...),
                               db: Session = Depends(get_db)):
    
    exists = db.query(ProfileCoach).filter(ProfileCoach.id==profile_id).first()
    if not exists:
        raise_not_found("profile coach is not found")
    return exists


def get_specialties_for_path(specialties_id: int = Path(...),
                             db: Session = Depends(get_db)):
    exists = db.query(Specialties).filter(Specialties.id==specialties_id).first()
    if not exists:
        raise_not_found("specialties is not found")
    return exists



# progress process


def get_progress_process_for_path(progress_process_id: int = Path(...),
                                  db: Session = Depends(get_db)):

    exists = db.query(ProgressProcess).filter(ProgressProcess.id==progress_process_id).first()
    if not exists:
        raise_not_found("this not found")
    return exists


def get_progress_picture_for_path(progress_picture_id: int = Path(...),
                         db: Session = Depends(get_db)):

    exists = db.query(ProgressPicture).filter(ProgressPicture.id==progress_picture_id).first()
    if not exists:
        raise_not_found("this not found")
    return exists


def get_progress_process_and_check_coach(progress_picture: ProgressPicture, coach_profile: ProfileCoach, db: Session):
    progress_process = db.query(ProgressProcess).filter(ProgressProcess.id==progress_picture.progress_process_id).first()
    if progress_process.data_recorder_coach != coach_profile.id:
        raise_bad_request("identification error")
    return progress_process


def get_progress_process_and_check_athlete(progress_picture: ProgressPicture, athlete_profile: ProfileAthlete, db: Session):
    progress_process = db.query(ProgressProcess).filter(ProgressProcess.id==progress_picture.progress_process_id).first()
    if progress_process.athlete_id != athlete_profile.id:
        raise_bad_request("identification error")
    return progress_process


def build_progress_process(progress_process: ProgressProcess):
    athlete_profile = progress_process.athlete
    return {
        "athlete_id" : progress_process.athlete_id,
        "date_measurement" : progress_process.date_measurement,
        "data_recorder_coach" : progress_process.data_recorder_coach,
        "weight" : progress_process.weight,
        "fat_percentage" : progress_process.fat_percentage,
        "around_neck" : progress_process.around_neck,
        "around_chest" : progress_process.around_chest,
        "around_arm" : progress_process.around_arm,
        "waist_circumference" : progress_process.waist_circumference,
        "abdominal_circumference" : progress_process.abdominal_circumference,
        "around_thigh" : progress_process.around_thigh,
        "leg_circumference" : progress_process.leg_circumference,
        "description" : progress_process.description,
        "created_date" : progress_process.created_date,
        "update_date" : progress_process.update_date,
        "athlete_profile" : athlete_profile
    }


def build_progress_process_all(profile_athlete: ProfileAthlete, limit: int, offset: int, db: Session):

    progress_process = db.query(ProgressProcess).filter(ProgressProcess.athlete_id==profile_athlete.id)
    coach_to_athlete = db.query(CoachAthleteConnection).filter(CoachAthleteConnection.profile_athlete_id==profile_athlete.id).first()
    profile_coach = coach_to_athlete.coach
    total = progress_process.count()
    items = progress_process.order_by(ProgressProcess.created_date.asc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset,
        "profile_athlete" : profile_athlete,
        "profile_coach" : profile_coach
    }




def build_progress_picture_one(progress_picture: ProgressPicture):
    progress_process = progress_picture.progress
    return {
       "progress_process_id" : progress_picture.progress_process_id,
       "date_registration" : progress_picture.date_registration,
       "front_view" : progress_picture.front_view,
       "side_view" : progress_picture.side_view,
       "back_view" :  progress_picture.back_view,
       "description" : progress_picture.description,
       "data_recorder_coach" : progress_picture.data_recorder_coach,
       "data_recorder_athlete" : progress_picture.data_recorder_coach,
       "progress_process" : progress_process
    }



# user_role 



def get_user_role_or_404(user_id: int, db: Session):
    exists = db.query(UserRole).filter(UserRole.user_id==user_id).first()
    if not exists:
        raise_not_found("user role for user is not found")
    return exists

def build_for_user_role(user_role: UserRole):
    user_name = user_role.users.user_name
    name_role = user_role.roles.name
    return {
        "user_name" : user_name,
        "user_id" : user_role.user_id,
        "role_id" : user_role.role_id,
        "name_role" : name_role
    }
