from sqlalchemy import Column, String, Integer, func, Date, ForeignKey, Boolean, Text, Time
from sqlalchemy.orm import relationship
from sqlite.database import Base




class MealPlan(Base):
    __tablename__="meal_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    athlete_id = Column(Integer, ForeignKey("profile_athlete.id"), nullable=False)
    coach_id = Column(Integer, ForeignKey("profile_coach.id"), nullable=False)
    start_date = Column(Date, default=func.current_date(), nullable=False)
    end_date = Column(Date, nullable=False)
    purpose_program = Column(Text, nullable=False)
    number_meal = Column(Integer, nullable=False)
    target_calories_needed = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Integer, nullable=False)
    
    meal_daily = relationship("MealPlanDaily", back_populates="plan_meal", cascade="all, delete-orphan")
    coach = relationship("ProfileCoach", back_populates="meal_plans")


class MealPlanDaily(Base):
    __tablename__="mael_plan_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    meal_plan_id = Column(Integer, ForeignKey("meal_plan.id"), nullable=False)
    meal = Column(Integer, nullable=False)       # Meals intenum
    suggested_hours = Column(Time, nullable=False)
    description = Column(Text, nullable=True)
    alternative_option = Column(Text, nullable=True)      # گزینه حایگزین 


    plan_meal = relationship("MealPlan", back_populates="meal_daily")
    item_food = relationship("FoodItems", back_populates="meal_daily", cascade="all, delete-orphan")


class FoodItems(Base):
    __tablename__="food_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_plan_daily_id = Column(Integer, ForeignKey("mael_plan_daily.id"), nullable=False)
    name_food_item = Column(String(200), nullable=False)
    amount = Column(String(500), nullable=False)
    unit = Column(String(200), nullable=False)      #  واحد
    Calories_on_record = Column(Integer, nullable=True)
    protein = Column(Boolean, default=False)
    carbohydrates = Column(Boolean, default=False)
    fat = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    alternatives = Column(Text, nullable=True)

    meal_daily = relationship("MealPlanDaily", back_populates="item_food")







    