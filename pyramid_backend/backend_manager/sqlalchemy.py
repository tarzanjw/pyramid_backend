__author__ = 'tarzan'

import importlib
from . import Manager

DBSession = None

def factory(config):
    """
    :type config: pyramid.config.Configurator
    """
    global DBSession
    settings = config.get_settings()
    dbsession_path = settings.get('pyramid_backend.sqlalchemy.dbsession')
    if not dbsession_path:
        return lambda m: None

    _module, _var = dbsession_path.rsplit('.', 1)
    _module = importlib.import_module(_module, package=None)
    DBSession = getattr(_module, _var)

    def _create_manager(model):
        return SQLAlchemyManager(model)

    return _create_manager

class SQLAlchemyManager(Manager):
    def create(self, data):
        obj = self.Model()
        for k,v in data.items():
            setattr(obj, k, v)
        DBSession.add(obj)
        DBSession.flush()
        return obj
