from fastapi import Depends, APIRouter, Path, Query
from sqlalchemy.orm import Session
from core.Models.meal_plan.meal_plan import MealPlan, MealPlanDaily, FoodItems
from core.security.jwt_auth import get_current_user, check_admin
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.profile.profile_coach_model import ProfileCoach
from sqlite.database import get_db
from core.Schemas.meal_plan.meal_plan_schemas import *
from core.Models.user.user_model import User
from core.Models.role.permission import Permission
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.user_role.user_role_model import UserRole
from core.Models.notification_system.notification_system_model import NotificationSystem
from controller.service.services import (get_profile_coach, get_profile_athlete_with_user_id, get_profile_athlete, get_profile_athlete_for_path,
                                         accepted_coach_to_athlete, get_meal_plan, get_meal_plan_for_path, get_meal_plan_daily_for_path,
                                         get_food_items_path, build_meal_plan_daily_response, build_meal_plan_response,
                                         build_meal_plan_daily_responses, build_food_item_with_meal_plan_daily,
                                         build_food_item_with_meal_plan_daily_all, build_get_all_meal_plan)
from sqlite.redis_client import redis_client
from controller.service.db_helper import (commit, update, delete, create_or_update_to_api_redis, 
                                          commit_notification, get_for_redis)


meal_plan_router = APIRouter(prefix="/meal/plan", tags=["meal_plan"])
meal_plan_daily_router = APIRouter(prefix="/meal/plan/daily", tags=["meal_plan_daily"])
food_item_router = APIRouter(prefix="/food/items", tags=["food_item"])
 
 
@meal_plan_router.post("/create/{profile_id}", response_model=MealPlanResponse)
def create_meal_plan(request: CreateMealPlan,
                     requests: CreateNotification,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
    new_meal_plan = MealPlan.create(athlete_profile.id, coach_profile.id, request.title, request.start_date, request.end_date, request.purpose_program,
                                    request.number_meal, request.status, request.target_calories_needed, request.description)
    create_or_update_to_api_redis(f"create_meal_plan:{current_user.id}:{athlete_profile.id}")
    commit(new_meal_plan, db)
    new_notification = NotificationSystem.create(athlete_profile.id, requests.type, requests.title, requests.text,
                                                 requests.read_status)
    commit_notification(new_notification, db)
    return new_meal_plan



@meal_plan_router.put("/update/{meal_plan_id}", response_model=MealPlanResponse)
def update_meal_plan(request: UpdateMealPlan,
                     requests: CreateNotification,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
    meal_plan.update(request.title, request.start_date, request.end_date, request.purpose_program, request.number_meal, request.status,
                     request.target_calories_needed, request.description)
    update(meal_plan, db)
    athlete_profile_id = meal_plan.athlete_id
    
    for key in redis_client.keys(f"get_all_meal_plan:{current_user.id}:*:{athlete_profile_id}"):
        redis_client.delete(key)
        
    create_or_update_to_api_redis(f"update_meal_plan{current_user.id}:{meal_plan.id}")
    new_notification = NotificationSystem.create(meal_plan.athlete_id, requests.type, requests.title, requests.text,
                                                 requests.read_status)
    commit_notification(new_notification, db)
    return meal_plan



@meal_plan_router.delete("/delete/{meal_plan_id}")
def delete_meal_plan(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
    exists_meal_plan_daily = db.query(MealPlanDaily).filter(MealPlanDaily.meal_plan_id==meal_plan.id).first()
    if exists_meal_plan_daily:
        raise_bad_request("meal plan has meal plan daily")
    delete(meal_plan, db)
    athlete_profile_id = meal_plan.athlete_id
    
    for key in redis_client.keys(f"get_all_meal_plan:{current_user.id}:*:{athlete_profile_id}"):
        redis_client.delete(key)
        
    return {
        "detail" : "deleted successfully"
    }                                       



@meal_plan_router.delete("/delete/with/all/meal/plan/daily/{meal_plan_id}")
def delete_meal_plan_with_all_meal_plan_daily(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
        
    db.query(MealPlanDaily).filter(MealPlanDaily.meal_plan_id == meal_plan.id).delete()
    
    delete(meal_plan, db)
    athlete_profile_id = meal_plan.athlete_id
    
    for key in redis_client.keys(f"get_all_meal_plan:{current_user.id}:*:{athlete_profile_id}"):
        redis_client.delete(key)
        
    return {
        "detail" : "deleted successfully"
    }   


@meal_plan_router.get("/get/one/{meal_plan_id}")
def get_one_meal_plan(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        return build_meal_plan_response(meal_plan)
    if user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if coach_profile.id != meal_plan.coach_id:
            raise_bad_request("this meal plan is not for you")
        return build_meal_plan_response(meal_plan)
    if user_role.role_id == 5:
        profile_athlete = get_profile_athlete(current_user.id, db)
        if profile_athlete.id != meal_plan.athlete_id:
            raise_bad_request("this meal plan is not for you")
        return build_meal_plan_response(meal_plan)


@meal_plan_router.get("/get/all/{profile_id}", response_model=MealPlanResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
    elif user_role.role_id == 5:
        profile_athlete = get_profile_athlete_with_user_id(current_user.id, db)
        if profile_athlete.id != athlete_profile.id:
            raise_bad_request("this is not for you")
    else:
        raise_bad_request("you have not permission")

    return get_for_redis(f"get_all_meal_plan:{current_user.id}:{limit}:{offset}:{athlete_profile.id}", MealPlanResponses, 
                  lambda: build_get_all_meal_plan(limit, offset, athlete_profile, db))



@meal_plan_daily_router.post("/create/{meal_plan_id}", response_model=MealPlanDailyResponse)
def create_plan_daily(request: CreateMealPlanDaily,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user),
                      meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal is not for you")
    create_or_update_to_api_redis(f"create_plan_daily_meal:{current_user.id}:{meal_plan.id}")
    new = MealPlanDaily.create(meal_plan.id, request.title, request.meal, request.suggested_hours, request.description,
                               request.alternative_option)
    commit(new, db)
    return new



@meal_plan_daily_router.put("/update/{meal_plan_daily_id}", response_model=MealPlanDailyResponse)
def update_meal_plan_daily(request: UpdateMealPlanDaily,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           meal_plan_daily: MealPlanDaily = Depends(get_meal_plan_daily_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
    create_or_update_to_api_redis(f"create_plan_daily_meal:{current_user.id}:{meal_plan_daily.id}")
    meal_plan_daily.update(request.title, request.meal, request.suggested_hours, request.description,
                           request.alternative_option)
    update(meal_plan_daily, db)
    for key in redis_client.keys(f"get_all_meal_plan_daily:{current_user.id}:{meal_plan.id}:*"):
        redis_client.delete(key)
    return meal_plan_daily



@meal_plan_daily_router.delete("/delete/{meal_plan_daily_id}")
def delete_meal_plan_daily(db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           meal_plan_daily: MealPlanDaily = Depends(get_meal_plan_daily_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
    delete(meal_plan_daily, db)
    for key in redis_client.keys(f"get_all_meal_plan_daily:{current_user.id}:{meal_plan.id}:*"):
        redis_client.delete(key)
    return {
        "detail" : "deleted successfully"
    }


@meal_plan_daily_router.get("/get/one/{meal_plan_daily_id}")
def get_meal_plan_daily_one(db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            meal_plan_daily: MealPlanDaily = Depends(get_meal_plan_daily_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id == current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        return build_meal_plan_daily_response(meal_plan_daily)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if meal_plan_daily.meal_plans.coach_id != coach_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_meal_plan_daily_response(meal_plan_daily)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if meal_plan_daily.meal_plans.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_meal_plan_daily_response(meal_plan_daily)
    else:
        raise_bad_request("you have not access")
    

@meal_plan_daily_router.get("/get/all/{meal_plan_id}", response_model=MealPlanDailyResponses)
def get_all_meal_plan_daily(limit: int = Query(20, ge=1, le=100),
                            offset: int = Query(0, ge=0),
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id in (1, 2, 3):
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if meal_plan.coach_id != coach_profile.id:
                raise_bad_request("this meal plan is not for you")

    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if meal_plan.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")

    else:
        raise_bad_request("you have not access")
    return get_for_redis(f"get_all_meal_plan_daily:{current_user.id}:{meal_plan.id}:{limit}:{offset}", MealPlanDailyResponses,
                  lambda: build_meal_plan_daily_responses(offset, limit, meal_plan, db))


@food_item_router.post("/create/{meal_plan_daily_id}", response_model=FoodItemsResponse)
def create_food_item(request: CreateFoodItems,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan_daily: MealPlanDaily = Depends(get_meal_plan_daily_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
    create_or_update_to_api_redis(f"create_food_item:{current_user.id}:{meal_plan_daily.id}")
    new = FoodItems.create(meal_plan_daily.id, request.name_food_item, request.amount,
                           request.unit, request.protein, request.carbohydrates, request.fat, request.calories_on_record,
                           request.description, request.alternatives,)
    commit(new, db)
    return new


@food_item_router.put("/update/{food_items}", response_model=FoodItemsResponse)
def update_food_item(request: UpdateFoodItems,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     food_item: FoodItems = Depends(get_food_items_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    plan_daily = db.query(MealPlanDaily).filter(MealPlanDaily.id==food_item.meal_plan_daily_id).first()
    meal_plan = get_meal_plan(plan_daily.meal_plan_id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not foy you")
    create_or_update_to_api_redis(f"update_food_item:{current_user.id}:{food_item.id}")
    food_item.update(request.name_food_item, request.amount, request.unit, request.protein, request.carbohydrates, 
                     request.fat,request.calories_on_record, request.description,request.alternatives)
    update(food_item, db)
    for key in redis_client.keys(f"get_all_food_items:{current_user.id}:{plan_daily.id}:*"):
        redis_client.delete(key)
    return food_item



@food_item_router.get("/get/one/{food_items}")
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            food_item: FoodItems = Depends(get_food_items_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        daily_meal = db.query(MealPlanDaily).filter(MealPlanDaily.id==food_item.meal_plan_daily_id).first()
        meal = get_meal_plan(daily_meal.meal_plan_id, db)
        if meal.coach_id != coach_profile.id:
            raise_bad_request("this meal plan is not for you")
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        daily_meal = db.query(MealPlanDaily).filter(MealPlanDaily.id==food_item.meal_plan_daily_id).first()
        meal = get_meal_plan(daily_meal.meal_plan_id, db)
        if meal.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")
    else:
        raise_bad_request("you have not access")
    return build_food_item_with_meal_plan_daily(food_item)


@food_item_router.get("/get/all/{meal_plan_daily_id}", response_model=FoodItemsResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            meal_plan_daily: MealPlanDaily = Depends(get_meal_plan_daily_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        pass
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
        if meal_plan.coach_id != coach_profile.id:
            raise_bad_request("this meal plan is not for you")
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
        if meal_plan.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")
    else:
        raise_bad_request("you have not access")
    return get_for_redis(f"get_all_food_items:{current_user.id}:{meal_plan_daily.id}:{limit}:{offset}", FoodItemsResponses,
                  lambda: build_food_item_with_meal_plan_daily_all(limit, offset, meal_plan_daily, db))
    
    