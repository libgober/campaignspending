#### A regular expression ####
#
#
#
#
#Valid keys
    # CONTRACTSTART 
    # CONTRACTEND
    # CONTRACTCOST
    # CONTRACTNUMBER
    # CONTRACTSPOTCOUNT
    
(?(DEFINE) #start define block
 #(?<eg>eg) #an example, not run

) #end define block

##### EXPRESSION CODE HERE #####


 
##### TIPS #####
#(?P<linecharval>(?&linechar)), invoke saved routines and save output


# (?<datetype> #
#   \b(?:0?[1-9]|1[012])
#   [/.-]
#   (?:0?[1-9]|[12][0-9]|3[01])
#   [/.-]
#   (?:19|20)?[0-9]{2})
# )