import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apimgmt.db.database import get_db
from sqlalchemy.orm import Session
from apimgmt.models import EndpointTest, TestResult, Endpoint, Api, System, Relationship, HealthCheckResult, ApiTag


def clean_database():
    """清理数据库中的测试数据，只保留user表"""
    db: Session = next(get_db())
    
    try:
        # 删除测试结果
        db.query(TestResult).delete()
        print("已删除所有测试结果")
        
        # 删除测试用例
        db.query(EndpointTest).delete()
        print("已删除所有测试用例")
        
        # 删除健康检查结果
        db.query(HealthCheckResult).delete()
        print("已删除所有健康检查结果")
        
        # 删除关系
        db.query(Relationship).delete()
        print("已删除所有关系")
        
        # 删除API标签关联
        db.query(ApiTag).delete()
        print("已删除所有API标签关联")
        
        # 删除端点
        db.query(Endpoint).delete()
        print("已删除所有端点")
        
        # 删除API
        db.query(Api).delete()
        print("已删除所有API")
        
        # 删除系统
        db.query(System).delete()
        print("已删除所有系统")
        
        db.commit()
        print("数据库清理完成")
    except Exception as e:
        db.rollback()
        print(f"清理数据库时出错: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    clean_database()
