# bb-microservice-v2
Use microservice for App and Web

## permiss for all file
```
sudo chown -R $USER:[$USER] . 
Example: sudo chown -R $USER:ductai26998 . 
```
## Docker
### Add a project in submodule
```docker-compose run [container_name] django-admin startproject src [submodule_name]```
Example: docker-compose run bb_app django-admin startproject src bb_app

### Add an app in project
Create a folder=app_name then:
```django-admin startapp [app_name] path```
Example: docker-compose exec bb_app django-admin startapp gallery bb_app/src/gallery

## After alter model:
```
docker-compose exec bb_app python3 ./bb_app/manage.py makemigrations api
docker-compose exec bb_app python3 ./bb_app/manage.py migrate
```
