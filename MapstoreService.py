import requests
from requests.auth import HTTPBasicAuth
import json
from GeoserverCatalog import GeoserverCatalog
from Config import Config

set_up = None


class MapstoreService:
    def __init__(self):
        global set_up

    def login(self):
        try:
            user = Config.MAPSTORE_USER
            password = Config.MAPSTORE_PASSWD
            response = requests.post(Config.MAPSTORE_URL + "/session/login", auth=HTTPBasicAuth(user, password),
                                     data={})
            response_data = json.loads(response.text)
            return response_data
        except Exception as e:
            return e.args[0]

    def get_maps(self, access_token):
        try:
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/xml'
            }
            response = requests.get(Config.MAPSTORE_URL + "/extjs/search/category/MAP",
                                     headers=headers,
                                     data={})
            response_data = json.loads(response.text)
            return response_data
        except Exception as e:
            return e.args[0]

    def create_map(self, access_token, catalog_name, catalog_title,
                   mapname, mapdescription,
                   layers, workspace):
        try:
            catalog_url = Config.GEOSERVER_GC_URL
            url_layer = Config.GEOSERVER_GC_URL
            postgis_layers = ''
            for layer in layers:
                geoserver_catalog = GeoserverCatalog()
                ly = geoserver_catalog.getLayer(workspace, layer)
                if ly:
                    layer_data = geoserver_catalog.getLayer(workspace, layer)  # Return Layer data
                    projection = "EPSG:4326" #layer_data.resource.projection
                    postgis_layers += '''{
                                    "id": "''' + layer + '''",
                                    "format": "image/png",
                                    "name": "''' + layer + '''",
                                    "description": "''' + layer + '''",
                                    "title": "''' + layer + '''",
                                    "type": "wms",
                                    "url": "''' + url_layer + '''",
                                    "bbox": {
                                      "crs": "''' + projection + '''",
                                      "bounds": {
                                        "minx": "-75.695357",
                                        "miny": "4.980746",
                                        "maxx": "-75.02321",
                                        "maxy": "5.400837"
                                      }
                                    },
                                    "visibility": true,
                                    "singleTile": false,
                                    "allowedSRS": {
                                      "''' + projection + '''": true
                                    },
                                    "dimensions": [],
                                    "hideLoading": false,
                                    "handleClickOnLayer": false,
                                    "catalogURL": null,
                                    "useForElevation": false,
                                    "hidden": false,
                                    "params": {}
                                  },'''
            postgis_layers = postgis_layers[:-1]  # Remove last comma

            headers = {
              'Authorization': 'Bearer ' + access_token,
              'Content-Type': 'application/xml'
            }
            payload = '''
                <Resource>
                    <description><![CDATA['''+mapdescription+''']]></description>
                    <metadata></metadata>
                    <name><![CDATA['''+mapname+''']]></name>
                    <category>
                        <name>MAP</name>
                    </category>
                    <Attributes>
                        <attribute>
                            <name>owner</name>
                            <value>admin</value>
                            <type>STRING</type>
                        </attribute>
                    </Attributes>
                    <store>
                        <data>
                            <![CDATA[{
                              "version": 2,
                              "map": {
                                "center": {
                                  "x": -75.33341895846947,
                                  "y": 4.215397240394516,
                                  "crs": "EPSG:4326"
                                },
                                "maxExtent": [
                                  -20037508.34,
                                  -20037508.34,
                                  20037508.34,
                                  20037508.34
                                ],
                                "projection": "EPSG:900913",
                                "units": "m",
                                "zoom": 11,
                                "mapOptions": {},
                                "layers": [
                                  {
                                    "id": "mapnik__0",
                                    "group": "background",
                                    "source": "osm",
                                    "name": "mapnik",
                                    "title": "Open Street Map",
                                    "type": "osm",
                                    "visibility": true,
                                    "singleTile": false,
                                    "dimensions": [],
                                    "hideLoading": false,
                                    "handleClickOnLayer": false,
                                    "useForElevation": false,
                                    "hidden": false
                                  },
                                  {
                                    "id": "Night2012__1",
                                    "group": "background",
                                    "source": "nasagibs",
                                    "name": "Night2012",
                                    "provider": "NASAGIBS.ViirsEarthAtNight2012",
                                    "title": "NASAGIBS Night 2012",
                                    "type": "tileprovider",
                                    "visibility": false,
                                    "singleTile": false,
                                    "dimensions": [],
                                    "hideLoading": false,
                                    "handleClickOnLayer": false,
                                    "useForElevation": false,
                                    "hidden": false
                                  },
                                  {
                                    "id": "OpenTopoMap__2",
                                    "group": "background",
                                    "source": "OpenTopoMap",
                                    "name": "OpenTopoMap",
                                    "provider": "OpenTopoMap",
                                    "title": "OpenTopoMap",
                                    "type": "tileprovider",
                                    "visibility": false,
                                    "singleTile": false,
                                    "dimensions": [],
                                    "hideLoading": false,
                                    "handleClickOnLayer": false,
                                    "useForElevation": false,
                                    "hidden": false
                                  },
                                  {
                                    "id": "s2cloudless:s2cloudless__3",
                                    "format": "image/jpeg",
                                    "group": "background",
                                    "source": "s2cloudless",
                                    "name": "s2cloudless:s2cloudless",
                                    "opacity": 1,
                                    "title": "Sentinel 2 Cloudless",
                                    "type": "wms",
                                    "url": [
                                      "https://1maps.geo-solutions.it/geoserver/wms",
                                      "https://2maps.geo-solutions.it/geoserver/wms",
                                      "https://3maps.geo-solutions.it/geoserver/wms",
                                      "https://4maps.geo-solutions.it/geoserver/wms",
                                      "https://5maps.geo-solutions.it/geoserver/wms",
                                      "https://6maps.geo-solutions.it/geoserver/wms"
                                    ],
                                    "visibility": false,
                                    "singleTile": false,
                                    "dimensions": [],
                                    "hideLoading": false,
                                    "handleClickOnLayer": false,
                                    "useForElevation": false,
                                    "hidden": false
                                  },
                                  {
                                    "id": "undefined__4",
                                    "group": "background",
                                    "source": "ol",
                                    "title": "Empty Background",
                                    "type": "empty",
                                    "visibility": false,
                                    "singleTile": false,
                                    "dimensions": [],
                                    "hideLoading": false,
                                    "handleClickOnLayer": false,
                                    "useForElevation": false,
                                    "hidden": false
                                  },'''+postgis_layers+'''
                                ],
                                "groups": [
                                  {
                                    "id": "Default",
                                    "title": "Default",
                                    "expanded": true
                                  }
                                ],
                                "backgrounds": []
                              },
                              "catalogServices": {
                                "services": {
                                  "ST WMS Service": {
                                    "url": "''' + catalog_url + '''",
                                    "type": "wms",
                                    "title": "ST WMS Service",
                                    "autoload": false
                                  },
                                  "''' + catalog_name + '''": {
                                    "url": "''' + catalog_url + '''",
                                    "type": "wms",
                                    "title": "''' + catalog_title + '''",
                                    "autoload": false,
                                    "showAdvancedSettings": false,
                                    "showTemplate": false,
                                    "hideThumbnail": false,
                                    "metadataTemplate": "<p></p>"
                                  }
                                },
                                "selectedService": "'''+catalog_name+'''"
                              },
                              "widgetsConfig": {
                                "layouts": {
                                  "md": [],
                                  "xxs": []
                                }
                              },
                              "mapInfoConfiguration": {},
                              "dimensionData": {},
                              "timelineData": {}
                            }]]></data>
                    </store>
                </Resource>
                '''

            response = requests.post(Config.MAPSTORE_URL + "/resources",
                                     headers=headers,
                                     data=payload)
            return response
        except Exception as e:
            return e.args[0]
