from fastapi import Depends, APIRouter, Path, Query
from sqlalchemy.orm import Session
from core.Models.meal_plan.meal_plan import MealPlan, MealPlanDaily, FoodItems
from core.security.jwt_auth import get_current_user, check_admin
from controller.exercise_program_route.exercise_program_route import (accepted_coach_to_athlete, get_profile_athlete, get_profile_coach,
                                                                      get_profile_athlete_for_path, get_profile_athlete_with_user_id)
from core.Models.profile.profile_athlete_model import ProfileAthlete
from core.Models.profile.profile_coach_model import ProfileCoach
from sqlite.database import get_db
from core.Schemas.meal_plan.meal_plan_schemas import *
from core.Models.user.user_model import User
from core.Models.role.permission import Permission
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from core.Models.user_role.user_role_model import UserRole


meal_plan_router = APIRouter(prefix="/meal/plan", tags=["meal_plan"])
meal_plan_daily_router = APIRouter(prefix="/meal/plan/daily", tags=["meal_plan_daily"])
food_item_router = APIRouter(prefix="/food/items", tags=["food_item"])


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


@meal_plan_router.post("/create/{profile_id}", response_model=MealPlanResponse)
def create_meal_plan(request: CreateMealPlan,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     athlete_profile: ProfileAthlete = Depends(get_profile_athlete_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    accepted_coach_to_athlete(coach_profile.id, athlete_profile.id, db)
    new_meal_plan = MealPlan.create(athlete_profile.id, coach_profile.id, request.title, request.start_date, request.end_date, request.purpose_program,
                                    request.number_meal, request.status, request.target_calories_needed, request.description)
    db.add(new_meal_plan)
    db.commit()
    db.refresh(new_meal_plan)
    return new_meal_plan



@meal_plan_router.put("/update/{meal_plan_id}", response_model=MealPlanResponse)
def update_meal_plan(request: UpdateMealPlan,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
    meal_plan.update(request.title, request.start_date, request.end_date, request.purpose_program, request.number_meal, request.status,
                     request.target_calories_needed, request.description)
    db.commit()
    db.refresh(meal_plan)
    return meal_plan



@meal_plan_router.delete("/delete/{meal_plan_id}")
def delete_meal_plan(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal plan is not for you")
    db.delete(meal_plan)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }                                       



@meal_plan_router.get("/get/one/{meal_plan_id}")
def get_one_meal_plan(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
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





@meal_plan_daily_router.post("/create/{meal_plan_id}", response_model=MealPlanDailyResponse)
def create_plan_daily(request: CreateMealPlanDaily,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user),
                      meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    check_admin(db, current_user, Permission.coach)
    coach_profile = get_profile_coach(current_user.id, db)
    if meal_plan.coach_id != coach_profile.id:
        raise_bad_request("this meal is not for you")
    new = MealPlanDaily.create(meal_plan.id, request.title, request.meal, request.suggested_hours, request.description,
                               request.alternative_option)
    db.add(new)
    db.commit()
    db.refresh(new)
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
    meal_plan_daily.update(request.title, request.meal, request.suggested_hours, request.description,
                           request.alternative_option)
    db.commit()
    db.refresh(meal_plan_daily)
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
    db.delete(meal_plan_daily)
    db.commit()
    return {
        "detail" : "deleted successfully"
    }


@meal_plan_daily_router.get("/get/one/{meal_plan_daily_id}")
def get_meal_plan_daily_one(db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            meal_plan_daily: MealPlanDaily = Depends(get_meal_plan_daily_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        return build_meal_plan_daily_response(meal_plan_daily)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
        if meal_plan.coach_id != coach_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_meal_plan_daily_response(meal_plan_daily)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
        if meal_plan.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_meal_plan_daily_response(meal_plan_daily)
    else:
        return {
            "detail" : "you have not access"
        }


@meal_plan_daily_router.get("/get/all/{meal_plan_id}")
def get_all_meal_plan_daily(limit: int = Query(20, ge=1, le=100),
                            offset: int = Query(0, ge=0),
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user),
                            meal_plan: MealPlan = Depends(get_meal_plan_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        return build_meal_plan_daily_responses(offset, limit, meal_plan, db)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        if meal_plan.coach_id != coach_profile.id:
                raise_bad_request("this meal plan is not for you")
        return build_meal_plan_daily_responses(offset, limit, meal_plan, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        if meal_plan.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_meal_plan_daily_responses(offset, limit, meal_plan, db)
    else:
        return {
            "detail" : "you have not access"
        }



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
    new = FoodItems.create(meal_plan_daily.id, request.name_food_item, request.amount,
                           request.unit, request.protein, request.carbohydrates, request.fat, request.calories_on_record,
                           request.description, request.alternatives,)
    db.add(new)
    db.commit()
    db.refresh(new)
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
    food_item.update(request.name_food_item, request.amount, request.unit, request.protein, request.carbohydrates, 
                     request.fat,request.calories_on_record, request.description,request.alternatives)
    db.commit()
    db.refresh(food_item)
    return food_item



@food_item_router.get("/get/one/{food_items}")
def get_one(db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            food_item: FoodItems = Depends(get_food_items_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        return build_food_item_with_meal_plan_daily(food_item)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        daily_meal = db.query(MealPlanDaily).filter(MealPlanDaily.id==food_item.meal_plan_daily_id).first()
        meal = get_meal_plan(daily_meal.meal_plan_id, db)
        if meal.coach_id != coach_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_food_item_with_meal_plan_daily(food_item)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        daily_meal = db.query(MealPlanDaily).filter(MealPlanDaily.id==food_item.meal_plan_daily_id).first()
        meal = get_meal_plan(daily_meal.meal_plan_id, db)
        if meal.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_food_item_with_meal_plan_daily(food_item)
    else:
        return {
            "detail" : "you have not access"
                }


@food_item_router.get("/get/all/{meal_plan_daily_id}", response_model=FoodItemsResponses)
def get_all(limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user),
            meal_plan_daily: MealPlanDaily = Depends(get_meal_plan_daily_for_path)):

    user_role = db.query(UserRole).filter(UserRole.user_id==current_user.id).first()
    if user_role.role_id == 3:
        return build_food_item_with_meal_plan_daily_all(limit, offset, meal_plan_daily, db)
    elif user_role.role_id == 4:
        coach_profile = get_profile_coach(current_user.id, db)
        meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
        if meal_plan.coach_id != coach_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_food_item_with_meal_plan_daily_all(limit, offset, meal_plan_daily, db)
    elif user_role.role_id == 5:
        athlete_profile = get_profile_athlete_with_user_id(current_user.id, db)
        meal_plan = get_meal_plan(meal_plan_daily.meal_plan_id, db)
        if meal_plan.athlete_id != athlete_profile.id:
            raise_bad_request("this meal plan is not for you")
        return build_food_item_with_meal_plan_daily_all(limit, offset, meal_plan_daily, db)
    else:
        return {
            "detail" : "you have not access"
                }
    
    