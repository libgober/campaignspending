(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
    (?<datetype> #
      \b(?:0?[1-9]|1[012])
      [/.-]
      (?:0?[1-9]|[12][0-9]|3[01])
      [/.-]
      (?:19|20)?[0-9]{2})
    (?<amount>(?:\d{0,3},?)+\.\d{2})
) #end define

Order\s+lines\s+Total\s+
(?P<CONTRACTSPOTCOUNT>(?&amount))\s+
(?P<CONTRACTCOST>(?&amount))