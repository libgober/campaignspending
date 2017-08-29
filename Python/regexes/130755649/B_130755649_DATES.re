(?(DEFINE)

(?<datetype> #
      \b(?:0?[1-9O]|1[0O12])
      [/.\p{Pd}lI1Il]
      (?:0?[1-9O]|[12O][0-9]|3[01])
      [/.\p{Pd}lI1I]
      (?:19|20)?[0-9]{2})
)
\d+#customer number
\s*
(?P<CONTRACTSTART>(?&datetype))
\s*
[\p{Pd}\p{Sm}]
\s*
(?P<CONTRACTEND>(?&datetype))
\s+
