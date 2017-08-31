#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 21:49:20 2017

@author: brianlibgober

The way the thing should work.

- A document model is initialized with text and a regular expression.

- Under the hood, we use regular expressions to handle all questions about
what text gets extracted. Python handles the transformation of these extracted texts 
into meaningful objects.


The regular expression should specify a consistent set of keys across models.
"""
    
import regex as re
from collections import OrderedDict
import pandas as pd
import numpy as np
import os
import datetime
import copy
import glob
import string
import codecs
import arrow as a

#%%
constants = dict()
constants["weekdays"] =["Monday","Tuesday","Wednesday",
                            "Thursday","Friday","Saturday","Sunday"]
constants["regex_table_templatekeys"] =[
         "LINENUMBER","ENDAIRDATE","BEGINAIRDATE",
         "AIRDATE","AIRDAYS","SPOTCOUNT_ROW","RATE",
         "TOTAL","AIRTIME","AIRTIMERANGE",
         "NETWORKNAME","PROGRAMNAME","SUBROWBEGINAIRDATE",
         "SUBROWENDAIRDATE","SUBROWAIRDAYS","SUBROWRATE","SUBROWSPOTS",
         "BEGINDAYNUMBER","BEGINMONTHNUMBER","BEGINYEAR",
         "ENDDAYNUMBER","ENDMONTHNUMBER","ENDYEAR",
         "ZONE","SYSCODE","SUBROWAIRTIME"
         ]

constants["regex_meta_templatekeys"] =[
        "CONTRACTSTART",
        "CONTRACTEND",
        "ORDERNUMBER",
        "CONTRACTSPOTCOUNT",
        "CONTRACTCOST",
        "SUBCONTRACTCOST",
        "SUBCONTRACTSPOTCOUNT"]
constants["dateformats"] = [
            "MM/DD/YYYY","MM-DD-YYYY",
            "M/D/YYYY","M-D-YYYY",
            "MM/DD/YY","MM-DD-YY","MM DD YY",
                   "M/D/YY","M-D-YY","M D YY"
                   ]  
#note this reflects the order these will be tried, which has efficiency implications
###these numbers reflect the file that was used to design the template
#these were selected to correspond to the most efficient ordering
constants["templates"] = [
        105381770,
        109776428,
        49618345,
        100495244,
        7386192,
        80544371,
        130755649,
        124318564,
        50061208,
        42361724,
        136365447]


def dollarparser(foo):
    return float(foo.replace("$","").replace(",",""))

def dateparser(foo):
    #use regexes to salvage dates
    def textcleaning(x):
        x = x.replace("O","0")
        return x

    match = re.search("""
      (?P<month>0{0,1}[1-9O]|1[0O12])
      [/.\p{Pd}lI1Il]
      (?P<day>0?[1-9O]|[12O][0-9]|3[01])
      [/.\p{Pd}lI1I]
      (?P<year>(19|20)?[0-9]{2})""",foo,flags=\
            re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE)
    try:
        month = int(textcleaning(match.group("month")))
        day = int(textcleaning(match.group("day")))
        year =int(textcleaning(match.group("year")))
        if year < 1900:
            year = year + 2000
            
        return a.Arrow(year,month,day)
    except AttributeError:
        return np.nan
        
class LineNumber(object):
    """
    Each item on a record usually has a number corresponding to a discrete
    purchase
    n
    Primary method is value
    """
    def __init__(self,text):
        try:
            self.value = int(float(text))
        except ValueError:
            self.value = np.nan

if __name__=="__main__":
    ln = LineNumber("1.0")
    print ln, ln.value 
#%%

class DateRange(object):


    def __init__(self,BEGINAIRDATE,ENDAIRDATE):
        self.beginairdate= dateparser(BEGINAIRDATE)
        self.endairdate = dateparser(ENDAIRDATE)
        self.value = [self.beginairdate,self.endairdate]
    
    def __repr__(self):
        return "<DateRange: " + str(self.value)+  " >"
    
if __name__ == "__main__":
    dr = DateRange("08/31/16","08/31/16")
    print dr
    dr = DateRange("08/31/16","yo")
    print dr
 #%% as a preliminary matter to the airdays object we need some other types
class WeekDay(object):
    """"
    Object has attributes:
        * name - a day name in constants["weekdays"]
        * isairday - whether this is a date that an ad aired
        * aircount - either string "unknown" or an int with the count
        * date - either a date from datetime or None if unknown

    
    """
    def __init__(self,name,isairday,aircount="unknown"):
        #check that we have initialized a proper day name
        if name in constants["weekdays"]:
            self.name = name
            #get the isoweekday, which is indexed from 1
            self.isoweekday = constants["weekdays"].index(name) + 1
        else:
            raise ValueError("Name must be in " + str(constants["weekdays"]))
        
        #make sure that isairday is logical
        if isairday:
            self.isairday = True
            if aircount == "unknown":
                self.aircount = "unknown"
            else:
                self.aircount = int(float(aircount))
        else:
            self.isairday = False
            self.aircount = 0
        
        self.date = "unknown"
        
    def __repr__(self):
        return "<Day: %s, IsAirDay: %s, Ads Aired Today: %s, Date: %s>" % (
            self.name,self.isairday,self.aircount,self.date)

if __name__ == "__main__":
    WeekDay("Monday",True,3)

class AirDays(object):
    def __init__(self,text):
        self.text = text
        #now we must parse text using one of the possible formatting rules
        #possibility one, format like Y N Y  N N Y Y starting with Monday
        if re.search("((?=([YN]))\s*){7}",text,re.IGNORECASE):
            match =re.search("""([YN])\s*
                          ([YN])\s*
                          ([YN])\s*
                          ([YN])\s*
                          ([YN])\s*
                          ([YN])\s*
                          ([YN])""",text,
                          re.IGNORECASE | re.VERBOSE) 
            #loop over the days of the week and the match groups
            storage = []
            self.stringrep = ""
            for i in xrange(0,7):
                dayname = constants["weekdays"][i]
                #recall match group 0 is the whole string
                capturegroup = match.group(i+1)
                if capturegroup in ["N","n"]:
                    storage.append(WeekDay(dayname,False))
                else:
                    storage.append(WeekDay(dayname,True))
            
            #done
            self.value = storage
        elif re.search("[M\p{Pd}][T\p{Pd}][W\p{Pd}][T\p{Pd}][F\p{Pd}][S\p{Pd}][S\p{Pd}]",
                         text,re.IGNORECASE):
            match = re.search("[M\p{Pd}][T\p{Pd}][W\p{Pd}][T\p{Pd}][F\p{Pd}][S\p{Pd}][S\p{Pd}]",
                         text,re.IGNORECASE)
            
            storage=[]
            for i in xrange(7):
                dayname = constants["weekdays"][i]
                if match.group(0)[i] not in string.ascii_letters:
                    storage.append(WeekDay(dayname,False))
                else:
                    storage.append(WeekDay(dayname,True))
            self.value=storage
        elif text.lower() in ["m"] :
            self.value = [WeekDay("Monday",True)]
        elif text.lower() in ["tu"]:
            self.value = [WeekDay("Tuesday",True)]
        elif text.lower() in ["w"]:
            self.value = [WeekDay("Wednesday",True)]
        elif text.lower() in ["th"]:
            self.value = [WeekDay("Thursday",True)]
        elif text.lower() in ["f"]:
            self.value = [WeekDay("Friday",True)]
        elif text.lower() in ["sa"]:
            self.value = [WeekDay("Saturday",True)]
        elif text.lower() in ["su"]:
            self.value = [WeekDay("Sunday",True)]
        else:
            self.value = np.nan
                
    @property
    def string_rep():
       """
       Ideally we would store in a standard form that concisely conveys the data
       
       MTWTFSS
       0|0|0|0|<4|2
       
       MTWTFSS
       0|0|0|0|?|2  perhaps should be allowed?       
       """
    
    def __repr__(self):
        return "<AirDays:" +str(self.value) + ">"
    
    
    
        
#
if __name__ == "__main__":
    AirDays('N     N   N   N    N   Y N')
    AirDays('M-WTF--')
    AirDays('X X X X X X X')
#%%
class Ad():
    def __init__(self,date,cost,timerange):
        self.date = date
        self.cost = cost
        self.earliestpossibleairtime = timerange[0]
        self.latesttpossibleairime = timerange[1]

#%% Now we handle the dollar stuff

#%%
if __name__ == "__main__":
    with open("regexes/100495244_Table.re") as g:
        regexcode = g.read()
        regex = re.compile(regexcode,flags=
                           re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE)
        keys = [i for i in regex.groupindex.keys() if i.upper() == i]
        #check if all keys are valid
        all([key in constants["regex_table_templatekeys"] for key in keys])
        match = regex.search(txt)
    
    with open("regexes/7386192_Table.re") as g:
        regexcode = g.read()
        regex = re.compile(regexcode,flags=re.UNICODE |
                           re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE)
        keys = [i for i in regex.groupindex.keys() if i.upper() == i]
        #check if all keys are valid
        all([key in constants["regex_table_templatekeys"] for key in keys])
        match = regex.search(txt)
        
    with codecs.open("regexes/105381770_Table.re","r","utf-8") as g:
        regexcode = g.read()
        regex = re.compile(regexcode,flags= 
                           re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE)
        keys = [i for i in regex.groupindex.keys() if i.upper() == i]
        #check if all keys are valid
        all([key in constants["regex_table_templatekeys"] for key in keys])
        match = regex.search(txt)
        matches = list(regex.finditer(txt[5527:5797]))
        matches = list(regex.finditer(txt[:]))


#%% can delete was scratch 
#list(re.finditer("""
#(?<!Net\s*)Total\s*\$(?P<CONTRACTCOST>(?:\d{0,3},?)+(?:\.\d{2})?)
#""",text,flags=re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE))


