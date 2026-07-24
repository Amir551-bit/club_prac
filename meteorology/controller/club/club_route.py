from fastapi import Depends, APIRouter, Path, Query
from core.Models.club.club_model import Club, ClubAmenity, ClubGallery
from core.Models.user.user_model import User
from core.security.jwt_auth import get_current_user, check_admin
from sqlite.database import get_db
from core.execptions.execption import raise_bad_request, raise_forbidden, raise_not_found
from sqlalchemy.orm import Session
from core.Schemas.club.club_schemas import *
from core.Models.role.permission import Permission


club_router = APIRouter(prefix="/club", tags=["club"])
club_amenity_router = APIRouter(prefix="/amenity/club", tags=["amenity_club"])
club_gallery_router = APIRouter(prefix="/club/gallery", tags=["club_gallery"])


def get_club_for_path(club_id: int = Path(...),
                      db: Session = Depends(get_db)):
    
    exists = db.query(Club).filter(Club.id==club_id).first()
    if not exists:
        raise_not_found("club is not exists")
    return exists


def get_club_amenity_for_path(amenity_id: int = Path(...),
                              db: Session = Depends(get_db)):
    
    exists = db.query(ClubAmenity).filter(ClubAmenity.id==amenity_id).first()
    if not exists:
        raise_not_found("amenity is not found")
    return exists


def get_club_amenity_or_404(amenity_id: int,
                              db: Session = Depends(get_db)):
    
    exists = db.query(ClubAmenity).filter(ClubAmenity.id==amenity_id).first()
    if not exists:
        raise_not_found("amenity is not found")
    return exists


def get_club_gallery_for_path(gallery_id: int = Path(...),
                              db: Session = Depends(get_db)):

    exists = db.query(ClubGallery).filter(ClubGallery.id==gallery_id).first()
    if not exists:
        raise_not_found("gallery is not found")
    return exists


@club_router.post("/create", response_model=ClubResponseModel)
def create_club(request: CreateInformationClub,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    check_admin(db, current_user, Permission.club_owner)
    club = Club.create(request.club_name, request.club_name_english, request.less_description, request.description, 
        request.logo, request.cover_image, request.contact_number, request.mobile_number, request.address, request.club_rules,
        request.status_club_site, request.map_link, request.social_network_link, request.messenger_link,
        request.geographical_location, request.license_number_legal_information, request.email)
    db.add(club)
    db.commit()
    db.refresh(club)
    return club


@club_router.put("/update/{club_id}", response_model=ClubResponseModel)
def update_club(request: UpdateInformationClub,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user),
                club: Club = Depends(get_club_for_path)):
    
    check_admin(db, current_user, Permission.club_owner)
    club.update(request.club_name, request.club_name_english, request.less_description, request.description, request.logo,
        request.cover_image, request.contact_number, request.mobile_number, request.address, request.club_rules, 
        request.status_club_site, request.map_link, request.social_network_link, request.messenger_link,
        request.geographical_location, request.license_number_legal_information, request.email )
    db.commit()
    db.refresh(club)
    return club


@club_router.delete("/delete/{club_id}")
def delete_club(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user),
                club: Club = Depends(get_club_for_path)):
    
    check_admin(db, current_user, Permission.club_owner)
    name_club = club.club_name
    db.delete(club)
    db.commit()
    return {
        "detail" : f"{name_club} is deleted"
    }



@club_router.get("/get/{club_id}", response_model=ClubResponseModel)
def get_club(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user),
             club: Club = Depends(get_club_for_path)):
    
    return club



@club_amenity_router.post("/create/{club_id}", response_model=AmenityOneResponse)
def create_club_amenity(request: CreateClubAmenity,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        club: Club = Depends(get_club_for_path)):
    
    check_admin(db, current_user, Permission.club_owner)
    amenity = ClubAmenity.create(club.id, request.name, request.is_available, request.description)
    db.add(amenity)
    db.commit()
    db.refresh(amenity)
    return amenity


