from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favorites_peoples: Mapped[list["FavoritePeoples"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    favorites_planets: Mapped[list["FavoritePlanets"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")
    favorites_starships: Mapped[list["FavoriteStarships"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
        return f"{self.email}"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            # do not serialize the password, its a security breach
            "favorites_peoples": [fav.serialize() for fav in self.favorites_peoples] if self.favorites_peoples else [],
            "favorites_planets": [fav.serialize() for fav in self.favorites_planets] if self.favorites_planets else [],
            "favorites_starships": [fav.serialize() for fav in self.favorites_starships] if self.favorites_starships else []
        }

# -------------------------------


class Peoples(db.Model):
    __tablename__ = "peoples"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    comment_text: Mapped[str] = mapped_column(String(120), nullable=False)
    favorite_peoples_by: Mapped[list["FavoritePeoples"]] = relationship(
        back_populates="peoples", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
       return f"Personaje: {self.name} ; Descripcion: {self.comment_text}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "comment_text": self.comment_text
        } 

class FavoritePeoples(db.Model):
    __tablename__ = "favorite_peoples"
    __table_args__ = (UniqueConstraint('user_id', 'peoples_id', name='unique_fav_people'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User", back_populates="favorites_peoples", foreign_keys=[user_id])
    peoples_id: Mapped[int] = mapped_column(ForeignKey("peoples.id"))
    peoples: Mapped["Peoples"] = relationship("Peoples",
        back_populates="favorite_peoples_by", foreign_keys=[peoples_id])
    
    def __repr__(self):
        return f"{self.peoples.name}"
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "peoples_id": self.peoples_id,
            "peoples": self.peoples.serialize() if self.peoples else None,
        }

# ---------------------------------


class Planets(db.Model):
    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    comment_text: Mapped[str] = mapped_column(String(120), nullable=False)
    favorite_planets_by: Mapped[list["FavoritePlanets"]] = relationship(
        back_populates="planets", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
       return f"Planeta: {self.name} ; Descripcion: {self.comment_text}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "comment_text": self.comment_text
        }
    

class FavoritePlanets(db.Model):
    __tablename__ = "favorite_planets"
    __table_args__ = (UniqueConstraint('user_id', 'planets_id', name='unique_fav_planet'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="favorites_planets", foreign_keys=[user_id])
    planets_id: Mapped[int] = mapped_column(ForeignKey("planets.id"))
    planets: Mapped["Planets"] = relationship(
        back_populates="favorite_planets_by", foreign_keys=[planets_id])

    def __repr__(self):
        return f"{self.planets.name}"
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planets_id": self.planets_id,
            "planets": self.planets.serialize() if self.planets else None,
        }

# -------------------------

class Starships(db.Model):
    __tablename__ = "starships"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    comment_text: Mapped[str] = mapped_column(String(120), nullable=True)
    favorite_starships_by: Mapped[list["FavoriteStarships"]] = relationship(
        back_populates="starships", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
       return f"Nave de Batalla: {self.name} ; Descripcion: {self.comment_text}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "comment_text": self.comment_text
        }

class FavoriteStarships(db.Model):
    __tablename__ = "favorite_starships"
    __table_args__ = (UniqueConstraint('user_id', 'starships_id', name='unique_fav_starship'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="favorites_starships", foreign_keys=[user_id])
    starships_id: Mapped[int] = mapped_column(ForeignKey("starships.id"))
    starships: Mapped["Starships"] = relationship(
        back_populates="favorite_starships_by", foreign_keys=[starships_id])

    def __repr__(self):
        return f"{self.starships.name}"
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "starships_id": self.starships_id,
            "starship": self.starships.serialize() if self.starships else None
        }