#%%

class CostsAndSpots():
    """
    Generally it will be tricky to disentangle the ordering of
    rates, spot counts, and total costs. Thus we leave it to the regex
    to give us a dictionary that gives us what we need.
    """
    def __init__(self,dictin):
        try:
            self.rate = dollarparser(dictin["RATE"])
        except KeyError:
            self.rate = np.nan
        self.total = dollarparser(dictin["TOTAL"])
        try:
            self.spotcount = int(float(dictin["SPOTCOUNT_ROW"]))
        except KeyError:
            self.spotcount = np.nan
        except ValueError:
            self.spotcount = dictin["SPOTCOUNT_ROW"]
        try:
            self.valid = self.total == self.spotcount* self.rate
        except TypeError:
            self.valid = False
    
    def dollarparser(self,foo):
        return float(foo.replace("$","").replace(",","")) 
    
    def __repr__(self):
        if self.valid:
            return "<ValidCostsAndSpots- Spots: {:n}, Rate: ${:.2f}/spot, Total: ${:.2f}".format(
                    self.spotcount, self.rate,self.total)
        else:
            return "<InvalidCostsAndSpots -  Spots: {:n}, Rate: ${:.2f}/spot, Total: ${:.2f}>\n".format(
                    self.spotcount, self.rate,self.total)


