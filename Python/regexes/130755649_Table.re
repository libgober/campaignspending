#130755649, ad link

# Table 136365447 type., Spectrum Reach
#Currently understood codes
#["LINENUMBER","ENDAIRDATE","BEGINAIRDATE",
#         "AIRDATE","AIRDAYS","SPOTCOUNT_ROW","RATE",
#         "TOTAL","AIRTIME","AIRTIMERANGE",
#         "NETWORKNAME","PROGRAMNAME","SUBROWBEGINAIRDATE",
#         "SUBROWENDAIRDATE","SUBROWAIRDAYS","SUBROWRATE","SUBROWSPOTS",
#         "BEGINDAYNUMBER","BEGINMONTHNUMBER","BEGINYEAR",
#         "ENDDAYNUMBER","ENDMONTHNUMBER","ENDYEAR",
#         "ZONE","SYSCODE"
#         ]
(?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be 
(?(DEFINE)
(?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be empty space.
#(?<linechar>(?!\s*\d*).)
)
^\s*(?P<LINENUMBER>\d+)
\s+
(?:(?!\d{3,4}).)+
\s+
(?P<SYSCODE>\d+)
\s+
(?P<NETWORKNAME>\w+)
\s+
(?P<ENDMONTHNUMBER>(?P<BEGINMONTHNUMBER>1[012]|0[1-9]))
\D?
(?P<ENDDAYNUMBER>(?P<BEGINDAYNUMBER>(?:3[01]|[012]\d)))
\D?
(?P<ENDYEAR>(?P<BEGINYEAR>1\d))
\s+
(?P<AIRTIME>([1][0-2]|[1-9]):[0-5]\d\s+[pa]m)
(?:(?!\$).)*
\$\s+
#seems that they do amounts with no commas, but not sure of that
(?P<TOTAL>(?<amount>\d{1,3}(?:,\d{3}|\d{3})*(?:\.\d{2})?))
