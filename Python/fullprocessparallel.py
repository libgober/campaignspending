#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 17:45:08 2017




References:
1. http://docs.sqlalchemy.org/en/rel_1_1/core/tutorial.html
2. http://proquest.safaribooksonline.com.ezp-prod1.hul.harvard.edu/9781491916544

@author: brianlibgober
"""
BUFSIZE = 200
threadcount = 32
try:
    refresh_table()
except:
    needs_refreshing=False
    import os
from psycopg2 import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, null
from sqlalchemy.sql import select, text, func
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

import Queue
import threading
print "SQL ALCHEMY VERSION:", sqlalchemy.__version__#1.1.10
from modularaug29 import *

#%%
#create an engine to connect to the database
engine = create_engine(
    'postgresql://brian2:123FH!wjitJt@140.247.114.40/campaignspending',
    pool_size=threadcount)
conn = engine.connect()
#%%
def refresh_table():
    conn.execute(
            """
            -- Table for storing individual ad spots
            
            DROP TABLE IF EXISTS allspots;
            CREATE TABLE allspots (
            	docid int8 NULL,
            	earliest_possible_air_date timestamptz NULL,
            	latest_possible_air_date timestamptz NULL,
            	rate numeric NULL,
            	spots numeric NULL,
            	total numeric NULL,
            	valid bool NULL,
            	weekdays varchar NULL
            );
            
            -- Table for storing data about how a document was parsed.
            DROP TABLE IF EXISTS documentparsing;
            CREATE TABLE documentparsing AS
            select id as docid,False as attempted from documents;
            alter table documentparsing
            add column dollarsindocument boolean,
            add column template int,
            add column contract_cost numeric,
            add column contract_spotcount int,
            add column contract_start timestamp with time zone,
            add column contract_end timestamp with time zone,
            add column spot_match_proportion numeric;
            """
            )
    
if needs_refreshing:
    needs_refreshing=refresh_table()
    needs_refreshing=False
    conn.close()
#%%
#initialize a base object
print "Starting to reflect db"
engine = create_engine(
'postgresql://brian2:123FH!wjitJt@140.247.114.40/campaignspending',
poolclass=NullPool
)
meta = MetaData()
meta.reflect(bind=engine)
#create a document table
documents=meta.tables["documents"]
allspots = meta.tables["allspots"]
documentparsing = meta.tables["documentparsing"]
#setup a connection object
print "db reflected"

#%%

q = Queue.Queue(BUFSIZE)

def producerthread():
    #logging parameters
    recordsdone = 0
    initial =True
    lastreport = 0
    starttime = arrow.now()
    # main action
    prodconn = engine.connect()
    s = select([documentparsing.c.docid])
    s = s.where(documentparsing.c.attempted==False)
    s = s.order_by(func.random())
    results = prodconn.execute(s)
    while True:
        try:
            if q.empty():
                docids = results.fetchmany(size=BUFSIZE)
                for docid in docids:
                    q.put(docid[0])
                #for logging purposes
                if initial:
                    initial =False
                else:
                    recordsdone += BUFSIZE
                    
            if not q.full():
                docids  = results.fetchmany(size=q.maxsize - q.qsize())
                for docid in docids:
                    q.put(docid[0])            
                    i = 1
                    recordsdone += 1
            #every hundred records do another report
            if recordsdone/100 != lastreport:
                endtime = arrow.now()
                elapsed = endtime - starttime
                speed = elapsed.total_seconds()/recordsdone
                remainingcount = prodconn.execute("""
                select 
                    count(*) 
                from 
                    documentparsing 
                where 
                    attempted is false""").fetchone()[0]
                estimate = dt.timedelta(seconds=speed*remainingcount)
                print "Time Elapsed:", elapsed
                print "Seconds Per Record:", speed
                print "Expected RunTime:", estimate
                print "Finish on:", starttime + estimate
                lastreport = recordsdone/100
        except OperationalError:
            prodconn = engine.connect()
                
                
                
def cleandatetime(x):
    if x==x: 
        return x.isoformat()


def consumerthread():
    conconn = engine.connect()     
    while True:
        try:
            if not q.empty():
                docid = q.get()
                s = select([documents]).where(documents.c.id==docid)
                row = conconn.execute(s).fetchone()
                try:
                    txt = row["content"] if row["content"] is not None else ""
                    #run the regex parser
                    parsed = TemplateTester(txt)
                    #update the ad table and processing table depending on the results
                    if parsed.document == "No dollars in document":
                        updt = documentparsing.update().\
                        where(documentparsing.c.docid==docid).\
                            values(
                            attempted=True,
                            dollarsindocument=False
                            )
                        conn.execute(updt)
                    
                    elif parsed.document == 'No succesful document model':
                        #dollars were found, but parse failed.
                        #Template will be null.
                        updt = documentparsing.update().\
                            where(documentparsing.c.docid==docid).\
                            values(
                            attempted=True,
                            dollarsindocument=True
                            )
                        conn.execute(updt)
            
                    else:
                        #first update the document-level parsing table
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
                        conn.execute(updt)
                        #now update the line-by-line data.
                        spotsdata = parsed.document.table.data
                        spotsdata["docid"] = docid
                        spotsdata.earliest_possible_air_date = spotsdata.\
                        earliest_possible_air_date.apply(cleandatetime)
                        spotsdata.latest_possible_air_date = spotsdata.\
                        latest_possible_air_date.apply(cleandatetime)
                        spotsdata.to_sql("allspots",con=engine,if_exists="append",
                                 index=False)
    
                except Exception as e:
                    print "Error",e, "on", docid
                    updt = documentparsing.update().\
                    where(documentparsing.c.docid==docid).values(
                            attempted=True)
                    conn.execute(updt)
                #finished
                q.task_done()
                
        except OperationalError:
            conconn = engine.connect()
            
#%% Now get the threads running
starttime =  arrow.now()
t = threading.Thread(target=producerthread)
t.start()
for i in xrange(threadcount-1):
    t = threading.Thread(target=consumerthread)      
    t.start()

#Problems

        

