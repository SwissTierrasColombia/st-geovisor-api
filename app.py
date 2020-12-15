from flask import Flask
from flask import request
from flask import jsonify
from GeoserverCatalog import GeoserverCatalog
from GeoserverRestService import GeoserverRestService
from MapstoreService import MapstoreService
from Config import Config

import json as jsonlib

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({'OrchesterAPI': True}), 200


@app.route('/layers')
def get_layers():
    geoserver_catalog = GeoserverCatalog()
    all_layers = geoserver_catalog.getLayers()
    layer_names = [layer.name for layer in all_layers]
    return jsonify({'layers': layer_names}), 200


@app.route('/store', methods=["POST"])
def create_feature_store():
    json = request.get_json()
    store_name = json['store_name']
    workspace = json['workspace']
    db_name = json['db_name']
    host = json['host']
    port = json['port']
    schema = json['schema']
    pg_user = json['pg_user']
    pg_password = json['pg_password']

    geoserver_instance = GeoserverRestService()
    result = geoserver_instance.create_feature_store(store_name,
                                                     workspace,
                                                     db_name,
                                                     host,
                                                     port,
                                                     schema,
                                                     pg_user,
                                                     pg_password)
    cat = GeoserverCatalog()
    stores = cat.get_stores(store_name, workspace)

    return jsonify({'created_store': stores[0].name}), 200


@app.route("/publish_featuretype", methods=["POST"])
def publish_featuretype():
    json = request.get_json()
    store = json['store']
    workspace = json['workspace']
    pg_table = json['pg_table']
    geoserver_instance = GeoserverRestService()
    layer = geoserver_instance.publish_pglayer(store, pg_table, workspace)
    print(str(layer))
    return jsonify({'publish_featuretype': 'ok'}), 200


@app.route('/create_workspace', methods=["POST"])
def create_ws():
    json = request.get_json()
    name = json['name']
    geoserver_instance = GeoserverRestService()
    geoserver_instance.create_workspace(name)
    geoserver_catalog = GeoserverCatalog()
    workspace = geoserver_catalog.getWorkspace(name)
    return jsonify({'workspace': workspace.name}), 200