#%%

class PurchaseRow():
    """
    An abstract representation of a purchase row.

    Assumes we have a valid match object
    
    Usually  we can combine some information here to acheive better granularity.
    For example we may know that an ad spot ran between 
    
    8/24/2016 and 8/31/2016
    
    And we may also know that ad spots only air on Tuesdays. Therefore
    we can infer which day the ad aired.
    
    We do a little bit of this kind of thing, but it's best saved for later.
    
    For now we focus on concisely reorganizing purchase row data in a consistent
    fashion.
    
    Weekday representation is a string like 0|<3|<3|0 |0|0|0 
    
    This means that there could be 1 or 2 ads on Tuesday or Wednesday, and 0
    all other days.
    
    Note that the Katz media group format indicates in common the dates.
    """
    def __init__(self,match):
        try:
            self._airdays = AirDays(match.group("AIRDAYS"))
        except IndexError:
            #often there is no match group for AIRDAYS
            #for examples see 7381692
            #this is because the absence of an ad is marked with whitespace
            #and this cannot be interpreted easily via regex
            #in this case we assume that all days were marked as possible
            self._airdays = AirDays("YYYYYYY")
          
        if self._airdays.value is np.nan:
            self._airdays = AirDays("YYYYYYY")
        self.airdays = [i.isoweekday for i in \
                        [i for i in self._airdays.value if i is not np.nan] \
                        if i.isairday]
        try:
            BEGINAIRDATE = match.group("BEGINMONTHNUMBER") + "/" + \
                        match.group("BEGINDAYNUMBER") + "/" + \
                        match.group("BEGINYEAR")
            ENDAIRDATE = match.group("ENDMONTHNUMBER") + "/" + \
                        match.group("ENDDAYNUMBER") + "/" + \
                        match.group("ENDYEAR")  
        except IndexError:
            pass
        try:
            BEGINAIRDATE = match.group("BEGINAIRDATE")
            ENDAIRDATE = match.group("ENDAIRDATE")
        except IndexError:
            pass
        self.daterange = DateRange(BEGINAIRDATE,
                                   ENDAIRDATE)
        self.costsandspots = CostsAndSpots(match.groupdict())
        
        ####---- Try to integrate these data sources -----####
        #focus on the dates in the range between begin and end
        #with the right day of week.
        #first try to handle obvious       
        self.datadict = {}
        try:
            self.datadict["earliest_possible_air_date"] =  min(self.dates)
        except (TypeError,ValueError) as err:
            #TypeError trying to compare float and int
            #ValueError min of []
            self.datadict["earliest_possible_air_date"] = np.nan
        try:
            self.datadict["latest_possible_air_date"] = max(self.dates)
        except (TypeError,ValueError) as err:
            self.datadict["latest_possible_air_date"] = np.nan
        # a string representation of the dates
        self.datadict["weekdays"] = \
             "|".join(["<" + str(self.costsandspots.spotcount + 1) \
                 if i in self.airdays else "0" \
                 for i in xrange(1,8)])
        
        self.datadict["rate"]= self.costsandspots.rate
        self.datadict["total"] = self.costsandspots.total
        self.datadict["spots"]= self.costsandspots.spotcount
        self.datadict["valid"] = self.costsandspots.valid
        
        self.data = pd.Series(self.datadict)
