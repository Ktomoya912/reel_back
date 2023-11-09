from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from api.db import Base


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(50), unique=True, index=True)

    def __repr__(self):
        return f"<Tag({self.id}, {self.tag_name})>"
