#80544371 Table Regex
# Also 51358119 and 125024786

(?(DEFINE)
#preliminaries
#pdf tends to collect stray marks where there should be empty space.
(?<pdfwhitespace>[\s‘]) 
(?<linechar>(?!^\*(?&pdfwhitespace)+).) 
    (?<datetype> #
      \b(?:0?[1-9]|1[012])
      [/.-]
      (?:0?[1-9]|[12][0-9]|3[01])
      [/.-]
      (?:19|20)?[0-9]{2})
(?<airdaystype>[M\p{Pd}\p{Sm}][T\p{Pd}\p{Sm}][W\p{Pd}\p{Sm}][T\p{Pd}\p{Sm}][F\p{Pd}\p{Sm}][S\p{Pd}\p{Sm}][S\p{Pd}\p{Sm}])
(?<timetype>(?:2[0-4]|[01]\d):[0-5]\d)
(?<amount>(?:(?:[1-9]\d{0,2}(?:,\d{3})*|0)(?:\p{P}?\d{2})))
) #END DEFINE

#BEGIN REGEX
\*?
(?&pdfwhitespace)+
(?P<LINENUMBER>\d+)
(?&pdfwhitespace)+
\d+\/\d+(?:\p{Pd}\w+)?
(?&pdfwhitespace)*
(?:\d*
(?&pdfwhitespace)*)? #not in #125024786
(?P<NETWORKNAME>\S+)
(?&pdfwhitespace)+
(?P<ZONE>\D+)
#some kind of weeks on off thing
(?:\d+\/\d+
(?&pdfwhitespace)+)?
(?P<BEGINAIRDATE>(?&datetype))
[\s\p{Pd}\p{Sm}]+
(?P<ENDAIRDATE>(?&datetype))
(?:(?!(?&airdaystype)).)+
(?P<AIRDAYS>(?&airdaystype))
(?&pdfwhitespace)+
(?P<AIRTIMERANGE>(?&timetype)(?&pdfwhitespace)+(?&timetype))
\s+
(?P<SPOTCOUNT_ROW>\d+)
(?&pdfwhitespace)+
(?P<RATE>(?&amount))
(?&pdfwhitespace)+
(?P<TOTAL>(?&amount))