#        #just some useful things to know
#        self.beginyear,self.beginweeknum,self.begindaynum = \
#            self.daterange.beginairdate.isocalendar()
#        self.endyear,self.endweeknum,self.enddaynum = \
#            self.daterange.endairdate.isocalendar()
#    
    @property
    def dates(self):
        """"
        Some basic error handle with the dates given.
        Sometimes pdf corrupts the date range in a fairly obvious way.
        We can try to recover
        """
        #nothing to do
        
        if np.nan in [self.daterange.beginairdate,self.daterange.endairdate]:
            return [self.daterange.beginairdate,self.daterange.endairdate]
        
        if self.daterange.beginairdate < self.daterange.endairdate:
            return [arrow for arrow in a.Arrow.range("day",
                                              self.daterange.beginairdate,
                                              self.daterange.endairdate) if 
            arrow.isoweekday() in self.airdays]
        #otherwise we have a problem, let's try some unobjectionable amendments
        if self.daterange.endairdate.year < self.daterange.beginairdate.year:
            self.daterange.endairdate =self.daterange.endairdate.shift(years=1)
        
        return [arrow for arrow in a.Arrow.range("day",
                                              self.daterange.beginairdate,
                                              self.daterange.endairdate) if 
            arrow.isoweekday() in self.airdays]

    
    def __repr__(self):
        return self.data.to_string()
        
if __name__ == "__main__":
    if match is not None:
        self = PurchaseRow(match)

#%%



