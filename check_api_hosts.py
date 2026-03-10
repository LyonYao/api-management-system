from apimgmt.db.database import get_db
from apimgmt.repositories.api_repository import ApiRepository

db = next(get_db())
api_repo = ApiRepository(db)
apis = api_repo.find_all()

for api in apis:
    print(f'API ID: {api.id}, Name: {api.name}, Dev Host: {api.dev_host}, UAT Host: {api.uat_host}, Prod Host: {api.prod_host}')