@club_amenity_router.put("/update/{amenity_id}", response_model=AmenityOneResponse)
def update_club_amenity(request: UpdateClubAmenity,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        amenity: ClubAmenity = Depends(get_club_amenity_for_path)):
    
    check_admin(db, current_user, Permission.club_owner)
    amenity.update(request.name, request.is_available, request.description)
    db.commit()
    db.refresh(amenity)
    return amenity


@club_amenity_router.delete("/delete/{amenity_id}")
def delete_club_amenity(db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        amenity: ClubAmenity = Depends(get_club_amenity_for_path)):
    
    check_admin(db, current_user, Permission.club_owner)
    name_club = amenity.club.club_name_english
    amenity_enum = amenity.name
    db.delete(amenity)
    db.commit()
    return {
        "detail" : f"{amenity_enum} for this {name_club} club is deleted"
    }


@club_amenity_router.get("/get/all/{club_id}", response_model=AmenityResponses)
def get_amenity_club(db: Session = Depends(get_db),
                     limit: int = Query(20, ge=1, le=100),
                     offset: int = Query(0, ge=0),
                     current_user: User = Depends(get_current_user),
                     club: Club = Depends(get_club_for_path)):
    
    amenityes = db.query(ClubAmenity).filter(ClubAmenity.club_id==club.id)
    total = amenityes.count()
    items = amenityes.order_by(ClubAmenity.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }
    


@club_gallery_router.post("/create/{club_id}", response_model=GalleryClubResponse)
def create_gallery_club(request: CreateClubGallery,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user),
                        club: Club = Depends(get_club_for_path)):

    check_admin(db, current_user, Permission.club_owner)
    if request.club_amenity_id is not None:
        get_club_amenity_or_404(request.club_amenity_id, db)
    new = ClubGallery.create(club.id, request.image_url, request.club_amenity_id)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@club_gallery_router.put("/update/{gallery_id}", response_model=GalleryClubResponse)
def update_gallery(request: UpdateClubGallery,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   gallery: ClubGallery = Depends(get_club_gallery_for_path)):

    check_admin(db, current_user, Permission.club_owner)
    gallery.update(db, request.image_url, request.club_amenity_id)
    db.commit()
    db.refresh(gallery)
    return gallery


@club_gallery_router.delete("/delete/{gallery_id}")
def delete_gallery(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   gallery: ClubGallery = Depends(get_club_gallery_for_path)):

    check_admin(db, current_user, Permission.club_owner)
    db.delete(gallery)
    db.commit()
    return {
        "detail" : "gallery deleted successfully"
    }



@club_gallery_router.get("/get/one/{gallery_id}", response_model=GalleryClubResponse)
def get_gallery_one(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   gallery: ClubGallery = Depends(get_club_gallery_for_path)):

    return gallery


@club_gallery_router.get("/get/with/amenity/{amenity_id}", response_model=GalleryClubResponses)
def get_gallery_with_amenity(db: Session = Depends(get_db),
                            limit: int = Query(20, ge=1, le=100),
                            offset: int = Query(0, ge=0),
                            current_user: User = Depends(get_current_user),
                            amenity: ClubAmenity = Depends(get_club_amenity_for_path)):
    
    gallery = db.query(ClubGallery).filter(ClubGallery.club_amenity_id==amenity.id)
    total = gallery.count()
    items = gallery.order_by(ClubGallery.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }


@club_gallery_router.get("/all/{club_id}", response_model=GalleryClubResponses)
def get_all_galler(db: Session = Depends(get_db),
                   limit: int = Query(20, ge=1, le=100),
                   offset: int = Query(0, ge=0),
                   current_user: User = Depends(get_current_user),
                   club: Club = Depends(get_club_for_path)):

    gallery = db.query(ClubGallery).filter(ClubGallery.club_id==club.id)
    total = gallery.count()
    items = gallery.order_by(ClubGallery.id.desc()).offset(offset).limit(limit).all()
    return {
        "items" : items,
        "total" : total,
        "limit" : limit,
        "offset" : offset
    }


    