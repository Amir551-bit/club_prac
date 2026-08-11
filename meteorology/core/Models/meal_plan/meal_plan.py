from sqlalchemy import Column, String, Integer, func, Date, ForeignKey, Boolean, Text, Time, DateTime
from sqlalchemy.orm import relationship
from sqlite.database import Base
from datetime import datetime, date, time
from core.Models.meal_plan.meal_plan_enum import MealStatus, Meals




class MealPlan(Base):
    __tablename__="meal_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    title = Column(String(200), nullable=False)
    start_date = Column(Date, default=func.current_date(), nullable=False)
    end_date = Column(Date, nullable=False)
    purpose_program = Column(Text, nullable=False)
    number_meal = Column(Integer, nullable=False)
    target_calories_needed = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Integer, nullable=False)

    created_date = Column(DateTime, server_default=func.now())
    update_date = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    
    meal_daily = relationship("MealPlanDaily", back_populates="meal_plans", cascade="all, delete-orphan")
    coach = relationship("ProfileCoach", back_populates="meal_plans")
    athlete = relationship("ProfileAthlete", back_populates="meal_plans")



    @classmethod
    def create(cls, athlete_id: int, coach_id: int, title: str, start_date: date, end_date: date, purpose_program: str,
               number_meal: int, status: MealStatus, target_calories_needed: int | None = None, description: str | None = None):

        instance = cls()
        instance.athlete_id = athlete_id
        instance.coach_id = coach_id
        instance.title = title
        instance.start_date = start_date
        instance.end_date = end_date
        instance.purpose_program = purpose_program
        instance.number_meal = number_meal
        instance.status = status.value
        instance.target_calories_needed = target_calories_needed
        instance.description = description
        return instance


    def update(self, title: str | None = None, start_date: date | None = None, end_date: date | None = None,
               purpose_program: str | None = None, number_meal: int | None = None, status: MealStatus | None = None,
               target_calories_needed: int | None = None, description: str | None = None):
        
        self.title = title if title is not None else self.title
        self.start_date = start_date if start_date is not None else self.start_date
        self.end_date = end_date if end_date is not None else self.end_date
        self.purpose_program = purpose_program if purpose_program is not None else self.purpose_program
        self.number_meal = number_meal if number_meal is not None else self.number_meal
        self.target_calories_needed = target_calories_needed if target_calories_needed is not None else self.target_calories_needed
        self.description = description if description is not None else self.description
        if status is not None:
            self.status = status.value

    

class MealPlanDaily(Base):
    __tablename__="mael_plan_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    meal_plan_id = Column(Integer, ForeignKey("meal_plan.id"), nullable=False)
    meal = Column(Integer, nullable=False)       # Meals intenum
    suggested_hours = Column(Time, nullable=False)
    description = Column(Text, nullable=True)
    alternative_option = Column(Text, nullable=True)      # گزینه حایگزین 


    meal_plans = relationship("MealPlan", back_populates="meal_daily")
    item_food = relationship("FoodItems", back_populates="meal_daily", cascade="all, delete-orphan")



    @classmethod
    def create(cls, meal_plan_id: int, title: str, meal: Meals, suggested_hours: time, description: str | None = None,
               alternative_option: str | None = None):
        
        instance = cls()
        instance.meal_plan_id = meal_plan_id
        instance.title = title
        instance.meal = meal.value
        instance.suggested_hours = suggested_hours
        instance.description = description
        instance.alternative_option = alternative_option
        return instance



    def update(self, title: str | None = None, meal: Meals | None = None, suggested_hours: time | None = None, 
               description: str | None = None, alternative_option: str | None = None):

        self.title = title if title is not None else self.title
        self.suggested_hours = suggested_hours if suggested_hours is not None else self.suggested_hours
        self.description = description if description is not None else self.description
        self.alternative_option = alternative_option if alternative_option is not None else self.alternative_option
        if meal is not None:
            self.meal = meal.value
        




class FoodItems(Base):
    __tablename__="food_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_plan_daily_id = Column(Integer, ForeignKey("mael_plan_daily.id"), nullable=False)
    name_food_item = Column(String(200), nullable=False)
    amount = Column(String(500), nullable=False)
    unit = Column(String(200), nullable=False)      #  واحد
    calories_on_record = Column(Integer, nullable=True)
    protein = Column(Boolean, default=False)
    carbohydrates = Column(Boolean, default=False)
    fat = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    alternatives = Column(Text, nullable=True)

    meal_daily = relationship("MealPlanDaily", back_populates="item_food")


    @classmethod
    def create(cls, meal_plan_daily_id: int, name_food_item: str, amount: str, unit: str, protein: bool,
               carbohydrates: bool, fat: bool, calories_on_record: int | None = None, description: str | None = None,
               alternatives: str | None = None):

        instance = cls()
        instance.meal_plan_daily_id = meal_plan_daily_id
        instance.name_food_item = name_food_item
        instance.amount = amount
        instance.unit = unit
        instance.protein = protein
        instance.carbohydrates = carbohydrates
        instance.fat = fat
        instance.calories_on_record = calories_on_record
        instance.description = description
        instance.alternatives = alternatives
        return instance


    def update(self, name_food_item: str | None = None, amount: str | None = None, unit: str | None = None, protein: bool | None = None, 
               carbohydrates: bool | None = None, fat: bool | None = None, calories_on_record: int | None = None, description: str | None = None, 
               alternatives: str | None = None):

        self.name_food_item = name_food_item if name_food_item is not None else self.name_food_item
        self.amount = amount if amount is not None else self.amount
        self.unit = unit if unit is not None else self.unit
        self.calories_on_record = calories_on_record if calories_on_record is not None else self.calories_on_record
        self.protein = protein if protein is not None else self.protein
        self.carbohydrates = carbohydrates if carbohydrates is not None else self.carbohydrates
        self.fat = fat if fat is not None else self.fat
        self.description = description if description is not None else self.description
        self.alternatives = alternatives if alternatives is not None else self.alternatives





    