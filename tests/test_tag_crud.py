from sqlalchemy.orm import Session

import api.cruds.tag as tag_crud
from api import schemas


class TestTag:
    def test_make_tag(self, db_session: Session):
        tag = tag_crud.create_tag(
            db_session,
            schemas.TagCreate.model_validate(
                {
                    "name": "tag",
                }
            ),
        )
        assert tag.name == "tag"

    def test_read_tag(self, db_session: Session):
        tag = tag_crud.get_tag_by_name(db_session, "tag")
        assert tag.name == "tag"

    def test_read_tags(self, db_session: Session):
        tags = tag_crud.get_tags(db_session)
        assert tags[0].name == "tag"
        assert len(tags) == 1
