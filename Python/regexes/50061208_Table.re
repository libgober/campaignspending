#Type 50061208
#partially corrupted, only expect some of the lines to match (4/5 to be precise)
(?(DEFINE)
(?<linechar>(?!^\s*\d+\.0).)
)
#first a line number
^\s*(?P<LINENUMBER>\d+)\.0
#then a bunch of other stuff, not very structured and likely corrupted
(?&linechar)+?
(?P<ENDMONTHNUMBER>(?P<BEGINMONTHNUMBER>
\b
(?:1[0O12]|0?[1-9O]))) #a month
[/.\p{Pd}lI1] #some separation 
(?P<ENDDAYNUMBER>(?P<BEGINDAYNUMBER>[12O][0-9]|3[01]|0?[1-9O]))
[/.\p{Pd}lI1] # anotehr separator 
(?P<ENDYEAR>(?P<BEGINYEAR>(?:19|20)?[0-9]{2}))
(?&linechar)+?
#check if the number if the total appears to have thousands separators
\$\s*
(?P<TOTAL>(?=[1-9]\d{0,2},\d{3})
#if it does, match this
[1-9]\d{0,2},(?:\d{3})*(?:\.\d{2})?|
#if not
[1-9]\d*(?:\.\d{2})?)