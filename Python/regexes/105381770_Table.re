#105381770 NCC Cable Order Table Regex
#### A regular expression ####
#
#
#
#
#Valid keysa
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
    # NETWORKNAME
    # PROGRAMNAME
    
    
(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
    (?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be empty space.
    (?<linebegin>^(?&pdfwhitespace)*\d+) #the mark that a line has begun
    (?<linechar>(?:(?!^\d|\Z).))#a character between lines is any one not follwed by a new line and immediately thereafter a digit or the end of character
    (?<datetype> #
      \b(?:0?[1-9O]|1[0O12])
      [/.\p{Pd}lI1Il]
      (?:0?[1-9O]|[12O][0-9]|3[01])
      [/.\p{Pd}lI1I]
      (?:19|20)?[0-9]{2})

    (?<amount>(?:(?:[1-9]\d{0,2}(?:,\d{3})*|0)(?:\.\d{2})?))
    (?<trange>(?:[01]\d|2[0-4]):{0,1}[0-5][0-9][\p{Pd}\s]+([01]\d|2[0-4])[:.]?[0-5][0-9])
    (?<airtimetype>(?:[1][0-2]|0?\d)(:[0-5][0-9])?[AP]\p{P} #dash punctuation of any kind
    \s*(?:[1][0-2]|0?\d)(:[0-5][0-9])?[AP]?)
    #for this type must insist on the dollar, named example and 118644788 both have it
    # latter would not succeed without it
    (?<dollaramount>\$(?&amount))
    ) #end define

    
###Regex match begins now ####
    #start of line
    (?P<LINENUMBER>)(?&linebegin)
    (?&pdfwhitespace)*
    \d*
    (?&pdfwhitespace)*
    \b(?P<NETWORKNAME>\w*\b)
    (?&pdfwhitespace)*
    (?P<PROGRAMNAME>(?:(?!(?&datetype)).)*)#try to gobble anything that is not a date range
    (?>(?P<BEGINAIRDATE>(?&datetype))  
    (?&pdfwhitespace)+
    (?P<ENDAIRDATE>(?&datetype)))
    (?&pdfwhitespace)+
    (?:#begin alternative, order of these two migh be different
    (?P<AIRTIMERANGE>(?&trange))
    (?&pdfwhitespace)+
    (?P<AIRDAYS>(?:x|(?&pdfwhitespace)|\p{Pd}|\p{Sm})+)
    #but the reverse would be ok too!
    |
    (?P<AIRDAYS>(?:x|(?&pdfwhitespace)|\p{Pd}|\p{Sm})+)
    (?&pdfwhitespace)+
    (?P<AIRTIMERANGE>(?&trange)
    )  
    )#end alternative
    (?&linechar)*?
    (?<SPOTCOUNT_ROW>(?&amount))
    (?&pdfwhitespace)+
    (?P<RATE>(?&dollaramount))
    (?&pdfwhitespace)+
    (?P<TOTAL>(?&dollaramount))