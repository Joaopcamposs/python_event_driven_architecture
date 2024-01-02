# Aplicação de exemplo para o site Cosmic Python, que ensina o padrão de desenvolvimento 'Event-driven Architecture'


## Requirements

* docker with docker-compose


## Building the containers

```sh
make build
make up
# or
make all # builds, brings containers up, runs tests
```

## Creating a local virtualenv (optional) [windows powershell]

```sh
make local-enviroment
venv_eda\Scripts\Activate  # caso o ambiente não ativar
make install-dependencies
```

## Running the tests

```sh
make test
# or, to run individual test types
make unit
make integration
make e2e
# or, if you have a local virtualenv
make up
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

## Makefile

There are more useful commands in the makefile, have a look and try them out.
