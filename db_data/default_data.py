import time

from sqlalchemy import delete
from database import SessionLocal
from models import *

db = SessionLocal()


def db_default_data():
    time.sleep(5)

    # Table shape_types

    if db.query(ShapeTypes).count() != 3:
        db.execute(delete(ShapeTypes))
        print("'shape_types' | Filled")
        shape_types = [ShapeTypes(type="Polygon"),
                       ShapeTypes(type="Circle"),
                       ShapeTypes(type="Point")]
        db.add_all(shape_types)
        db.commit()
    else:
        print("'shape_types' | Skipped")

    # Table slot_type

    if db.query(SlotType).count() != 4:
        print("'slot_type' | Filled")
        db.execute(delete(SlotType))
        slot_types = [SlotType(type="Open"),
                      SlotType(type="Closed"),
                      SlotType(type="Busy"),
                      SlotType(type="Assigned")]
        db.add_all(slot_types)
        db.commit()
    else:
        print("'slot_type' | Skipped")

    # Table roles

    if db.query(Roles).count() != 4:
        print("'roles' | Filled")
        db.execute(delete(Roles))
        roles = [Roles(role_name="Assault", role_description="Assault"),
                 Roles(role_name="Support", role_description="Support"),
                 Roles(role_name="Scout", role_description="Scout"),
                 Roles(role_name="Sniper", role_description="Sniper")]
        db.add_all(roles)
        db.commit()
    else:
        print("'roles' | Skipped")

    # Table game_status

    if db.query(GameStatus).count() != 6:
        print("'game_status' | Filled")
        db.execute(delete(GameStatus))
        game_status = [GameStatus(id=1, status_name="New"),
                       GameStatus(id=2, status_name="Ready"),
                       GameStatus(id=3, status_name="Active"),
                       GameStatus(id=4, status_name="Suspended"),
                       GameStatus(id=5, status_name="Terminated"),
                       GameStatus(id=6, status_name="Ended")]
        db.add_all(game_status)
        db.commit()
    else:
        print("'game_status' | Skipped")

    # Table events

    if db.query(Events).count() != 9:
        print("'events' | Filled")
        db.execute(delete(Events))
        events = [Events(id=1, event_name="New User Account"),
                  Events(id=2, event_name="Deactivated"),
                  Events(id=3, event_name="Activated"),
                  Events(id=4, event_name="Log In"),
                  Events(id=5, event_name="Login Failed"),
                  Events(id=6, event_name="Password Change"),
                  Events(id=7, event_name="User Edit"),
                  Events(id=8, event_name="New User Account"),
                  Events(id=9, event_name="Confirm email")]

        db.add_all(events)
        db.commit()
    else:
        print("'events' | Skipped")