@app.route("/ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


# ################## Final Endpoints #########################
@app.route("/st_geocreateconn", methods=["POST"])
def st_geocreateconn():
    json = request.get_json()
    name = json['name']
    geoserver_catalog = GeoserverCatalog()
    workspace = geoserver_catalog.getWorkspace(name)

    if workspace is not None:
        return jsonify({'workspace_not_created': 'Workspace Exist'}), 200

    geoserver_instance = GeoserverRestService()
    geoserver_instance.create_workspace(name)
    geoserver_catalog = GeoserverCatalog()
    workspace = geoserver_catalog.getWorkspace(name)

    result = {
        'name': workspace.name,
        'wmsstore_url': workspace.wmsstore_url,
        'coveragestore_url': workspace.coveragestore_url,
        'datastore_url': workspace.datastore_url,
        'href': workspace.href
    }

    return jsonify({'workspace_created': result}), 200


@app.route("/st_createstore", methods=["POST"])
def st_createstore():
    json = request.get_json()
    store_name = json['store_name']
    workspace = json['workspace']
    db_name = json['db_name']
    host = json['host']
    port = json['port']
    schema = json['schema']
    pg_user = json['pg_user']
    pg_password = json['pg_password']

    cat = GeoserverCatalog()
    stores = cat.get_stores(store_name, workspace)
    if stores:
        return jsonify({'store_not_created': 'Store Exist'}), 200

    geoserver_instance = GeoserverRestService()
    geoserver_instance.create_feature_store(store_name,
                                            workspace,
                                            db_name,
                                            host,
                                            port,
                                            schema,
                                            pg_user,
                                            pg_password)
    cat = GeoserverCatalog()
    stores = cat.get_stores(store_name, workspace)
    result = {
        'name': stores[0].name,
        'href': stores[0].href,
        'resource_url': stores[0].resource_url,
        'enabled': stores[0].enabled,
        'type': stores[0].type,
    }
    return jsonify({'workspace_created': result}), 200


@app.route("/st_geocreatelayer", methods=["POST"])
def st_geocreatelayer():
    json = request.get_json()
    name = json['name']
    workspace = json['workspace']
    store = json['store']
    table = json['table']
    srs = json['srs']

    cat = GeoserverCatalog()
    layer = cat.getLayer(workspace, table)
    if layer:
        return jsonify({'layer_not_created': 'Layer Exist'}), 200

    layer = cat.publish_featuretype(store, table, srs, srs)

    result = {
        'name': layer.name,
        'href': layer.href,
        'projection': layer.projection
    }
    return jsonify({'layer_created': result}), 200


@app.route("/st_geogetmaps", methods=["GET"])
def st_geogetmaps():
    mapstore_service = MapstoreService()
    result = {'result': 'FAIL'}

    login_response = mapstore_service.login()
    if isinstance(login_response, dict):
        access_token = login_response['access_token']
        response = mapstore_service.get_maps(access_token)

        result['maps'] = response
        result['result'] = 'TRUE'
    else:
        result['error'] = 'Bad Credentials'

    return jsonify({'st_geocreatemap': result}), 200


@app.route("/st_geocreatemap", methods=["POST"])
def st_geocreatemap():
    json = request.get_json()
    workspace = json['workspace']
    map_name = json['map_name']
    map_description = json['map_description']
    pgtables = json['layers']

    mapstore_service = MapstoreService()
    login_response = mapstore_service.login()

    geoserver_catalog = GeoserverCatalog()
    wk = geoserver_catalog.getWorkspace(workspace)

    access_token = login_response['access_token']
    maps = mapstore_service.get_maps(access_token)
    mr = maps['results']

    if isinstance(mr, dict):
        if mr['name'] == map_name:
            return jsonify({'Map not created': 'Map Exist'}), 200

    if isinstance(mr, list):
        for map in mr:
            if map['name'] == map_name:
                return jsonify({'Map not created': 'Map Exist'}), 200

    if isinstance(login_response, dict):
        mapstore_service.create_map(access_token,
                                    wk.name,  # Catalog name as workspace name
                                    wk.name,  # Catalog title as workspace name
                                    map_name,  # Map name
                                    map_description,  # Map description
                                    pgtables,  # Tables from existing databases sent from client as POST
                                    workspace
                                    )
        maps = mapstore_service.get_maps(access_token)
        return jsonify({'st_geocreatemap': maps}), 200


@app.route('/st_geocreatefastcontext', methods=["POST"])
def st_geocreatefastcontext():
    result = {'result': False}
    json = request.get_json()
    name_conn = json['name_conn']
    store = json['store']
    workspace = json['workspace']
    dbname = json['dbname']
    host = json['host']
    port = json['port']
    user = json['user']
    password = json['password']
    schema = json['schema']
    pgtables = json['layers']

    geoserver_catalog = GeoserverCatalog()
    geoserver_instance = GeoserverRestService()

    # Workspace
    wk = geoserver_catalog.getWorkspace(workspace)
    if wk is None:
        print('Workspace not exist, creating...')
        wk = geoserver_instance.create_workspace(workspace)
    result['workspace'] = wk.name

    # DataStore
    stores = geoserver_catalog.get_stores(store, workspace)
    if not stores:
        print('Datastore not exist, creating...')
        result = geoserver_instance.create_feature_store(store,
                                                         workspace,
                                                         dbname,
                                                         host,
                                                         port,
                                                         schema,
                                                         user,
                                                         password)
        print('Datastore created.')

    # Layers
    for pgtable in pgtables:
        ly = geoserver_catalog.getLayer(workspace, pgtable)
        if ly is None:
            print('Layer from Postgis table not exist, creating...')
            geoserver_instance.publish_pglayer(store, pgtable, workspace)
            print('Layer from Postgis created')

    mapstore_service = MapstoreService()
    login_response = mapstore_service.login()

    access_token = login_response['access_token']

    if isinstance(login_response, dict):
        myMapResponse=mapstore_service.create_map(access_token,
                                    wk.name,  # Catalog name
                                    wk.name,  # Catalog title
                                    workspace,  # Map name
                                    workspace,  # Map description
                                    pgtables,  # Tables from existing databases sent from client as POST
                                    workspace
                                    )

    maps = mapstore_service.get_maps(access_token)
    maplink = Config.MAPSTORE_PUBLIC_URL+"/#/viewer/openlayers/"+ myMapResponse.text
#    return jsonify({'st_geocreatefastcontext': maps}), 200
    return jsonify({'maplink': maplink}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
