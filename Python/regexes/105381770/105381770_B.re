(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
    (?<pdfwhitespace>[\s‘]) #pdf tends to collect stray marks where there should be empty space
    (?<amount>(?:[1-9]\d{0,2}(?:,\d{3})*|0)(?:\.\d{2})?)
)
Total
(?&pdfwhitespace)+
Spots
(?&pdfwhitespace)+
(?P<CONTRACTSPOTCOUNT>(?&amount))