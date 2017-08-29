(?(DEFINE)
(?<amount>(?:(?:[1-9]\d{0,2}(?:,\d{3})*|0)(?:\p{P}?\d{2})))
)
Gross\sAdvertising\sTotal\s+(?P<CONTRACTCOST>\$(?&amount))