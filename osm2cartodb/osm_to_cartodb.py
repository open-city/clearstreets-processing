from os import listdir
from os.path import isfile, join
import datetime

from cartodb_settings import CARTODB_SETTINGS
from cartodb import CartoDBAPIKey, CartoDBException
import xml.etree.ElementTree as ET

def get_latest_insert(plow_id, carto):
  latest = datetime.datetime.now()
  try:
    query = carto.sql("select datestamp from %s where id = '%s'" % (CARTODB_SETTINGS['table'], plow_id))

    if 'datestamp' in query.keys():
      latest = query['datestamp']
    return latest

  except CartoDBException as e:
    print ("some error ocurred", e)

def insert_into_cartodb(plow_id, datestamp, the_geom, carto):

  print plow_id, ' - ', datestamp

  the_geom_wkt = ''
  for point in the_geom:
    the_geom_wkt += point[1] + " " + point[0] + ","

  print the_geom_wkt

  try:
    carto.sql("""
          INSERT INTO %s (id, datestamp, the_geom) 
          VALUES ('%s', '%s', ST_GeomFromText('LINESTRING(%s)'))
          """ % (CARTODB_SETTINGS['table'], plow_id, datestamp, the_geom_wkt))
  
  except CartoDBException as e:
    print ("some error ocurred", e)

# setup
user =  CARTODB_SETTINGS['user']
API_KEY = CARTODB_SETTINGS['api_key']
cartodb_domain = CARTODB_SETTINGS['domain']
carto = CartoDBAPIKey(API_KEY, cartodb_domain)

insert_count = 0
osm_files = [ f for f in listdir('../osm') if isfile(join('../osm',f)) and '.osm' in f]

for osm_file in osm_files:

  plow_id = osm_file.split("_")[0]
  datestamp = ''
  the_geom = []

  latest_insert = get_latest_insert(plow_id, carto)
  # print latest_insert

  # read OSM file
  tree = ET.parse("../osm/%s" % osm_file)
  for node in tree.getroot().iter('node'):
    # print node.attrib
    for child in node:
      if child.attrib['k'] == 'time':
        # print child.attrib
        if len(the_geom) > 0 and current_segment_datestamp > latest_insert:
          the_geom.append([node.attrib['lat'], node.attrib['lon']])
          insert_into_cartodb(plow_id, datestamp, the_geom, carto)
          insert_count = insert_count + 1
          print "inserted %s so far\n" % insert_count;
        the_geom = []
        current_segment_datestamp = datetime.datetime.strptime(child.attrib['v'], "%m/%d/%Y %I:%M:%S %p")

      datestamp = current_segment_datestamp
      the_geom = [[node.attrib['lat'], node.attrib['lon']]]