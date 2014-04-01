pyramid_backend
===============

A backend development kit for pyramid

Usage
-----

    config.include('pyramid_backend')

### Configurations:

1. *pyramid_backend.admin_site*: related path for backend site from root
2. *pyramid_backend.manager_factories*: the list of backend manager factories. Default is :

        pyramid_backend.backend_manager.sqlalchemy:factory

3. *pyramid_backend.models*: list of class to be managed automatically by pyramid_backend

#### Backend manager's configuration:

##### SQLAlchemy

1. *pyramid_backend.sqlalchemy.dbsession*: the full path to Session object