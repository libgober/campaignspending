#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 17:45:08 2017



syntax 
sys.argv[0] = manager number
sys.argv[1] = manager count
sys.argv[2] = killfile.txt 
#put anything in here and it will stop all processes gracefully



References:
1. http://docs.sqlalchemy.org/en/rel_1_1/core/tutorial.html
2. http://proquest.safaribooksonline.com.ezp-prod1.hul.harvard.edu/9781491916544

@author: brianlibgober
"""
import os
from psycopg2 import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, null
from sqlalchemy.sql import select, text, func, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from psycopg2 import DataError
from sqlalchemy.ext.automap import automap_base 
import sqlalchemy
import itertools
import numpy as np
import regex as re
import pandas as pd
import datetime as dt
import arrow
print "SQL ALCHEMY VERSION:", sqlalchemy.__version__#1.1.10
from modularaug29 import *
import sys
#%% CONSTANTS
dbapi_str = 'postgresql://brian2:123FH!wjitJt@140.247.114.40/campaignspending'




#%%

#%%

def cleandatetime(x):
    if x==x: 
        return x.isoformat()
    
class InteractionManager(object):
    def __init__(self):
        self.assign_manager_number()
        self.setup_killfile()
        self.setup_db()
        self.setup_queue()
        self.get_next_batch()
        
    def assign_manager_number(self):
        """
        For keeping each interaction manager out of each others hair.
        We'll use modular arithmetic on the indexes.
        """
        try:
            self.manager_number = int(sys.argv[0]) 
        except ValueError:
            self.manager_number = 0
        try:
            self.manager_count = int(sys.argv[1])
        except (IndexError,ValueError) as e:
            self.manager_count=1
    
    def setup_killfile(self):
        try:
            self.killfile = sys.argv[2]
        except:
            self.killfile = "killfile.txt"
        with open(self.killfile,"a"):
            pass
    
    
    def setup_db(self):
        self.engine = create_engine(dbapi_str)
        self.meta = MetaData()
        self.meta.reflect(bind=self.engine)
        self.conn = self.engine.connect()
        print "db setup"
        
    def setup_queue(self):
        documentparsing = self.meta.tables["documentparsing"]
        s = select([documentparsing.c.docid])
        s = s.where(documentparsing.c.attempted==False).where(
                documentparsing.c.docid % self.manager_count == self.manager_number)
        s= s.order_by(func.random())
        self.queue = self.conn.execute(s).fetchall()  
        self.queue = [i[0] for i in self.queue]
        self.batch = self.get_next_batch()


    def run(self):
        while self.keepgoing():
            if len(self.batch)==0:
                self.get_next_batch()
            docid,txt = self.batch[0]
            self.upload_results(docid,txt)
            #now fix the queue
            del self.batch[0]
            self.queue = [i for i in self.queue if i != docid]
            
            
    def keepgoing(self):
        """
        Be able to send a kill signal to all processes
        """
        return os.stat(self.killfile).st_size == 0
    
    def get_next_batch(self):
        """
        Fetching 100 documents at a time should 
        lower the processing load on the server, so that it's not swamped
        with many simultaneous connections
        """
        documents = self.meta.tables["documents"]
        s = select([documents.c.id, documents.c.content]).where(
                documents.c.id.in_(self.queue[:100]))
        self.batch = [i for i in self.conn.execute(s).fetchall()]
        for i in xrange(len(self.batch)):
            #null txt can pose a problem, let's replace as so
            if self.batch[i][1] is None:
                self.batch[i][1] = ""
        
    

    
    def upload_results(self,docid,txt):
        documentparsing = self.meta.tables["documentparsing"]
        try:
            parsed = TemplateTester(txt)
            if parsed.document == "No dollars in document":
                updt = documentparsing.update().\
                where(documentparsing.c.docid==docid).\
                values(
                        attempted=True,
                        dollarsindocument=False
                        )
            elif parsed.document == 'No succesful document model':
                #dollars were found, but parse failed.
                #Template will be null.
                updt = documentparsing.update().\
                    where(documentparsing.c.docid==docid).\
                    values(
                    attempted=True,
                    dollarsindocument=True
                    )
            else:
                #setup the data to add to the indiviudal ads table
                spotsdata = parsed.document.table.data
                spotsdata["docid"] = docid
                spotsdata.earliest_possible_air_date = spotsdata.\
                earliest_possible_air_date.apply(cleandatetime)
                spotsdata.latest_possible_air_date = spotsdata.\
                latest_possible_air_date.apply(cleandatetime)
                spotsdata.to_sql("allspots",con=self.engine,if_exists="append",
                         index=False)
                #now do the update
                updt = documentparsing.update().\
                where(documentparsing.c.docid==docid).\
                values(
                        dollarsindocument=True,
                        template = parsed.document.templateid,
                        #technically this could be easily calculated via SQL commands,
                        #But a little redundancy is fine
                        spot_match_proportion= \
                            parsed.document.matchstats[
                                "table_proportion_row_rates_times_spots_equals_total"
                                  ],
                        contract_cost = \
                             parsed.document.matchstats["CONTRACTCOST"] if \
                             type(parsed.document.matchstats["CONTRACTCOST"]) in [float,int] \
                             else null(),
                        contract_spotcount = \
                            parsed.document.matchstats["CONTRACTSPOTCOUNT"] if \
                            type(parsed.document.matchstats["CONTRACTSPOTCOUNT"]) \
                            in [float,int] \
                            else null(),
                        contract_start = parsed.document.\
                            matchstats["CONTRACTSTART"].isoformat() if \
                            type(parsed.document.matchstats["CONTRACTSTART"]) \
                            is arrow.arrow.Arrow \
                            else null(),
                        contract_end = parsed.document.\
                            matchstats["CONTRACTEND"].isoformat() if \
                            type(parsed.document.matchstats["CONTRACTEND"]) \
                            is arrow.arrow.Arrow \
                            else null(),
                        attempted=True
                        )
            # now run update    
            self.conn.execute(updt)
        except Exception as e:
            print "Error",e, "on", docid
            updt = documentparsing.update().\
            where(documentparsing.c.docid==docid).values(
                    attempted=True)
            self.conn.execute(updt)

        
    

#%%
im = InteractionManager()
im.run()
                
                
                




