from sqlalchemy import Column, ForeignKey, String

from apimgmt.db.database import Base


class ApiTag(Base):
    __tablename__ = "api_tags"
    
    api_id = Column(String(36), ForeignKey("apis.id"), primary_key=True)
    tag_id = Column(String(36), ForeignKey("tags.id"), primary_key=True)
