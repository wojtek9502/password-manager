## Password manager
Dockerhub: https://hub.docker.com/repository/docker/wojtek9502/password-manager-api


### Requirements
- Python 3.10
- Docker >=  24.0.5
- docker-compose >= 2.23.3

### Install and run
1) Install venv and activate:
```shell
python -m pip install virtualenv
make install-venv
make install
source venv/bin/activate
```
2) Create .env file in main dir. See .env.example
3) Run db containers
```shell
make up-build
````
4) Go to http://127.0.0.1:5000/swagger-ui
5) Create your user with /user/create endpoint. Use API_AUTH_MASTER_TOKEN from .env file to authorize
6) Sign in with user from prev step, use /user/login endpoint. Use token from response to authorize instead of API_AUTH_MASTER_TOKEN


### Test
Run 1-3 steps from 'Install and run' and run command
```shell
make test
```

### Coverage
Run 1-3 steps from 'Install and run' and run command
```shell
make coverage
```

## Develop
You can run run_server.py to start http server instead of rebuilding an app container after every change
```shell
make up
make db-upgrade
python run_server.py
```

### pgadmin
1) Run pgadmin
```shell
make run-pgadmin
```
2) Go to http://127.0.0.1/login?next=%2Fbrowser%2F
3) Email\password: admin@admin.com \ admin
4) Connect with db. Host: 127.0.0.1 Port: 5432 Login/password (see docker-compose.yaml)
