import logging
import time
from typing import Optional

from open_webui.apps.webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, Text, ForeignKey

log = logging.getLogger(__name__)

####################
# User Models DB Schema
####################

class UserModel(Base):
    __tablename__ = "user_models"

    id = Column(Text, primary_key=True)
    """
        The unique ID of the user-model relationship.
    """
    user_id = Column(Text, ForeignKey('users.id'))
    """
        Foreign key referencing the user.
    """
    model_id = Column(Text, ForeignKey('model.id'))
    """
        Foreign key referencing the model.
    """

class UserModelModel(BaseModel):
    id: str
    user_id: str
    model_id: str

    model_config = ConfigDict(from_attributes=True)

####################
# Forms
####################

class UserModelForm(BaseModel):
    user_id: str
    model_id: str

####################
# User Models Table
####################

class UserModelsTable:
    def assign_model_to_user(self, form_data: UserModelForm) -> Optional[UserModelModel]:
        """
        Assigns a model to a user.
        """
        user_model = UserModelModel(
            id=f"{form_data.user_id}_{form_data.model_id}",  # generate a unique id
            user_id=form_data.user_id,
            model_id=form_data.model_id,
            assigned_at=int(time.time())
        )
        try:
            with get_db() as db:
                result = UserModel(**user_model.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)

                if result:
                    return UserModelModel.model_validate(result)
                else:
                    return None
        except Exception as e:
            log.error(f"Error assigning model to user: {e}")
            return None

    def get_models_by_user_id(self, user_id: str) -> list[UserModelModel]:
        """
        Returns all models assigned to a specific user.
        """
        with get_db() as db:
            return [
                UserModelModel.model_validate({
                **user_model.__dict__,
                'id': str(user_model.id)  # Ensure id is a string
            })
                for user_model in db.query(UserModel).filter_by(user_id=user_id).all()
            ]

    def remove_model_from_user(self, user_id: str, model_id: str) -> bool:
        """
        Removes a specific model assignment from a user.
        """
        try:
            with get_db() as db:
                db.query(UserModel).filter_by(user_id=user_id, model_id=model_id).delete()
                db.commit()
                return True
        except Exception as e:
            log.error(f"Error removing model from user: {e}")
            return False

UserMapModels = UserModelsTable()
