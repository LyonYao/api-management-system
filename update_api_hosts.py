from apimgmt.db.database import get_db
from apimgmt.repositories.api_repository import ApiRepository
from apimgmt.repositories.system_repository import SystemRepository

db = next(get_db())
system_repo = SystemRepository(db)
api_repo = ApiRepository(db)

# 查找现有的系统
systems = system_repo.find_all()
for system in systems:
    print(f'Found system: {system.name} (ID: {system.id})')
    # 查找系统下的API
    apis = api_repo.find_by_system_id(system.id)
    for api in apis:
        print(f'  Found API: {api.name} (ID: {api.id})')
        print(f'    Current Dev Host: {api.dev_host}')
        print(f'    Current UAT Host: {api.uat_host}')
        print(f'    Current Prod Host: {api.prod_host}')
        
        # 更新host配置
        api.dev_host = api.dev_host.replace('8000', '8080') if api.dev_host else 'http://localhost:8080'
        api.uat_host = api.uat_host.replace('8000', '8080') if api.uat_host else 'http://localhost:8080'
        api.prod_host = api.prod_host.replace('8000', '8080') if api.prod_host else 'http://localhost:8080'
        
        # 保存更新
        db.commit()
        print(f'    Updated Dev Host: {api.dev_host}')
        print(f'    Updated UAT Host: {api.uat_host}')
        print(f'    Updated Prod Host: {api.prod_host}')

print('API host configurations updated successfully!')
