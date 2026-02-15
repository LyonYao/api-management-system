from typing import Optional
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from apimgmt.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """创建用户"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        """根据ID查找用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def find_by_email(self, email: str) -> Optional[User]:
        """根据邮箱查找用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_last_login(self, user_id: str) -> Optional[User]:
        """更新最后登录时间"""
        user = self.find_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def update(self, user: User) -> Optional[User]:
        """更新用户信息"""
        existing_user = self.find_by_id(user.id)
        if existing_user:
            for key, value in user.__dict__.items():
                if key != '_sa_instance_state' and value is not None:
                    setattr(existing_user, key, value)
            existing_user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_user)
        return existing_user
    
    def delete(self, user_id: str) -> bool:
        """删除用户"""
        user = self.find_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def find_all(self) -> list[User]:
        """查找所有用户"""
        return self.db.query(User).filter(User.is_active == "Y").all()
