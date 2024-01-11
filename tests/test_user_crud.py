from sqlalchemy.orm import Session

import api.cruds.user as user_crud
from api import schemas


class TestUser:
    def test_make_user(self, db_session: Session):
        user = user_crud.create_user(
            db_session,
            schemas.UserCreate.model_validate(
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

    def test_read_user(self, db_session: Session):
        user = user_crud.get_user(db_session, 1)
        assert user.username == "username"

    def test_read_user_by_username(self, db_session: Session):
        user = user_crud.get_user_by_username(db_session, "username")
        assert user.username == "username"

    def test_authenticate_user(self, db_session: Session):
        user = user_crud.authenticate_user(
            db_session, username="username", password="password"
        )
        assert user.username == "username"

    def test_user_password_change(self, db_session: Session):
        user = user_crud.get_user_by_username(db_session, "username")
        user = user_crud.update_user_password(
            db_session,
            user=user,
            new_password=schemas.UserPasswordChange.model_validate(
                {"password": "new_password"}
            ),
        )
        assert user.password != "new_password", user.password
        assert user.password != "password", user.password
        assert user.username == "username"

        user = user_crud.authenticate_user(
            db_session, username="username", password="new_password"
        )
        assert user.username == "username"
