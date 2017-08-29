(?(DEFINE)
(?<amount>
#try to match as without commas
(?:[1-9]\d+(?:\.\d{2})?)
))
(?:Affidavits|Summary)\s+Totals\s+:\s+(?P<CONTRACTSPOTCOUNT>\d+)\s+\$\s+(?P<CONTRACTCOST>(?&amount))