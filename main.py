from models.base import Session, engine, Base
from models.account import Account

Base.metadata.create_all(engine)
session = Session()

account1 = Account(123456, 50)
account2 = Account(1234567890, 100)

session.add(account1)
session.add(account2)

session.commit()
session.close()

print("Session committed")