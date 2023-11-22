
# -*- coding: utf-8 -*-

from enum import unique
from pymongo import MongoClient
import pymongo
import os
from decimal import Decimal
import datetime
import re

from collections import OrderedDict
from .settings import MDB_USERNAME,MDB_PASSWORD,MDB_HOST,MDB_PORT

class mdb_connection(object):
    is_connect = False

    def __init__(self):
        self.username = MDB_USERNAME
        self.password = MDB_PASSWORD
        self.host = MDB_HOST
        self.port = MDB_PORT
        self.db = None

    def connect(self, database):
        client = MongoClient('mongodb://' + self.host + ':%s' % self.port,
                             username=self.username,
                             password=self.password)
        #self.table = table
        self.db = client[database]
        #self.mdb = self.db[table]
        self.is_connect = True
    
    def connect_table(self, table):
        self.table = table
        self.mdb = self.db[table]

    def change_table(self, table):
        self.table = table
        self.mdb = self.db[table]

    def disconnect_table(self):
        self.table = None
        self.mdb = None

    def disconnect(self):
        self.is_connect = False
        self.sock = None

    def list_collections(self):
        collections = self.db.list_collection_names()
        return collections

    def mdb_insert(self, records, one_record=False):
        if one_record:
            self.mdb.insert_one(records[0])
        else:
            for record in records:
                self.mdb.insert_one(record)

    def mdb_find_all(self):
        return self.mdb.find()

    def aggregate(self, search, project, sort, count, limit):
        data = []
        if search:
            data.append({"$search": search})
        if limit:
            data.append({"$limit": limit})
        if sort:
            data.append({"$sort": sort})
        if project:
            data.append({"$project": project})
        if count:
            data.append({"$count": count})
        return self.mdb.aggregate(data)
    
    def find(self, query, limit, sort="_id", sort_type="DESC"):
        data = self.mdb.find(query)
        if sort:
            if sort_type == "ASC":
                data = data.sort(sort, pymongo.ASCENDING)
            else:
                data = data.sort(sort, pymongo.DESCENDING)
        if limit:
            data = data.limit(limit)

        return data
    
    def find_new(self, filter={}, sort=None, limit=20):
        print("#"*20,filter,sort,limit)
        data = self.mdb.find(filter=filter,sort=sort,limit=limit)
        return data
