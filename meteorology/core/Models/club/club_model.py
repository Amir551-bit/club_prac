from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlite.database import Base
from core.Models.club.club_enum import Amenity
from sqlalchemy.orm import Session
from core.execptions.execption import raise_not_found


class Club(Base):
    __tablename__ = "club"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_name = Column(String(200), nullable=False)
    club_name_english = Column(String(200), nullable=False)
    less_description = Column(String(400), nullable=False)
    description = Column(Text, nullable=False)
    logo = Column(String(300), nullable=False)
    cover_image = Column(String(300), nullable=False)
    contact_number = Column(String(20), nullable=False)   # شماره تماس 
    mobile_number = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(String(500), nullable=False)
    geographical_location = Column(String(300), nullable=True)    # موقعیت جغرافیایی
    map_link = Column(String(200), nullable=False)
    social_network_link = Column(String(750), nullable=True)
    messenger_link = Column(String(500), nullable=False)
    license_number_legal_information = Column(String(300), nullable=True)
    club_rules = Column(Text, nullable=False)
    status_club_site = Column(Boolean, nullable=False)

    # اصلاح نام روابط برای هماهنگی کامل
    club_facilities = relationship("ClubAmenity", back_populates="club", cascade="all, delete-orphan")
    club_gallery = relationship("ClubGallery", back_populates="club", cascade="all, delete-orphan")


    @classmethod
    def create(cls, club_name: str, club_name_english: str, less_description: str, description: str, logo: str,
    cover_image: str, contact_number: str , mobile_number: str, address: str, club_rules: str, status_club_site: bool,
    map_link: str, social_network_link: str, messenger_link: str, geographical_location: str | None = None,
    license_number_legal_information: str | None = None, email: str | None = None):
        
        instance = cls()
        instance.club_name = club_name
        instance.club_name_english = club_name_english
        instance.less_description = less_description
        instance.description = description
        instance.logo = logo
        instance.cover_image = cover_image
        instance.contact_number = contact_number
        instance.mobile_number = mobile_number
        instance.address = address
        instance.club_rules = club_rules
        instance.status_club_site = status_club_site
        instance.map_link = map_link
        instance.social_network_link = social_network_link
        instance.messenger_link = messenger_link
        instance.geographical_location = geographical_location
        instance.license_number_legal_information = license_number_legal_information
        instance.email = email
        return instance
    

    def update(self, club_name: str | None = None, club_name_english: str | None = None, less_description: str | None = None,
                description: str | None = None, logo: str | None = None, cover_image: str | None = None,
                contact_number: str | None = None, mobile_number: str | None = None, address: str | None = None,
                club_rules: str | None = None, status_club_site: bool | None = None, map_link: str | None = None, 
                social_network_link: str | None = None, messenger_link: str | None = None, geographical_location: str | None = None,
                license_number_legal_information: str | None = None, email: str | None = None):
        
        self.club_name = club_name if club_name is not None else self.club_name
        self.club_name_english = club_name_english if club_name_english is not None else self.club_name_english
        self.less_description = less_description if less_description is not None else self.less_description
        self.description = description if description is not None else self.description
        self.logo = logo if logo is not None else self.logo
        self.cover_image = cover_image if cover_image is not None else self.cover_image
        self.contact_number = contact_number if contact_number is not None else self.contact_number
        self.mobile_number = mobile_number if mobile_number is not None else self.mobile_number
        self.address = address if address is not None else self.address
        self.club_rules = club_rules if club_rules is not None else self.club_rules
        self.status_club_site = status_club_site if status_club_site is not None else self.status_club_site
        self.map_link = map_link if map_link is not None else self.map_link
        self.social_network_link = social_network_link if social_network_link is not None else social_network_link
        self.messenger_link = messenger_link if messenger_link is not None else self.messenger_link
        self.geographical_location = geographical_location if geographical_location is not None else self.geographical_location
        self.license_number_legal_information = license_number_legal_information if license_number_legal_information is not None else self.license_number_legal_information
        self.email = email if email is not None else self.email


class ClubAmenity(Base):
    __tablename__ = "club_amenities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("club.id"), nullable=False)
    name = Column(Integer, nullable=False)  # عدد مربوط به Amenity Enum اینجا ذخیره می‌شود
    is_available = Column(Boolean, default=True, nullable=False)
    description = Column(String(300), nullable=True)

    # اصلاح back_populates جهت اتصال دقیق به کلاس Club
    club = relationship("Club", back_populates="club_facilities")
    club_gallery = relationship("ClubGallery", back_populates="club_amenity", cascade="all, delete-orphan")

    
    @classmethod
    def create(cls, club_id: int, name: Amenity, is_available: bool, description: str | None = None):
        instance = cls()
        instance.club_id = club_id
        instance.name = name.value
        instance.is_available = is_available
        instance.description = description
        return instance
    
    def update(self, name: Amenity | None = None, is_available: bool | None = None, description: str | None = None):
        self.name = name.value if name is not None else self.name
        self.is_available = is_available if is_available is not None else self.is_available
        self.description = description if description is not None else self.description


class ClubGallery(Base):
    __tablename__ = "club_gallery"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("club.id"), nullable=False)
    image_url = Column(String(250), nullable=False)
    club_amenity_id = Column(Integer, ForeignKey("club_amenities.id"), nullable=True)


    club = relationship("Club", back_populates="club_gallery")
    club_amenity = relationship("ClubAmenity", back_populates="club_gallery")


    @classmethod
    def create(cls, club_id: int, image_url: str, club_amenity_id: int | None = None):

        instance = cls()
        instance.club_id = club_id
        instance.image_url = image_url
        instance.club_amenity_id = club_amenity_id
        return instance


    def update(self, db: Session, image_url: str | None = None, club_amenity_id: int | None = None):

        self.image_url = image_url if image_url is not None else self.image_url
        if club_amenity_id is not None:
            if not db.query(ClubAmenity).filter(ClubAmenity.id==club_amenity_id).first():
                    raise_not_found("amenity is not found")
            self.club_amenity_id = club_amenity_id

        