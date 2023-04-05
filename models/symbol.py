from sqlalchemy import Column, String, Integer

from models.base import Base

class Symbol(Base):
    __tablename__ = 'symbol'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name