class TieredPurchaseRow():
    """
    A template may require some reorganizatoin. For example something like
    
N    1  59      10/25/16 10/31/16 M-F 1p-2p   4            $3000.00
          Start Date End Date    Weekdays       Spots/Wee      Rate Rating
    Week: 10/25/16     10/31/16  M-WTF--   2          $300.00    0.00
    Week: 10/25/16     10/31/16  ---T---   2          $1,200.00    0.00

    For now what we will do is simply take the average of the subrates
    and then return a normal purchase row.
    
    If we wish to dig into these weekday things we can add that functionality.
    """

    def __init__(self,match):
        try:
            self._airdays = AirDays(match.group("AIRDAYS"))
        except IndexError:
            #often there is no match group for AIRDAYS
            #for examples see 7381692
            #this is because the absence of an ad is marked with whitespace
            #and this cannot be interpreted easily via regex
            #in this case we assume that all days were marked as possible
            self.match = match
            subrowairdays = [AirDays(s) for s in match.captures("SUBROWAIRDAYS")]
            #if any day is an air day, then mark as so
            try:
                untieredrepresentation = 7*["N"]
                for subrowairday in subrowairdays:
                    dayindex = 0
                    for day in subrowairday.value:
                        if day.isairday:
                            untieredrepresentation[day.isoweekday-1] = "Y"
            except TypeError:
                untieredrepresentation = 7*["Y"]

            self._airdays = AirDays("".join(untieredrepresentation))
            
        self.airdays = [i.isoweekday for i in \
                        [i for i in self._airdays.value if i is not np.nan] \
                        if i.isairday]
        try:
            self.daterange = DateRange(match.group("BEGINAIRDATE"),
                                           match.group("ENDAIRDATE"))
        except IndexError:
            endindex = np.array(map(dateparser,
                                          match.captures("SUBROWENDAIRDATE")
                                          )).argmax()
            beginindex = np.array(map(dateparser,
                                          match.captures("SUBROWBEGINAIRDATE")
                                          )).argmin()
            self.daterange = DateRange(
                    match.captures("SUBROWBEGINAIRDATE")[beginindex],
                    match.captures("SUBROWENDAIRDATE")[endindex])
                
        #Rate depends on the subrows, and will be missing. We add it
        #based on the subrows by calculating the right average.
        dictionary = match.groupdict()
        subrates = np.array([dollarparser(rate) \
                             for rate in match.captures("SUBROWRATE")])

        subrowspots = np.array([int(float(count)) \
                                for count in match.captures("SUBROWSPOTS")])
        #and now the code piggybacks
        dictionary["RATE"] = str(sum(subrates*subrowspots)/sum(subrowspots))
        self.costsandspots = CostsAndSpots(dictionary)
        
        ####---- Try to integrate these data sources -----####
        #focus on the dates in the range between begin and end
        #with the right day of week.
        #first try to handle obvious       
        self.datadict = {}
        try:
            self.datadict["earliest_possible_air_date"] =  min(self.dates)
        except (TypeError,ValueError) as err:
            #TypeError trying to compare float and int
            #ValueError min of []
            self.datadict["earliest_possible_air_date"] = np.nan
        try:
            self.datadict["latest_possible_air_date"] = max(self.dates)
        except (TypeError,ValueError) as err:
            self.datadict["latest_possible_air_date"] = np.nan
        # a string representation of the dates
        self.datadict["weekdays"] = \
             "|".join(["<" + str(self.costsandspots.spotcount + 1) \
                 if i in self.airdays else "0" \
                 for i in xrange(1,8)])
        
        self.datadict["rate"]= self.costsandspots.rate
        self.datadict["total"] = self.costsandspots.total
        self.datadict["spots"]= self.costsandspots.spotcount
        self.datadict["valid"] = self.costsandspots.valid
        self.data = pd.Series(self.datadict)
#        #just some useful things to know
#        self.beginyear,self.beginweeknum,self.begindaynum = \
#            self.daterange.beginairdate.isocalendar()
#        self.endyear,self.endweeknum,self.enddaynum = \
#            self.daterange.endairdate.isocalendar()
#    
    @property
    def dates(self):
        """"
        Some basic error handle with the dates given.
        Sometimes pdf corrupts the date range in a fairly obvious way.
        We can try to recover
        """
        #nothing to do
        
        if np.nan in [self.daterange.beginairdate,self.daterange.endairdate]:
            return [self.daterange.beginairdate,self.daterange.endairdate]
        
        if self.daterange.beginairdate < self.daterange.endairdate:
            return [arrow for arrow in a.Arrow.range("day",
                                              self.daterange.beginairdate,
                                              self.daterange.endairdate) if 
            arrow.isoweekday() in self.airdays]
        #otherwise we have a problem, let's try some unobjectionable amendments
        if self.daterange.endairdate.year < self.daterange.beginairdate.year:
            self.daterange.endairdate =self.daterange.endairdate.shift(years=1)
        
        return [arrow for arrow in a.Arrow.range("day",
                                              self.daterange.beginairdate,
                                              self.daterange.endairdate) if 
            arrow.isoweekday() in self.airdays]
    
    def __repr__(self):
        return self.data.to_string()
    

#%%

if __name__=="__main__":
    if match is not None:
        self = TieredPurchaseRow(match)


