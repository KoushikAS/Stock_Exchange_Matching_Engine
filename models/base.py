import sys
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

try:
    engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')
except:
    print("Exception when trying to create engine.")
    sys.exit()
try:
    engine.connect()
    print("Successfully connected to existing database")
except SQLAlchemyError as err:
    print("error", err.__cause__)

m = MetaData()
m.reflect(engine)
m.drop_all(engine)

Base = declarative_base()
Session = sessionmaker(bind=engine)