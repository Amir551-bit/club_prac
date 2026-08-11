from pydantic import BaseModel, ConfigDict
from core.Models.meal_plan.meal_plan_enum import MealStatus, Meals
from datetime import date, datetime, time
from core.Models.notification_system.notification_system_enum import NotificationsRequiredEnum
from core.Schemas.profile.profile_athlete import ProfileAthleteResponse

# Meal_Plan


class CreateMealPlan(BaseModel):

    title: str
    start_date: date
    end_date: date
    purpose_program: str
    number_meal: int
    status: MealStatus
    target_calories_needed: int | None = None
    description: str | None = None




class UpdateMealPlan(BaseModel):

    title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    purpose_program: str | None = None
    number_meal: int | None = None
    status: MealStatus | None = None
    target_calories_needed: int | None = None
    description: str | None = None



class MealPlanResponse(BaseModel):
    
    athlete_id: int
    coach_id: int
    title: str
    start_date: date
    end_date: date
    purpose_program: str
    number_meal: int
    status: MealStatus
    target_calories_needed: int | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MealPlanResponses(BaseModel):
    items: list[MealPlanResponse]
    total: int
    limit: int
    offset: int
    athlete_profile: ProfileAthleteResponse



# Meal_Plan_Daily


class CreateMealPlanDaily(BaseModel):

    title: str
    meal: Meals
    suggested_hours: time
    description: str | None = None
    alternative_option: str | None = None



class UpdateMealPlanDaily(BaseModel):

    meal_plan_id: int | None = None
    title: str | None = None
    meal: Meals | None = None
    suggested_hours: time | None = None
    description: str | None = None
    alternative_option: str | None = None




class MealPlanDailyResponse(BaseModel):

    meal_plan_id: int
    title: str
    meal: Meals
    suggested_hours: time
    description: str | None = None
    alternative_option: str | None = None

    model_config = ConfigDict(from_attributes=True)



class MealPlanDailyResponses(BaseModel):

    items: list[MealPlanDailyResponse]
    total: int
    limit: int
    offset: int
    meal_plan: MealPlanResponse


# Food_Items

class CreateFoodItems(BaseModel):

    name_food_item: str
    amount: str
    unit: str
    protein: bool
    carbohydrates: bool
    fat: bool
    calories_on_record: int | None = None
    description: str | None = None
    alternatives: str | None = None




class UpdateFoodItems(BaseModel):
    
    name_food_item: str | None = None
    amount: str | None = None
    unit: str | None = None
    protein: bool | None = None
    carbohydrates: bool | None = None
    fat: bool | None = None
    calories_on_record: int | None = None
    description: str | None = None
    alternatives: str | None = None





class FoodItemsResponse(BaseModel):

    meal_plan_daily_id: int
    name_food_item: str
    amount: str
    unit: str
    protein: bool
    carbohydrates: bool
    fat: bool
    calories_on_record: int | None = None
    description: str | None = None
    alternatives: str | None = None


    model_config = ConfigDict(from_attributes=True)


class FoodItemsResponses(BaseModel):

    items : list[FoodItemsResponse]
    total : int
    limit : int
    offset : int
    meal_plan_daily : MealPlanDailyResponse



class CreateNotification(BaseModel):
    
    title: str
    text: str
    type: NotificationsRequiredEnum
    read_status: bool = False