#%%Now let's put it all together to make an abstract purchase table
class PurchaseTable(object):
    def __init__(self,regex,text):
        if type(regex) is not re._pattern_type:
            raise ValueError("You have not given a regex compiled expression")
        self.text = text
        self.regex = regex
        self.storage = []
        for match in self.matches:
            #if a line item contains subrows, then we must handle differently
            if any(["SUBROW" in key for key in match.groupdict().keys()]):
                self.storage.append(TieredPurchaseRow(match).data)
            else:
                self.storage.append(PurchaseRow(match).data)
        if len(self.storage) == 0:
            self.data = "no match"
            self.earliest_possible_air_date ="no match"
            self.latest_possible_air_date ="no match"
            self.tablespotcount ="no match"
            self.tabletotalcost = "no match"
            self.matchablestats =  "no match"
        else:
            self.data = pd.concat(self.storage,axis=1).T
            self.earliest_possible_air_date = \
                self.data.earliest_possible_air_date[\
                 ~self.data.earliest_possible_air_date.isnull()\
                 ].min()
            self.latest_possible_air_date = \
                self.data.latest_possible_air_date[\
                 ~self.data.latest_possible_air_date.isnull()].max()
            self.tablespotcount =self.data.spots.sum()
            self.tabletotalcost = self.data.total.sum()
            self.sanerowproportion = self.data.valid.mean()
            self.matchablestats =  {"table_earliest_possible_air_date" : 
                self.earliest_possible_air_date,
            "table_latest_possible_air_date" :
                self.latest_possible_air_date,
            "table_totalcosts" : 
                self.tabletotalcost,
            "table_spotcount" :
                self.tablespotcount,
            "table_proportion_row_rates_times_spots_equals_total" :
                self.sanerowproportion}
                
            
    @property
    def matches(self):
        try:
            return list(self.regex.finditer(self.text))
        except Exception as e:
            print e
            return []


    
if __name__=="__main__":
    self = PurchaseTable(regex,txt)
#%% Now we also wish to get meta data out of the document
class Template():
    def __init__(self,number):
        self.templateid = number
        with codecs.open("regexes/%s_Table.re" % number,
                         encoding="utf-8") as f:
            regexcode = f.read()
            regex = re.compile(regexcode,flags=
                       re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE)
            keys = [i for i in regex.groupindex.keys() if i.upper() == i]
                #check if all keys are valid
            if not all([key in constants["regex_table_templatekeys"] for key in keys]):
                raise AttributeError("This is not a valid template, does not supply appropriate keys")
                print  [key for key in keys \
                        if key not in constants["regex_table_templatekeys"]]
            else:
                self.TableRegex=regex
        self.meta_regexes = []
        for fin in glob.glob("regexes/%s/*" % number):
            with open(fin) as g:
                regexcode = g.read()
                regex = re.compile(regexcode,flags=
                       re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE)
                #basic validity checking
                keys = [i for i in regex.groupindex.keys() if i.upper() == i]
                if not all([key in constants["regex_meta_templatekeys"] for key in keys]):
                    raise AttributeError("This is not a valid template, does not supply appropriate keys")
                else:
                    self.meta_regexes.append(regex)

if __name__ == "__main__":         
    template = Template(130755649)
#%%
class DocSummary(object):
    def __init__(self,template,text,supertext=""):
        if type(template) is int:
            self.templateid=template
            self.template = Template(template)
        else:
            self.template = template
        self.text =text
        self.supertext = supertext if len(supertext) > len(text) else text
        self.results = dict()
        for i in self.template.meta_regexes:
            for match in i.finditer(self.text):
                #find the keys that we wanted to get out of this regex
                keys = self._get_relevant_keys_from_match(match)
                for key in keys:
                    if "SUB" in key:
                        #this is a stitch type summary, so
                        #we actually expect multiple matches
                        #and we some across the captures
                        self.results[key.replace("SUB","")] = \
                            str(sum(map(dollarparser,match.captures(key))))
                    else:
                        for key in match.capturesdict().keys():
                            #when there is a conflicting match, record this fact 
                            #and overwrite the match (so the last match is always
                                                      #what we take
                            self.results[key] = match.group(key)
                            if self._check_conflicting_matches(match,key):
                                self.results["%s_conflict" %key] = True
                            else:
                                self.results["%s_conflict" % key]  =False
                
        
        datadict={}
        try:
            datadict["CONTRACTCOST"]=dollarparser(self.results["CONTRACTCOST"])
        except KeyError:
            datadict["CONTRACTCOST"]="no match"
        try:
            datadict["CONTRACTSTART"]=dateparser(self.results["CONTRACTSTART"])
        except KeyError:
            datadict["CONTRACTSTART"]="no match"
        try:
            datadict["CONTRACTEND"]= dateparser(self.results["CONTRACTEND"])
        except KeyError:
            datadict["CONTRACTEND"]="no match"
        try:
            datadict["CONTRACTSPOTCOUNT"]= \
                int(float(dollarparser(self.results["CONTRACTSPOTCOUNT"])))
        except KeyError:
            datadict["CONTRACTSPOTCOUNT"]="no match"
                  
        
        datadict.update(
        {key  : self.results[key] for key in self.results if "conflict" in key}
        )
        
        self.datadict = datadict
        self._failsafe_amounts_and_spots()
