#109776428 Common Broadcast Contract
#Edited  July 1 for compliance with named and 104556342 and 124804192
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
    # NETWORKNAME
    # PROGRAMNAME
    # SUBROWBEGINAIRDATE
    # SUBROWENDAIRDATE
    # SUBROWRATE
    # SUBROWSPOTS


  (?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
   (?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be empty space.
    (?<linechar>(?:(?!^(?&pdfwhitespace)*\b[NDE]\b(?&pdfwhitespace)*\b\d+\b|\Z).))#a character between lines is any one not follwed by a new line and immediately thereafter a digit or the end of character
    (?<datetype> #
      (?:0?[1-9O]|1[0O12])
      [/.\p{Pd}lI1Il]
      (?:0?[1-9O]|[12O][0-9]|3[01])
      [/.\p{Pd}lI1I]
      (?:19|20)?[0-9]{2}
       )

    (?<amount>[1-9]\d{0,2}(?:,\d{3})*(?:\.\d{2})?)
    (?<trange>(?:[01]\d|2[0-4]):{0,1}[0-5][0-9][\p{Pd}\s]+([01]\d|2[0-4])[:.]?[0-5][0-9])
    (?<airtimetype>
#Must match examples 3-4P
   (?:[1][0-2]|0?\d)(?::[0-5][0-9]){0,1}
       \s*(?:[APX]M?)?
       (\p{Pd}|\s)
       (?:[1][0-2]|0?\d)(?::[0-5][0-9]){0,1}
       (?:[APX]M?)?

    )
    (?<dollaramount>\$(?&amount))
    #a subline character is a line character that does not include another date
    (?<sublinecharacter>(?:(?!Week:)(?!Totals)(?&linechar)))
    (?<channeltype>(?!(?&datetype))\w)
    ) #end define

    
###Regex match begins now ####
    #start of line
    ^(?&pdfwhitespace)*\b[NDE]{0,1}(?&pdfwhitespace)*(?P<LINENUMBER>\d+)#\b #the mark that a line has begun
    (?&pdfwhitespace)*
    (?:(?!\d*\/)\d)*
    (?&pdfwhitespace)*
    (?&channeltype)*#channel, could be digits or a word
    (?&pdfwhitespace)*
        (?P<BEGINAIRDATE>(?&datetype))  
    (?&pdfwhitespace)+
    (?P<ENDAIRDATE>(?&datetype))
    (?&pdfwhitespace)+
       (?P<PROGRAMNAME>(?:(?!(?&airtimetype))(?&linechar)))+
    (?&airtimetype)
    (?&linechar)+?
    (?P<SPOTCOUNT_ROW>(?&amount)\b)    
    (?&pdfwhitespace)+
    (?P<TOTAL>(?<!:)(?&dollaramount))
        (?&sublinecharacter)*?
    (?:Weeks?:
    (?&sublinecharacter)*?
    (?P<SUBROWBEGINAIRDATE>(?&datetype))
    (?&pdfwhitespace)*
    (?P<SUBROWENDAIRDATE>(?&datetype))
    (?&pdfwhitespace)*
    (?P<SUBROWAIRDAYS>(?!\d*(?&pdfwhitespace)*(?&dollaramount))(?&sublinecharacter)*?)
    (?<SUBROWSPOTS>\d+)  
    (?&pdfwhitespace)+
    (?<SUBROWRATE>(?&dollaramount))
    (?&sublinecharacter)+
    )