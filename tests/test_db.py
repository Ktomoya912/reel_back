from sqlalchemy.orm import Session

import api.cruds.user as user_crud
from api import schemas


def test_make_user(db_session: Session):
    user = user_crud.create_user(
        db_session,
        schemas.UserCreate.parse_obj(
            {
                "username": "username",
                "password": "password",
                "email": "sample@kochi.com",
                "user_type": "g",
                "birthday": "2000-01-01",
            }
        ),
    )
    assert user.username == "username"
    assert user.password != "password", user.password
