#49618345 CONTRACTCOST
(?(DEFINE)
(?<amount>(?:(?:[1-9]\d{0,2}(?:,\d{3})*|0)(?:\p{P}?\d{2})))
)
\$(?P<CONTRACTCOST>(?&amount))\s+(?P<CONTRACTSPOTCOUNT>(?&amount))\s+(?&amount)+\s+.*Total\s+\$(?P=CONTRACTCOST)