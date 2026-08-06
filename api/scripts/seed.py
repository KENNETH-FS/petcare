from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Appointment, Clinic, Pet, User

USERS = [
    {"email": "alice@petcare.test", "name": "Alice Cruz", "role": "owner"},
    {"email": "ben@petcare.test", "name": "Ben Santos", "role": "owner"},
    {"email": "carla@petcare.test", "name": "Carla Mendoza", "role": "owner"},
    {"email": "reyes@petcare.test", "name": "Dr. Ana Reyes", "role": "clinic_owner"},
    {"email": "lim@petcare.test", "name": "Dr. Marco Lim", "role": "clinic_owner"},
    {"email": "user100@petcare.test", "name": "Diego Ramos", "role": "owner"},
    {"email": "user101@petcare.test", "name": "Elena Bautista", "role": "owner"},
    {"email": "user102@petcare.test", "name": "Franco Villareal", "role": "owner"},
    {"email": "user103@petcare.test", "name": "Grace Tolentino", "role": "owner"},
    {"email": "user104@petcare.test", "name": "Hector Dizon", "role": "owner"},
    {"email": "user105@petcare.test", "name": "Isabel Navarro", "role": "owner"},
    {"email": "user106@petcare.test", "name": "Jomar Aquino", "role": "owner"},
    {"email": "user107@petcare.test", "name": "Karina Salazar", "role": "owner"},
    {"email": "user108@petcare.test", "name": "Lorenzo Pineda", "role": "owner"},
    {"email": "user109@petcare.test", "name": "Mira Fajardo", "role": "owner"},
    {"email": "user110@petcare.test", "name": "Noel Gatchalian", "role": "owner"},
    {"email": "user111@petcare.test", "name": "Olivia Hernandez", "role": "owner"},
    {"email": "user112@petcare.test", "name": "Paolo Cabrera", "role": "owner"},
    {"email": "user113@petcare.test", "name": "Queenie Robles", "role": "owner"},
    {"email": "user114@petcare.test", "name": "Rafael Ocampo", "role": "owner"},
    {"email": "user115@petcare.test", "name": "Sofia Delgado", "role": "owner"},
    {"email": "user116@petcare.test", "name": "Dr. Teresa Yulo", "role": "clinic_owner"},
    {"email": "user117@petcare.test", "name": "Dr. Ulysses Bong", "role": "clinic_owner"},
    {"email": "user118@petcare.test", "name": "Dr. Vera Almeda", "role": "clinic_owner"},
    {"email": "user119@petcare.test", "name": "Dr. Wilson Ruiz", "role": "clinic_owner"},
]

CLINICS = [
    {
        "owner_email": "reyes@petcare.test",
        "name": "Masbate Animal Clinic",
        "address": "12 Quezon St, Masbate City",
        "phone": "+639171234567",
    },
    {
        "owner_email": "reyes@petcare.test",
        "name": "Reyes Veterinary Center",
        "address": "45 Rizal Ave, Masbate City",
        "phone": "+639171234568",
    },
    {
        "owner_email": "lim@petcare.test",
        "name": "Lim Pet Hospital",
        "address": "88 Bonifacio Rd, Mobo",
        "phone": "+639189876543",
    },
    {
        "owner_email": "lim@petcare.test",
        "name": "Southside Vet Care",
        "address": "7 Mabini St, Milagros",
        "phone": "+639189876544",
    },
    {
        "owner_email": "user116@petcare.test",
        "name": "Yulo Animal Wellness",
        "address": "23 Del Pilar St, Aroroy",
        "phone": "+639201112233",
    },
]

PETS = [
    {
        "owner_email": "alice@petcare.test",
        "name": "Milo",
        "species": "dog",
        "breed": "Aspin",
        "date_of_birth": date(2021, 3, 14),
    },
    {
        "owner_email": "alice@petcare.test",
        "name": "Luna",
        "species": "cat",
        "breed": "Puspin",
        "date_of_birth": date(2022, 7, 2),
    },
    {
        "owner_email": "ben@petcare.test",
        "name": "Rocky",
        "species": "dog",
        "breed": "Labrador Retriever",
        "date_of_birth": date(2019, 11, 30),
    },
    {
        "owner_email": "ben@petcare.test",
        "name": "Bella",
        "species": "dog",
        "breed": None,
        "date_of_birth": None,
    },
    {
        "owner_email": "carla@petcare.test",
        "name": "Simba",
        "species": "cat",
        "breed": "Persian",
        "date_of_birth": date(2023, 1, 20),
    },
]

