(?(DEFINE)
(?<amount>\d{1,3}(?:,\d{3})*(?:\.\d{2})?))
Totals\s+:\s+(?P<CONTRACTSPOTCOUNT>\d+)\s+\$\s+(?P<CONTRACTCOST>(?&amount))