#
    @property
    def data(self):
        return pd.Series(self.datadict)
    
    def _get_relevant_keys_from_match(self,match):
        return [key for key in match.groupdict() if key == key.upper()]
    
    def _check_conflicting_matches(self,match,key):
        if not self.results.has_key(key):
            return False
        else:
            #potentially there is a conflictr
            if self.results[key] == match.group(key):
                return False
            else:
                #conflict found
                return True
            
    def _failsafe_amounts_and_spots(self):
        """
        Ideally we grab the spots and amounts from structured text via regex
        But sometimes our structuring information we use has corrupted text.
        Such is the joys of dealing with pdfs.
        
        Therefore as a failsafe we use something like what open secrets did.
        """
        
        #only try to fix if using structured data didn't work
        if self.datadict["CONTRACTCOST"] == 'no match' and \
            self.datadict["CONTRACTSPOTCOUNT"] == "no match":
                
                
            
            regex = re.compile("""
                   (?(DEFINE)
                    (?<amount>[1-9]\d{0,2}(?:\d{0,3},?)+\.?(?:\d{2}){0,1})
                    (?<dollar>\$(?&amount))
                )
                \s(?P<SPOTCOUNT>(?&amount))\s+(?P<COST>(?&dollar))        
                 
            """, re.VERBOSE | re.DOTALL | re.IGNORECASE | re.MULTILINE)
            
            matches = list(regex.finditer(self.supertext))
            dollarlist = [match.group("COST").replace("$","") \
                          for match in matches]
            dollarlist = self._fixmissingcentmark(dollarlist)
            spotlist = [dollarparser(match.group("SPOTCOUNT")) for match in \
                            matches]
            #now we wish to look for a pair that conjoins the max spot list and
            #max dollar list, find their index
            try:
                maxdollar = max(dollarlist)
            except ValueError:
                return
            try:
                maxspot = max(spotlist)
            except ValueError:
                return
            #could be multiple matches if the phrase repeats
            try:
                index= min([i for i in xrange(len(spotlist))\
                                    if spotlist[i]==maxspot and\
                                    dollarlist[i]==maxdollar])
                self.datadict["CONTRACTCOST"] = dollarlist[index]
                self.datadict["CONTRACTSPOTCOUNT"]= spotlist[index]
            except ValueError:
                #iF we try to take minimum of the joint match,
                #and get nothing, we arrive here, let's try to return something
                #for the dollar total
                try:
                    self.datadict["CONTRACTCOST"] = \
                        maxdollar
                except NameError:
                    pass
                    
    def _fixmissingcentmark(self,dollarlist):
        """
        Usually receipts record dollar totals like $4,000.00.
        Somtimes they do like $4,000
        
        If the pdf ocr loses a period, which can easily happen.
        Then the total is like 400,000, or 100x too big.
        
        This can lead to big problems if it happens a lot.
        
        So we try to figure out what kind of set of dollar strings we have.
        
        Returns a list of floats
        """
        dollarlist = [i.replace(",","") for i in dollarlist]
        proportion_with_cents = np.mean(
                [amount[-3:]==".00" for amount in dollarlist])
        if proportion_with_cents > 0.6:
            #if ?3/5 dollar strings 
            #a larger number might be taken, but there are often very few ads
            newdollarlist = []
            for amount in dollarlist:
                try:
                    if amount[-3] == ".":
                        newdollarlist.append(float(amount))
                    elif amount[-1] == ".":
                        #probably some kind of weird truncation at the end issue,
                        #just assume that it's correct
                        #we had an example like 275.OO, note O not 0.
                        newdollarlist.append(float(amount))
                    else:
                        #insert a period in the third to last position
                        fixedamount = amount[:-2] + "." +  amount[-2:]
                        newdollarlist.append(float(fixedamount))
                except IndexError:
                    "If the amount is uncharactristically short, drop it"
                    newdollarlist.append(float(amount))
            return newdollarlist
        else:
            return [float(dollar) for dollar in dollarlist]

    def __repr__(self):
        return "<DocSummary--\n" + self.data.to_string() + "\n--DocSummary>"
    
