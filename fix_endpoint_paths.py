from apimgmt.db.database import get_db
from apimgmt.repositories.endpoint_repository import EndpointRepository

db = next(get_db())
endpoint_repo = EndpointRepository(db)

# 获取所有Endpoint
endpoints = endpoint_repo.find_all()
print(f'Found {len(endpoints)} endpoints')

# 统计需要修改的Endpoint数量
needs_fix = 0
for endpoint in endpoints:
    if not endpoint.path.startswith('/api/v1'):
        needs_fix += 1
        print(f'Endpoint {endpoint.id} has incorrect path: {endpoint.path}')

print(f'\nTotal endpoints needing fix: {needs_fix}')

# 修复Endpoint路径
if needs_fix > 0:
    print('\nFixing endpoint paths...')
    for endpoint in endpoints:
        if not endpoint.path.startswith('/api/v1'):
            old_path = endpoint.path
            new_path = f'/api/v1{old_path}' if old_path.startswith('/') else f'/api/v1/{old_path}'
            endpoint.path = new_path
            print(f'Updated endpoint {endpoint.id}: {old_path} -> {new_path}')
    
    # 保存修改
    db.commit()
    print('\nEndpoint paths fixed successfully!')
else:
    print('\nAll endpoints already have correct paths.')
