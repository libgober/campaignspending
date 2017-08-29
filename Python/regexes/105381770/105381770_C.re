(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
    (?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be empty space
    (?<amount>(?:\d{0,3},?)+(?:\.\d{2})?)
    (?<datetype> #
      \b(?:0?[1-9O]|1[0O12])
      [/.\p{Pd}lI1Il]
      (?:0?[1-9O]|[12O][0-9]|3[01])
      [/.\p{Pd}lI1I]
      (?:19|20)?[0-9]{2})

)
Flight
(?&pdfwhitespace)+
Dates
(?&pdfwhitespace)+
(?P<CONTRACTSTART>(?&datetype))
((?&pdfwhitespace))*-((?&pdfwhitespace))*
(?P<CONTRACTEND>(?&datetype))
