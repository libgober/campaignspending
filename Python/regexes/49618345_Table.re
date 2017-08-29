#COMCAST Cable Order Table Regex
#### A regular expression ####
# Seems that 125764229 might be a particularly clean one.
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
    # DAYNUMBER
    # MONTHNUMBER
    # YEAR
    
(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
#preliminaries
#pdf tends to collect stray marks where there should be empty space.
(?<pdfwhitespace>[\s‘]) 
#datetype, in 58763056, and named, we have that dates are two digits
#there's a lot of corruption in these. 2*6"16 and 2·5"16 both observed. 
#this seems like the best risk reward balance,exploit the fixed width-edness
#andthefactdates are so uniform
#lines are defined using a similar idea to the above
(?<linechar>(?:(?!(?:1[012]|[1-9])\D(?:3[01]|[12]\d|[1-9])\D(?:1\d)).))
(?<amount>(?:(?:[1-9]\d{0,2}(?:,\d{3})*|0)(?:\p{P}?\d{2})))
) #end define
#BEGIN REGEX HERE
^
(?P<ENDMONTHNUMBER>(?P<BEGINMONTHNUMBER>1[012]|[1-9]))
\D?
(?P<ENDDAYNUMBER>(?P<BEGINDAYNUMBER>(?:3[01]|[12]\d|[1-9])))
\D?
(?P<ENDYEAR>(?P<BEGINYEAR>1\d))
(?&pdfwhitespace)+
(?P<networkname>\w+)
(?&pdfwhitespace)+
(?P<ZONE>(?!/\d{4})(?&linechar))+
/
(?P<SYSCODE>\d{4})
(?&pdfwhitespace)*
#no leading zero, ends in P or AM. noticed colon replaced by nothing or ;, so invocated optional punctuation separator
(?P<AIRTIME>(?:1[012]|[1-9])\p{P}?[0-5]\d[AP]M)
(?P<PROGRAMNAME>(?&linechar)+?)
\$(?P<TOTAL>(?&amount))