APPOINTMENTS = [
    {
        "owner_email": "alice@petcare.test",
        "pet_name": "Milo",
        "clinic_name": "Masbate Animal Clinic",
        "days_from_now": 3,
        "status": "scheduled",
        "notes": "Annual vaccination",
    },
    {
        "owner_email": "alice@petcare.test",
        "pet_name": "Luna",
        "clinic_name": "Lim Pet Hospital",
        "days_from_now": 7,
        "status": "scheduled",
        "notes": None,
    },
    {
        "owner_email": "ben@petcare.test",
        "pet_name": "Rocky",
        "clinic_name": "Masbate Animal Clinic",
        "days_from_now": -14,
        "status": "completed",
        "notes": "Limping on left hind leg",
    },
    {
        "owner_email": "ben@petcare.test",
        "pet_name": "Bella",
        "clinic_name": "Southside Vet Care",
        "days_from_now": -5,
        "status": "cancelled",
        "notes": "Owner rescheduled",
    },
    {
        "owner_email": "carla@petcare.test",
        "pet_name": "Simba",
        "clinic_name": "Yulo Animal Wellness",
        "days_from_now": 21,
        "status": "scheduled",
        "notes": "Dental cleaning",
    },
]


def get_user_by_email(db, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def seed_users(db) -> None:
    for entry in USERS:
        existing = get_user_by_email(db, entry["email"])
        if existing is None:
            db.add(User(**entry))
            print("created user:", entry["email"])
        else:
            print("skipped user:", entry["email"])
    db.commit()


def seed_clinics(db) -> None:
    for entry in CLINICS:
        owner = get_user_by_email(db, entry["owner_email"])
        if owner is None:
            print("SKIPPED clinic, owner not found:", entry["owner_email"])
            continue

        existing = db.scalar(
            select(Clinic).where(
                Clinic.owner_id == owner.id,
                Clinic.name == entry["name"],
            )
        )
        if existing is None:
            db.add(
                Clinic(
                    owner_id=owner.id,
                    name=entry["name"],
                    address=entry["address"],
                    phone=entry["phone"],
                )
            )
            print("created clinic:", entry["name"])
        else:
            print("skipped clinic:", entry["name"])
    db.commit()


def seed_pets(db) -> None:
    for entry in PETS:
        owner = get_user_by_email(db, entry["owner_email"])
        if owner is None:
            print("SKIPPED pet, owner not found:", entry["owner_email"])
            continue

        existing = db.scalar(
            select(Pet).where(
                Pet.owner_id == owner.id,
                Pet.name == entry["name"],
            )
        )
        if existing is None:
            db.add(
                Pet(
                    owner_id=owner.id,
                    name=entry["name"],
                    species=entry["species"],
                    breed=entry["breed"],
                    date_of_birth=entry["date_of_birth"],
                )
            )
            print("created pet:", entry["name"])
        else:
            print("skipped pet:", entry["name"])
    db.commit()


def seed_appointments(db) -> None:
    for entry in APPOINTMENTS:
        owner = get_user_by_email(db, entry["owner_email"])
        if owner is None:
            print("SKIPPED appointment, owner not found:", entry["owner_email"])
            continue

        pet = db.scalar(
            select(Pet).where(
                Pet.owner_id == owner.id,
                Pet.name == entry["pet_name"],
            )
        )
        if pet is None:
            print("SKIPPED appointment, pet not found:", entry["pet_name"])
            continue

        clinic = db.scalar(select(Clinic).where(Clinic.name == entry["clinic_name"]))
        if clinic is None:
            print("SKIPPED appointment, clinic not found:", entry["clinic_name"])
            continue

        existing = db.scalar(
            select(Appointment).where(
                Appointment.pet_id == pet.id,
                Appointment.clinic_id == clinic.id,
                Appointment.status == entry["status"],
            )
        )
        if existing is None:
            scheduled_at = datetime.now(timezone.utc) + timedelta(
                days=entry["days_from_now"]
            )
            db.add(
                Appointment(
                    pet_id=pet.id,
                    clinic_id=clinic.id,
                    scheduled_at=scheduled_at,
                    status=entry["status"],
                    notes=entry["notes"],
                )
            )
            print("created appointment:", entry["pet_name"], "@", entry["clinic_name"])
        else:
            print("skipped appointment:", entry["pet_name"], "@", entry["clinic_name"])
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed_users(db)
        seed_clinics(db)
        seed_pets(db)
        seed_appointments(db)


if __name__ == "__main__":
    main()