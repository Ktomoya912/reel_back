from sqlalchemy.orm import Session

import api.cruds.tag as tag_crud
from api import schemas


def create_tag(db: Session):
    return tag_crud.create_tag(
        db,
        schemas.TagCreate.model_validate(
            {
                "name": "tag",
            }
        ),
    )


def test_make_tag(db_session: Session):
    tag = create_tag(db_session)
    assert tag.name == "tag"


def test_read_tag(db_session: Session):
    tag = create_tag(db_session)
    tag = tag_crud.get_tag_by_name(db_session, "tag")
    assert tag.name == "tag"


def test_read_tags(db_session: Session):
    tag = create_tag(db_session)
    tags = tag_crud.get_tags(db_session)
    assert tags[0].name == "tag"
    assert len(tags) == 1
