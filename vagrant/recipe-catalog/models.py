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
    # password_hash = Column(String(64))

    # # Hashing for manual passwords
    # def hash_password(self, password):
    #     return pwd_context.verify(password, self.password_hash)

    # def verify_password(self, password):
    #     return pwd_context.verify(password, self.password_hash)

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
    name = Column(String(250), nullable = False)
    instructions = Column(String(1000), nullable = False)
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
            'instructions': self.instructions,
            'picture': self.picture,
            'id': self.id
        }


class Ingredient(Base):
    # Set table name for reference
    __tablename__ = 'ingredient'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    picture = Column(String(250))
    # Recipe relationship
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    recipe = relationship(Recipe)
    # User relationship
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # ALlow for JSON enpoint
    @property
    def serialize(self):
        """Return object data in easily seriablizable format"""
        return {
            'name': self.name,
            'picture': self.picture,
            'id': self.id
        }


engine = create_engine('sqlite:///recipes.db')

Base.metadata.create_all(engine)