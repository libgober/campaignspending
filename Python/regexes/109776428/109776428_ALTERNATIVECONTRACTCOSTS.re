#Alternative Contract Cost for 109776428
Gross\s*Total\s*
#conditional regex, test whether the number has commas
(?P<CONTRACTCOST>\$\s*(?(?=[1-9]\d{0,2},\d{3})#match if yes, thousands number
[1-9]\d{0,2},(?:\d{3})*(?:\.\d{2})?
| #or match if no
[1-9]\d*(?:\.\d{2})?)
)