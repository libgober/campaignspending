# Table 124318564 type., Spectrum Reach
#similar to 136365447
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
(?(DEFINE)
(?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be empty space.
(?<amount>[1-9]\d{0,2}(?:,\d{3})*(?:.\d\d)?)
)
^\s+(?P<LINENUMBER>\d+)
\s+
#note that this date does zero fill out the full month
(?: 
(?P<BEGINMONTHNUMBER>1[012]|0[1-9])
\D
(?P<BEGINDAYNUMBER>3[01]|[0-2]\d|[1-9])
\D
(?P<BEGINYEAR>1\d)
\s*
(?P<ENDMONTHNUMBER>1[012]|0[1-9])
\D
(?P<ENDDAYNUMBER>3[01]|[0-2]\d|[1-9])
\D
(?P<ENDYEAR>1\d)
)
\s+
[\w:]*
\s*
(?P<AIRTIMERANGE>(?:2[0-4]|[01]\d):(?:[0-5]\d)\p{Pd}(?:2[0-4]|[01]\d):[0-5]\d)
\s+
(?P<NETWORKNAME>\w+)
\s+
(?P<PROGRAMNAME>(?:(?!\d{4}).)*)
(?P<SYSCODE>\d{4})
\s*
(?P<SPOTCOUNT_ROW>\d)
(?:(?!\$).)*
(?P<RATE>\$\s*(?&amount))
\s*
(?P<TOTAL>\$\s*(?&amount))
