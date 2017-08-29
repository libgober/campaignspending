#A_124318564 - Spots and costs
(?(DEFINE)
(?P<amount>\d{1,3}(?:,\d{3})*(?:\.\d{2})?)
)
Affidavits\s*Totals\s*:\s*(?P<CONTRACTSPOTCOUNT>\d+)\s*\$\s*(?P<CONTRACTCOST>(?&amount))