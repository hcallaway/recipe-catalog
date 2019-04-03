from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from passlib.apps import custom_app_context as pwd_context


Base = declarative_base()


class User(Base):
    # Set table name for reference
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False)
    email = Column(String(100), nullable = False)
    picture = Column(String(250))

    # Allow for JSON endpoint
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'id': self.id
        }


class Recipe(Base):
    # Set table name for reference
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key = True)
    category = Column(String(50), nullable = False)
    name = Column(String(250), nullable = False)
    instructions = Column(String(2000), nullable = False)
    cook_time = Column(String(100), nullable = True)
    ingredients = Column(String(2000), nullable = False)
    picture = picture = Column(String(250))
    # User relationship
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Allow for JSON endpoint
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'category': self.category,
            'instructions': self.instructions,
            'cook_time': self.cook_time,
            'ingredients': self.ingredients,
            'picture': self.picture,
            'id': self.id
        }


engine = create_engine('sqlite:///recipes.db')

Base.metadata.create_all(engine)