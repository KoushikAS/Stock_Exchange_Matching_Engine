from sqlalchemy import Column, String, Integer

from models.base import Base

id = 120
class Symbol(Base):
    __tablename__ = 'symbol'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

def create_symbol(session, name):
    id += 1
    newSymbol = Symbol(id=id, name=name)
    session.add(newSymbol)
    return newSymbol
