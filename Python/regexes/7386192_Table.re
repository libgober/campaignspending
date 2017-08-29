#### 7386192 A regular expression ####
#   Also should match 68869755
#   76428
#
#
#Valid keys
    # LINENUMBER +
    # ENDAIRDATE +
    # BEGINAIRDATE + 
    # AIRDATE 
    # AIRDAYS + 
    # SPOTCOUNT_ROW
    # RATE 
    # TOTAL
    # AIRTIME
    # AIRTIMERANGE
    
    
(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
    (?<linebegin>^\s*\d+\.0\s) #the mark that a line has begun
    (?<linechar>(?:(?!^\s*\d\.|\Z).))#a character between lines is any one not follwed by a new line and immediately thereafter a digit or the end of character
    (?<datetype> #
      \b(?:0?[1-9]|1[012])\s*
      [/.\p{Pd}]\s*
      (?:0?[1-9]|[12][0-9]|3[01])\s*
      [/.\p{Pd}]
      (?:19|20)?[0-9]{2})

    (?<amount>[1-9]\d{0,2}(?:,\d{3})*(?:.\d\d)?)
    (?<trange>(?:[01]\d|2[0-4]):[0-5][0-9]-([01]\d|2[0-4]):[0-5][0-9])
    (?<airtimetype>(?:[1][0-2]|0?\d)(:[0-5][0-9])?[AP]\p{P} #dash punctuation of any kind
    \s*(?:(?:[1][0-2]|0?\d)(:[0-5][0-9])?[AP]?)?)?
    (?<dollaramount>\$(?&amount))
    ) #end define

    
###Regex match begins now ####
    #start of line
    (?P<LINENUMBER>)(?&linebegin)
    (?&linechar)*?
    (?: 
          (?P<BEGINAIRDATE>(?&datetype))
          [\s\p{Pd}]+
          (?P<ENDAIRDATE>(?&datetype))
      )
    (?=
       (?&linechar)*
       (?P<AIRTIME>(?&airtimetype))
     )
     (?=(?&linechar)*
       (?P<SPOTCOUNT_ROW>\d+)
       \s+
       (?P<RATE>(?&dollaramount))
       \s+
       (?P<TOTAL>(?&dollaramount))
    )  