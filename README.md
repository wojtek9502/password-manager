## DND Manager

### Requirements
- Python 3.10
- Docker >=  24.0.5
- docker-compose >= 2.23.3

### Install
1) Run commands:
```shell
python -m pip install virtualenv
make install-venv
make install
```

### Test
```shell
make test
```

### Coverage
```shell
make coverage
```

## Develop
### pgadmin
1) Run pgadmin
```shell
make run-pgadmin
```
2) Go to http://127.0.0.1/login
3) Email\password: admin@admin.com \ admin
4) Connect with db. Host: 127.0.0.1 Port: 5432 Login/password (see docker-compose.yaml)
