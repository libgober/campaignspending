(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
    (?<datetype> #
      \b(?:0?[1-9]|1[012])
      [/.\p{Pd}]
      (?:0?[1-9]|[12][0-9]|3[01])
      [/.-]
      (?:19|20)?[0-9]{2})
    (?<amount>(?:\d{0,3},?)+\.\d{2})
    (?<dollaramount>\$(?&amount))
    ) #end define
Total:\s+(?P<CONTRACTSPOTCOUNT>\d+)\s+(?P<CONTRACTCOST>(?&dollaramount))