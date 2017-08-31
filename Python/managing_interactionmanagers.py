#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 09:48:27 2017

@author: brianlibgober
"""
NPROCESSES = 12
dbapi_str = 'postgresql://brian2:123FH!wjitJt@140.247.114.40/campaignspending'

#%%
from arrow import now
from time import sleep
from sqlalchemy import create_engine
import subprocess as sp
import datetime as dt
#%% SETUP BENCHMARKS

def todo(engine):
    return engine.execute("""
                select 
                    count(*) 
                from 
                    documentparsing 
                where 
                    attempted is false"""
            ).fetchone()[0]
    
    
engine = create_engine(dbapi_str)
starttodo = todo(engine)
starttime = now()
#%%
processes = []
for i in xrange(NPROCESSES):
    proc =sp.Popen(["python","fullprocess_separate_processes.py",
             str(i),str(NPROCESSES)],stdout=open("logs/" + str(i) + ".txt","w+"))
    processes.append(proc)
    
#%%

while True:
    sleep(60)
    remainingcount = todo(engine)
    recordsdone = starttodo -  remainingcount
    elapsed = now() - starttime
    speed = elapsed.total_seconds()/recordsdone
    estimate = dt.timedelta(seconds=speed*remainingcount)
    print "Records done", recordsdone
    print "Time Elapsed:", elapsed
    print "Seconds Per Record:", speed
    print "Expected RunTime:", estimate
    print "Finish on:", starttime + estimate