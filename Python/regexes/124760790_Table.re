#Type 124760790
#constants["regex_table_templatekeys"] #=["LINENUMBER","ENDAIRDATE","BEGINAIRDATE",
#         "AIRDATE","AIRDAYS","SPOTCOUNT_ROW","RATE",
#         "TOTAL","AIRTIME","AIRTIMERANGE",
#         "NETWORKNAME","PROGRAMNAME","SUBROWBEGINAIRDATE",
#         "SUBROWENDAIRDATE","SUBROWAIRDAYS","SUBROWRATE","SUBROWSPOTS",
#         "BEGINDAYNUMBER","BEGINMONTHNUMBER","BEGINYEAR",
#         "ENDDAYNUMBER","ENDMONTHNUMBER","ENDYEAR",
#         "ZONE","SYSCODE"
#         ]
(?(DEFINE)
(?<pdfwhitespace>[\s‘]) 
(?<linechar>(?!^\d+(?&pdfwhitespace)*\w*).)
(?<datetype> #
      (?:0?[1-9]|1[012])
      [/.-]
      (?:0?[1-9]|[12][0-9]|3[01])
      [/.-]
      (?:19|20)?[0-9]{2})
(?<amount>(?:(?:[1-9]\d{0,2}(?:,\d{3})*|0)(?:\p{P}?\d{2})))
)
#REGEX START HERE
^(?P<LINENUMBER>\d+)(?&pdfwhitespace)*
(?P<NETWORKNAME>\w*)
(?:(?!(?P=NETWORKNAME))(?!^\d).)*
((?P=NETWORKNAME)
(?&pdfwhitespace)*
(?P<SUBROWAIRDAYS>\w*)
(?&pdfwhitespace)*
(?P<SUBROWENDAIRDATE>(?P<SUBROWBEGINAIRDATE>(?&datetype)))
(?&pdfwhitespace)*
:\d* #length
(?&pdfwhitespace)*
(?P<SUBROWAIRTIME>(?:1[02]|\d):[0-5]\d\s*[AP]m)?
(?&pdfwhitespace)*
\w*
(?&pdfwhitespace)*
\$(?P<SUBROWRATE>(?&amount))
(?:(?!(?P=NETWORKNAME))(?!^\d).)*
)+