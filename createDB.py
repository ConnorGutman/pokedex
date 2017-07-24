from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)


class Type(Base):
    __tablename__ = 'type'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Pokemon(Base):
    __tablename__ = 'pokemon'

    name = Column(String(100), nullable=False)
    bio = Column(String(300))
    sprite = Column(String(80))
    id = Column(Integer, primary_key=True)
    type_id = Column(String, ForeignKey('type.name'))
    type = relationship(Type)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'type': self.type.name,
            'bio': self.bio,
            'sprite': self.sprite,
            'name': self.name,
        }


engine = create_engine('sqlite:///pokedex.db')
Base.metadata.create_all(engine)
