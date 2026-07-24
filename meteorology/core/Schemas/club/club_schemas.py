from pydantic import BaseModel, ConfigDict
from core.Models.club.club_enum import Amenity



class CreateInformationClub(BaseModel):
    club_name: str
    club_name_english: str
    less_description: str
    description: str
    logo: str 
    cover_image: str
    contact_number: str
    mobile_number: str 
    email: str | None = None 
    address: str
    geographical_location: str | None = None 
    map_link: str  
    social_network_link: str
    messenger_link: str 
    license_number_legal_information: str | None = None 
    club_rules: str
    status_club_site: bool


class UpdateInformationClub(BaseModel):
    club_name: str | None = None 
    club_name_english: str | None = None 
    less_description: str | None = None 
    description: str | None = None 
    logo: str | None = None 
    cover_image: str | None = None 
    contact_number: str | None = None 
    mobile_number: str | None = None 
    email: str | None = None 
    address: str | None = None 
    geographical_location: str | None = None 
    map_link: str | None = None 
    social_network_link: str | None = None 
    messenger_link: str | None = None 
    license_number_legal_information: str | None = None 
    club_rules: str | None = None 
    status_club_site: bool | None = None 


class ClubResponseModel(BaseModel):
    club_name: str
    club_name_english: str
    less_description: str
    description: str
    logo: str 
    cover_image: str
    contact_number: str
    mobile_number: str 
    email: str | None = None 
    address: str
    geographical_location: str | None = None 
    map_link: str  
    social_network_link: str | None = None
    messenger_link: str 
    license_number_legal_information: str | None = None 
    club_rules: str
    status_club_site: bool

    model_config = ConfigDict(from_attributes=True)



class CreateClubAmenity(BaseModel):
    name: Amenity
    is_available: bool 
    description: str | None = None 


class UpdateClubAmenity(BaseModel):
    name: Amenity | None = None
    is_available: bool | None = None
    description: str | None = None 


class AmenityReponse(BaseModel):
    club: ClubResponseModel
    name: Amenity
    is_available: bool 
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AmenityOneResponse(BaseModel):
    name: Amenity
    is_available: bool 
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AmenityResponses(BaseModel):
    items: list[AmenityOneResponse]
    total: int
    limit: int
    offset: int



class CreateClubGallery(BaseModel):
    club_id: int
    image_url: str 
    club_amenity_id: int | None = None 



# Gallery


class CreateClubGallery(BaseModel):
    image_url: str
    club_amenity_id: int | None = None



class UpdateClubGallery(BaseModel):
    image_url: str | None = None
    club_amenity_id: int | None = None



class GalleryClubResponse(BaseModel):
    image_url: str
    club_amenity_id: int | None = None

    model_config = ConfigDict(from_attributes=True)



class GalleryClubResponses(BaseModel):
    items: list[GalleryClubResponse]
    total: int
    limit: int
    offset: int