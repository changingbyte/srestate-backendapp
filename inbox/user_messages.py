"""Hinglish user-facing WhatsApp replies."""

WELCOME_TEXT = """*Namaste!* 👋

Main aapki *family property bot* hoon.

*Listing save kaise karein?*
Property ki detail seedha likh kar bhej dein (area, BHK, rent/buy/budget).
Example:
`3 bhk flat adajan rent 25000`

*Enquiry / purani listing dhundhne ke liye:*
`query 3bhk adajan rent`
`query vesu flat last 30 days`

*Ek message mein kai listing:*
Pehle `add` likhein, phir har listing ke beech khali line.

*Follow-up roz:*
`followup kal 5pm adajan broker call`
`pending` — aaj ke kaam
`done 3` — complete

*Poori guide:* `help` ya `madad`"""

HELP_TEXT = """*SR Estate — kaise use karein*

*1) Save (auto)*
Koi bhi property message bhejein — system samajh kar save karega.
`2 bhk vesu sell 85 lac`

*2) Enquiry search*
`query adajan rent`
`query 3bhk pal last 30 days`

*3) Kai listing ek saath*
```
add
3 bhk adajan rent 22k

2 bhk vesu sell 1.2 cr
```

*4) Follow-up schedule*
`followup kal sham 6 vesu client visit`
`followup 25/11 10am pal broker`
`pending` — list
`done 5` — khatam

*5) Roz auto (server)*
Subah *daily report* WhatsApp pe
Due time pe *reminder* WhatsApp pe
(PythonAnywhere Tasks mein set hota hai)

*6) Shuruat*
`hi` / `help` / `madad`

Sirf *real estate* — health/travel wagaira save nahi hoga."""

REJECT_MSG = (
    "Yeh property message nahi lag raha.\n\n"
    "*Save:* area + BHK + rent/buy + budget likh kar bhejein.\n"
    "*Search:* `query 3bhk adajan rent`\n"
    "*Guide:* `help` ya `hi`"
)

WHITELIST_MSG = "Yeh number family list mein nahi hai. Admin se number add karvayein."

QUERY_PARSE_FAIL = (
    "Query samajh nahi aayi.\n"
    "Example: `query 3bhk adajan rent` ya `query vesu last 30 days`"
)

QUERY_EMPTY = "Aisi koi listing archive mein nahi mili. Pehle kuch property message save karein."

SAVE_OK = "✅ *Save ho gayi!*\n\n"

ADD_OK_PREFIX = "✅ *{count} listing save ho gayi!*\n\n"

QUERY_OK_PREFIX = "*Mili hui listings:*\n\n"