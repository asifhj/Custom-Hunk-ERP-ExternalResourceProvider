import sys
import os
import json
import time
import StringIO
import gzip
from pymongo import MongoClient
from erpwriter import ChunkedWriter
import json
import sys, os
import logging
import pymongo

from bson.json_util import dumps


def isGenerating(args):
    return ("db.name" not in args["conf"]["indexes"][0])

# sample header line 
# {"action":"search","conf":{"provider":{"family":"windbag","mode":"stream"},"indexes":[{"name":"sample_vix",
logging.basicConfig(filename='/opt/sandbox-splunk-mongod/hunk/etc/apps/custom_erp/bin/logging_example.out',level=logging.DEBUG)

# parse args passed to us as a single line json object
fo = open("/opt/sandbox-splunk-mongod/hunk/etc/apps/custom_erp/bin/config.json", "r+")
line = fo.read()
fo.close()
args = json.loads(line)


if ("db.name" in args["conf"]["indexes"][0]):
    # get data from path
    path = os.path.expandvars(args["conf"]["indexes"][0]["db.name"])
    db_name = args["conf"]["indexes"][0]["db.name"]
    logging.debug(db_name)
    collection_name = args["conf"]["indexes"][0]["collection.name"]
    logging.debug(collection_name)
    client = MongoClient()
    db = client[db_name]
    docs = db[collection_name].find().sort([('_id', pymongo.ASCENDING)])
    logging.debug(db[collection_name].count())
    #logging.debug("hi hello")

    cw = ChunkedWriter("raw")

    header = {}
    # set some fields:
    # 1. index  is a required field, otherwise events will be thrown away during the filtering step
    # 2. source is a highly recommended field so we can bootstrap the config from props.conf 
    header['field.index'] = args["conf"]["indexes"][0]["name"]

    if isGenerating(args):
        # search time props
        #header['props.EXTRACT-foo']  = 'number (?<number>\\d+)$'
        #header['props.KV_MODE']      = ''

        # "index time" props
        header['props.TIME_FORMAT'] = '%Y-%m-%d %H:%M:%S.%Q'
        header['props.TIME_PREFIX'] = '^'
        header['props.MAX_TIMESTAMP_LOOKAHEAD'] = '30'
        header['props.SHOULD_LINEMERGE'] = 'false'
        header['props.ANNOTATE_PUNCT']   = 'false'
        header['props.INDEXED_EXTRACTION'] = 'json'
        #header['props.DATETIME_CONFIG']  = 'NONE'

    # add fields defined in indexes.conf for this index
    for k,v in args["conf"]["indexes"][0].iteritems():
        if k.startswith("field."):
            header[k] = v

    header['field.sourcetype'] = 'json'
    header['field.host']       = 'abacus'
    header['field.speed']      = 'fast'
    header['field.source'] = db_name+":"+collection_name
    

    for d in docs: 
        #logging.debug(d['_id'].generation_time) 
        d['__time'] =  d['_id'].generation_time
      	cw.write(header, str(dumps(d, sort_keys=True)))
	    #logging.debug(str(d).replace("u'","\"").replace("'","\""))
