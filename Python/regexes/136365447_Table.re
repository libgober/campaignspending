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
(?(DEFINE)
(?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be # Table 136365447 type., Spectrum Reach
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
)
^\s+(?P<NETWORKNAME>\w+)
\s+
#note that this date does zero fill out the full month
(?P<ENDMONTHNUMBER>(?P<BEGINMONTHNUMBER>1[012]|0[1-9]))
\D?
(?P<ENDDAYNUMBER>(?P<BEGINDAYNUMBER>(?:3[01]|[12]\d|[1-9])))
\D?
(?P<ENDYEAR>(?P<BEGINYEAR>1\d))
\s+
\w+
\s+
(?P<PROGRAMNAME>.+?)
(?P<AIRTIME>([1][0-2]|[1-9]):[0-5]\d:[0-5]\d\s[pa]m)
\s+
.+?
\$\s
#note sure how they do amountsempty space.
)
^\s+(?P<NETWORKNAME>)\w+
\s+
#note that this date does zero fill out the full month
(?P<ENDMONTHNUMBER>(?P<BEGINMONTHNUMBER>1[012]|0[1-9]))
\D?
(?P<ENDDAYNUMBER>(?P<BEGINDAYNUMBER>(?:3[01]|[12]\d|[1-9])))
\D?
(?P<ENDYEAR>(?P<BEGINYEAR>1\d))
\s+
\w+
\s+
(?P<PROGRAMNAME>.+?)
(?P<AIRTIME>([1][0-2]|[1-9]):[0-5]\d:[0-5]\d\s[pa]m)
\s+
.+?
\$\s
#note sure how they do amounts, was drafted without looking at anything larger than the hundreds
(?P<TOTAL>(?<amount>\d{1,3}(?:,\d{3})*(?:\.\d{2})?))
