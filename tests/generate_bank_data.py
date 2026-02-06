#!/usr/bin/env python3
"""
生成银行常见的服务架构、端点和调用关系数据的脚本

这个脚本会生成以下数据：
1. 银行常见的系统/服务
2. 各个系统的API端点
3. 系统之间的调用关系
4. 健康检查结果

使用方法：
    python tests/generate_bank_data.py
"""

import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apimgmt.db.database import engine, Base
from apimgmt.models.system import System
from apimgmt.models.api import Api
from apimgmt.models.endpoint import Endpoint
from apimgmt.models.relationship import Relationship
from apimgmt.models.health_check_result import HealthCheckResult
from apimgmt.models.tag import Tag
from apimgmt.models.api_tag import ApiTag


def create_system(db: Session, name: str, description: str) -> System:
    """创建系统"""
    system = System(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(system)
    db.commit()
    db.refresh(system)
    return system


def create_api(db: Session, system_id: str, name: str, description: str, tags: list = None) -> Api:
    """创建API"""
    api = Api(
        id=str(uuid.uuid4()),
        system_id=system_id,
        name=name,
        description=description,
        auth_type="JWT",
        spec_link=f"https://api.bank.com/{name.lower().replace(' ', '-')}/spec",
        department="IT",
        contact_name="API Team",
        contact_emails="api-team@bank.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(api)
    db.commit()
    db.refresh(api)
    
    # 添加标签
    if tags:
        for tag_name in tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(
                    id=str(uuid.uuid4()),
                    name=tag_name,
                    created_at=datetime.utcnow()
                )
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            api_tag = ApiTag(
                api_id=api.id,
                tag_id=tag.id
            )
            db.add(api_tag)
    
    if tags:
        db.commit()
    
    return api


def create_endpoint(db: Session, api_id: str, path: str, method: str, description: str) -> Endpoint:
    """创建端点"""
    endpoint = Endpoint(
        id=str(uuid.uuid4()),
        api_id=api_id,
        path=path,
        http_method=method,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint


def create_relationship(db: Session, caller_type: str, caller_id: str, callee_type: str, callee_id: str, endpoint_id: str, description: str) -> Relationship:
    """创建调用关系"""
    relationship = Relationship(
        id=str(uuid.uuid4()),
        caller_type=caller_type,
        caller_id=caller_id,
        callee_type=callee_type,
        callee_id=callee_id,
        endpoint_id=endpoint_id,
        auth_type="JWT",
        auth_config='{"token": "sample-token"}',
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


def create_health_check_result(db: Session, endpoint_id: str, status: str, response_code: int = None, response_time_ms: int = None, error_message: str = None) -> HealthCheckResult:
    """创建健康检查结果"""
    result = HealthCheckResult(
        id=str(uuid.uuid4()),
        endpoint_id=endpoint_id,
        status=status,
        response_code=response_code,
        response_time_ms=response_time_ms,
        error_message=error_message,
        checked_at=datetime.utcnow()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def delete_all_records(db: Session):
    """删除数据库中所有记录"""
    print("删除数据库中所有现有记录...")
    
    # 按照依赖关系的相反顺序删除数据，避免外键约束错误
    # 1. 删除健康检查结果
    db.query(HealthCheckResult).delete()
    print("  - 删除了健康检查结果")
    
    # 2. 删除调用关系
    db.query(Relationship).delete()
    print("  - 删除了调用关系")
    
    # 3. 删除API标签关联
    db.query(ApiTag).delete()
    print("  - 删除了API标签关联")
    
    # 4. 删除端点
    db.query(Endpoint).delete()
    print("  - 删除了端点")
    
    # 5. 删除API
    db.query(Api).delete()
    print("  - 删除了API")
    
    # 6. 删除系统
    db.query(System).delete()
    print("  - 删除了系统")
    
    # 7. 删除标签
    db.query(Tag).delete()
    print("  - 删除了标签")
    
    db.commit()
    print("  - 所有记录删除完成")


def generate_bank_data():
    """生成银行数据"""
    print("开始生成银行服务架构数据...")
    
    # 创建数据库会话
    db = Session(bind=engine)
    
    try:
        # 0. 删除所有现有记录
        delete_all_records(db)
        
        # 1. 创建银行常见系统
        print("\n1. 创建系统...")
        
        core_banking = create_system(
            db, 
            "核心银行系统", 
            "处理账户、交易等核心银行业务的系统"
        )
        print(f"  - 创建核心银行系统: {core_banking.name}")
        
        payment_gateway = create_system(
            db, 
            "支付网关", 
            "处理各种支付交易的系统"
        )
        print(f"  - 创建支付网关: {payment_gateway.name}")
        
        customer_management = create_system(
            db, 
            "客户管理系统", 
            "管理客户信息和关系的系统"
        )
        print(f"  - 创建客户管理系统: {customer_management.name}")
        
        risk_management = create_system(
            db, 
            "风险管理系统", 
            "评估和管理业务风险的系统"
        )
        print(f"  - 创建风险管理系统: {risk_management.name}")
        
        mobile_banking = create_system(
            db, 
            "手机银行系统", 
            "提供移动设备访问银行服务的系统"
        )
        print(f"  - 创建手机银行系统: {mobile_banking.name}")
        
        online_banking = create_system(
            db, 
            "网上银行系统", 
            "提供网页访问银行服务的系统"
        )
        print(f"  - 创建网上银行系统: {online_banking.name}")
        
        reporting_system = create_system(
            db, 
            "报表系统", 
            "生成各种业务报表的系统"
        )
        print(f"  - 创建报表系统: {reporting_system.name}")
        
        # 2. 创建API和端点
        print("\n2. 创建API和端点...")
        
        # 核心银行系统API
        core_banking_api = create_api(
            db, 
            core_banking.id, 
            "核心银行API", 
            "核心银行业务的API接口",
            tags=["core", "banking", "transaction"]
        )
        
        core_endpoints = [
            create_endpoint(db, core_banking_api.id, "/accounts", "GET", "获取账户列表"),
            create_endpoint(db, core_banking_api.id, "/accounts/{id}", "GET", "获取账户详情"),
            create_endpoint(db, core_banking_api.id, "/accounts", "POST", "创建新账户"),
            create_endpoint(db, core_banking_api.id, "/accounts/{id}", "PUT", "更新账户信息"),
            create_endpoint(db, core_banking_api.id, "/transactions", "GET", "获取交易列表"),
            create_endpoint(db, core_banking_api.id, "/transactions", "POST", "创建新交易"),
            create_endpoint(db, core_banking_api.id, "/transactions/{id}", "GET", "获取交易详情"),
        ]
        print(f"  - 为核心银行系统创建了 {len(core_endpoints)} 个端点")
        
        # 支付网关API
        payment_api = create_api(
            db, 
            payment_gateway.id, 
            "支付API", 
            "处理支付交易的API接口",
            tags=["payment", "transaction"]
        )
        
        payment_endpoints = [
            create_endpoint(db, payment_api.id, "/payments", "POST", "创建支付"),
            create_endpoint(db, payment_api.id, "/payments/{id}", "GET", "获取支付详情"),
            create_endpoint(db, payment_api.id, "/payments/{id}/status", "GET", "获取支付状态"),
            create_endpoint(db, payment_api.id, "/payments/{id}/cancel", "POST", "取消支付"),
            create_endpoint(db, payment_api.id, "/refunds", "POST", "创建退款"),
            create_endpoint(db, payment_api.id, "/refunds/{id}", "GET", "获取退款详情"),
        ]
        print(f"  - 为支付网关创建了 {len(payment_endpoints)} 个端点")
        
        # 客户管理系统API
        customer_api = create_api(
            db, 
            customer_management.id, 
            "客户API", 
            "管理客户信息的API接口",
            tags=["customer", "user"]
        )
        
        customer_endpoints = [
            create_endpoint(db, customer_api.id, "/customers", "GET", "获取客户列表"),
            create_endpoint(db, customer_api.id, "/customers/{id}", "GET", "获取客户详情"),
            create_endpoint(db, customer_api.id, "/customers", "POST", "创建新客户"),
            create_endpoint(db, customer_api.id, "/customers/{id}", "PUT", "更新客户信息"),
            create_endpoint(db, customer_api.id, "/customers/{id}/documents", "GET", "获取客户文档"),
            create_endpoint(db, customer_api.id, "/customers/{id}/documents", "POST", "上传客户文档"),
        ]
        print(f"  - 为客户管理系统创建了 {len(customer_endpoints)} 个端点")
        
        # 风险管理系统API
        risk_api = create_api(
            db, 
            risk_management.id, 
            "风险管理API", 
            "评估和管理风险的API接口",
            tags=["risk", "compliance"]
        )
        
        risk_endpoints = [
            create_endpoint(db, risk_api.id, "/risk/assess", "POST", "评估交易风险"),
            create_endpoint(db, risk_api.id, "/risk/scores/{customer_id}", "GET", "获取客户风险评分"),
            create_endpoint(db, risk_api.id, "/risk/rules", "GET", "获取风险规则"),
            create_endpoint(db, risk_api.id, "/risk/rules", "POST", "创建风险规则"),
        ]
        print(f"  - 为风险管理系统创建了 {len(risk_endpoints)} 个端点")
        
        # 手机银行系统API
        mobile_api = create_api(
            db, 
            mobile_banking.id, 
            "手机银行API", 
            "手机银行应用的API接口",
            tags=["mobile", "app"]
        )
        
        mobile_endpoints = [
            create_endpoint(db, mobile_api.id, "/mobile/auth", "POST", "手机银行认证"),
            create_endpoint(db, mobile_api.id, "/mobile/dashboard", "GET", "获取仪表盘数据"),
            create_endpoint(db, mobile_api.id, "/mobile/transactions", "GET", "获取交易列表"),
            create_endpoint(db, mobile_api.id, "/mobile/payments", "POST", "发起支付"),
        ]
        print(f"  - 为手机银行系统创建了 {len(mobile_endpoints)} 个端点")
        
        # 网上银行系统API
        online_api = create_api(
            db, 
            online_banking.id, 
            "网上银行API", 
            "网上银行应用的API接口",
            tags=["online", "web"]
        )
        
        online_endpoints = [
            create_endpoint(db, online_api.id, "/online/auth", "POST", "网上银行认证"),
            create_endpoint(db, online_api.id, "/online/accounts", "GET", "获取账户列表"),
            create_endpoint(db, online_api.id, "/online/transfers", "POST", "发起转账"),
            create_endpoint(db, online_api.id, "/online/bills", "GET", "获取账单列表"),
        ]
        print(f"  - 为网上银行系统创建了 {len(online_endpoints)} 个端点")
        
        # 报表系统API
        reporting_api = create_api(
            db, 
            reporting_system.id, 
            "报表API", 
            "生成业务报表的API接口",
            tags=["report", "analytics"]
        )
        
        reporting_endpoints = [
            create_endpoint(db, reporting_api.id, "/reports/account-summary", "GET", "生成账户汇总报表"),
            create_endpoint(db, reporting_api.id, "/reports/transaction-history", "GET", "生成交易历史报表"),
            create_endpoint(db, reporting_api.id, "/reports/risk-assessment", "GET", "生成风险评估报表"),
            create_endpoint(db, reporting_api.id, "/reports/custom", "POST", "生成自定义报表"),
        ]
        print(f"  - 为报表系统创建了 {len(reporting_endpoints)} 个端点")
        
        # 3. 创建调用关系
        print("\n3. 创建调用关系...")
        
        # 手机银行调用核心银行
        create_relationship(
            db, 
            "SYSTEM", 
            mobile_banking.id, 
            "API", 
            core_banking_api.id, 
            core_endpoints[0].id, 
            "手机银行获取账户列表"
        )
        
        create_relationship(
            db, 
            "SYSTEM", 
            mobile_banking.id, 
            "API", 
            payment_api.id, 
            payment_endpoints[0].id, 
            "手机银行发起支付"
        )
        
        # 网上银行调用核心银行
        create_relationship(
            db, 
            "SYSTEM", 
            online_banking.id, 
            "API", 
            core_banking_api.id, 
            core_endpoints[4].id, 
            "网上银行获取交易列表"
        )
        
        create_relationship(
            db, 
            "SYSTEM", 
            online_banking.id, 
            "API", 
            customer_api.id, 
            customer_endpoints[0].id, 
            "网上银行获取客户信息"
        )
        
        # 支付网关调用核心银行
        create_relationship(
            db, 
            "SYSTEM", 
            payment_gateway.id, 
            "API", 
            core_banking_api.id, 
            core_endpoints[5].id, 
            "支付网关处理交易"
        )
        
        # 支付网关调用风险管理
        create_relationship(
            db, 
            "SYSTEM", 
            payment_gateway.id, 
            "API", 
            risk_api.id, 
            risk_endpoints[0].id, 
            "支付网关评估交易风险"
        )
        
        # 报表系统调用核心银行
        create_relationship(
            db, 
            "SYSTEM", 
            reporting_system.id, 
            "API", 
            core_banking_api.id, 
            core_endpoints[4].id, 
            "报表系统获取交易数据"
        )
        
        # 报表系统调用客户管理
        create_relationship(
            db, 
            "SYSTEM", 
            reporting_system.id, 
            "API", 
            customer_api.id, 
            customer_endpoints[0].id, 
            "报表系统获取客户数据"
        )
        
        # 4. 创建健康检查结果
        print("\n4. 创建健康检查结果...")
        
        # 为部分端点创建健康检查结果
        all_endpoints = core_endpoints + payment_endpoints + customer_endpoints
        
        for i, endpoint in enumerate(all_endpoints[:10]):  # 只为前10个端点创建健康检查结果
            status = "SUCCESS" if i % 2 == 0 else "SUCCESS"  # 大部分成功
            if i == 5:
                status = "FAILURE"  # 一个失败的例子
            if i == 8:
                status = "TIMEOUT"  # 一个超时的例子
            
            create_health_check_result(
                db, 
                endpoint.id, 
                status, 
                200 if status == "SUCCESS" else (404 if status == "FAILURE" else None),
                150 + i * 10,  # 响应时间
                "Connection error" if status == "FAILURE" else ("Request timeout" if status == "TIMEOUT" else None)
            )
        
        print(f"  - 为 {len(all_endpoints[:10])} 个端点创建了健康检查结果")
        
        # 5. 总结
        print("\n3. 数据生成完成！")
        print(f"   - 创建了 {8} 个系统")
        print(f"   - 创建了 {7} 个API")
        print(f"   - 创建了 {len(all_endpoints)} 个端点")
        print(f"   - 创建了 {8} 个调用关系")
        print(f"   - 创建了 {len(all_endpoints[:10])} 个健康检查结果")
        print(f"   - 创建了 {len(db.query(Tag).all())} 个标签")
        
        print("\n数据已成功生成，您可以通过以下方式查看：")
        print("1. 访问 http://localhost:8080/docs 查看API文档和测试接口")
        print("2. 使用API端点查看数据，例如：")
        print("   - GET http://localhost:8080/api/v1/systems - 查看所有系统")
        print("   - GET http://localhost:8080/api/v1/apis - 查看所有API")
        print("   - GET http://localhost:8080/api/v1/endpoints - 查看所有端点")
        print("   - GET http://localhost:8080/api/v1/relationships - 查看所有调用关系")
        print("   - GET http://localhost:8080/api/v1/health/results - 查看健康检查结果")
        
    except Exception as e:
        print(f"\n错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # 创建数据库表结构
    print("创建数据库表结构...")
    Base.metadata.create_all(bind=engine)
    
    # 生成数据
    generate_bank_data()
