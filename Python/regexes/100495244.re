#### A regular expression ####
#
#
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
    (?<linebegin>^\d+) #the mark that a line has begun
    (?<linechar>(?:(?!^\d|\Z).))#a character between lines is any one not follwed by a new line and immediately thereafter a digit or the end of character
    (?<datetype> #
      \b(?:0?[1-9]|1[012])
      [/.-]
      (?:0?[1-9]|[12][0-9]|3[01])
      [/.-]
      (?:19|20)?[0-9]{2})

    (?<amount>(?:\d{0,3},?)+\.\d{2})
    (?<trange>(?:[01]\d|2[0-4]):[0-5][0-9]-([01]\d|2[0-4]):[0-5][0-9])
    ) #end define

    
###Regex match begins now ####
    #start of line
    (?P<LINENUMBER>)(?&linebegin)
    #check that the coming line characters are followed by a date range or a single date
    (?=
      (?&linechar)*
      (?: 
          (?P<BEGINAIRDATE>(?&datetype))
          [\s\-]+
          (?P<ENDAIRDATE>(?&datetype))
      )
    )
    #check that the coming line characters are followed by airdate,spotcount,rate,total
    (?=
      (?&linechar)*
      (?P<AIRDAYS>[ny]\s+[ny]\s+[ny]\s+[ny]\s+[ny]\s+[ny]\s+[ny])
      \s* #prevent being too gready
      (?P<SPOTCOUNT_ROW>(?&amount))
      \s*
      (?P<RATE>(?&amount))
      \s*
      (?P<TOTAL>(?&amount))
    )
    #check that the coming line characters contain an air time range.
    (?=(?&linechar)*(?P<AIRTIMERANGE>(?&trange)))
    (?&linechar)*

 
##### TIPS #####
#(?P<linecharval>(?&linechar)), invoke saved routines and save output


# (?<datetype> #
#   \b(?:0?[1-9]|1[012])
#   [/.-]
#   (?:0?[1-9]|[12][0-9]|3[01])
#   [/.-]
#   (?:19|20)?[0-9]{2})
# )