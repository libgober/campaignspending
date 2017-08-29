(?(DEFINE) #start define block, all naems in here should be lower case, all matches are upper
    (?<datetype> #
      \b(?:0?[1-9]|1[012])
      [/.-]
      (?:0?[1-9]|[12][0-9]|3[01])
      [/.-]
      (?:19|20)?[0-9]{2})
) #end define

Contract\s+End:\s*(?P<CONTRACTEND>(?&datetype))