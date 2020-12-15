from geoserver.catalog import Catalog
from Config import Config

catalog = None


class GeoserverCatalog:
    def __init__(self):
        global catalog
        catalog = Catalog(Config.GEOSERVER_URL + '/rest', Config.GEOSERVER_USER, Config.GEOSERVER_PASSWD)


    def getLayers(self):
        return catalog.get_layers()

    def getLayer(self, workspace, pg_table):
        return catalog.get_layer(workspace + ':' + pg_table)

    def get_stores(self, names, workspace):
        return catalog.get_stores(names, workspace)

    def getWorkspace(self, name):
        return catalog.get_workspace(name)

    def create_datastore(self, name, workspace, host, port, database, user, passwd, dbtype):
        try:
            ds = catalog.create_datastore(name, workspace)
            ds.connection_parameters.update(
                host=host,
                port=port,
                database=database,
                user=user,
                passwd=passwd,
                type=dbtype)
            catalog.save(ds)
            ds = catalog.get_store(name)
        except Exception as e:
            return e.args[0]
        return ds

    def publish_featuretype(self, store_name, table, native_srs, srs):
        try:
            store = catalog.get_stores(store_name)
            ft = catalog.publish_featuretype(table, store[0], native_srs, srs, jdbc_virtual_table=None)
            return ft
        except Exception as e:
            return print(e)
        return store