if __name__ == "__main__":
    text = txt
    self = DocSummary(template,text)

#%%
class DocumentModel():
    def __init__(self,template,text):
        if type(template) == int:
            self.templateid = template
            template =Template(template)
        self.text = text
        self.table = PurchaseTable(template.TableRegex,text)
        #modify the meta data text, only look in the first match or the last match
        #also, since we prefer the last match,  but we would prefer
        #this is a little goofy, may whish to cut or improve
        matches = list(self.table.matches)
        if len(matches) == 0:
            self.metatext = text
        else:
            firstmatch, lastmatch = matches[0],matches[-1]
        #do the best we can to move from the end position
        #other methods had difficulties with capturing because not lookahead messed up other matches
            lastmatch_endpos = max([i[1] for i in lastmatch.regs])
            firstmatch_startpos = firstmatch.span()[0]
            self.metatext = text[lastmatch_endpos:] + "\n\n\n\n\n" + text[:firstmatch_startpos]
        #try to do a meta summary
        self.metasummary = DocSummary(template, self.metatext,self.text) #!!!!!!

    
    @property
    def isempty(self):
        return self.metasummary.results=={} or (type(self.table.data) == str)
    
    @property
    def matchstats(self):
        if type(self.table.data) == pd.core.frame.DataFrame:
            out = dict(self.table.matchablestats)
            out.update(self.metasummary.data.to_dict())
            out["costs_in_table_matches_summary"] =  \
                out["CONTRACTCOST"]==out["table_totalcosts"]
            out["spotcount_in_table_matches_summary"] = \
                out["CONTRACTSPOTCOUNT"]==out["table_spotcount"]
            out["earliest_airdate_in_table_matches_summary"] =\
                out["CONTRACTSTART"] == out["table_earliest_possible_air_date"]
            out["latest_airdate_in_table_matches_summary"] = \
                out["CONTRACTEND"] == out["table_latest_possible_air_date"]                
            return pd.Series(out)
        else:
            return "no table data"
        
if __name__ == "__main__":
    self = DocumentModel(template,text)
    print DocumentModel(template,text).matchstats

#%%
class TemplateTester():
    def __init__(self,text):
        #first check if there is anything that looks like money on the table
        if re.search("\$\s*\d+",text):
            self.dollarsindocument = "Yes"
            self.document = "No succesful document model"
            self.successcount = 0
            #iterate over each template
            #eventually we will want to stop parsing once we reach success
            for template in constants["templates"]:
                new_document = DocumentModel(template,text)
                if new_document.isempty:
                    pass
                else:
                    self.successcount += 1
                    self.document = new_document
        else:
            self.document = "No dollars in document"
                
if __name__ == "__main__":                  
    self = TemplateTester(text)
    self.successcount,self.document
#%% SINGLE EXAMPLE
if __name__=="__main__":
    try:
        import os
        try:
            os.chdir(os.path.expanduser("~/Github/campaignspending/Python"))
        except OSError:
            os.chdir('/Users/brianlibgober/Dropbox/Collaborations/Campaign Spending/Python')
        from modularaug29 import *
        pullid=55178
        from sqlalchemy import create_engine
        from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
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
        import arrow
        engine = create_engine('postgresql://brian2:123FH!wjitJt@140.247.114.40/campaignspending')
        conn = engine.connect()
        meta = MetaData()
        meta.reflect(bind=engine)
        #create a document table
        documents =meta.tables["documents"]
        processing = meta.tables["processing"]
        s = select([documents]).where(documents.c.id==pullid)
        row = conn.execute(s).fetchone()
        txt = row["content"]
        parsed = TemplateTester(txt)
        summary = parsed.document.metasummary
        print parsed.document.matchstats, summary, "Number of successses", parsed.successcount
    except Exception as e:
        print e
        pass
        

