"""Hinglish user-facing WhatsApp replies — helpful assistant tone."""

WELCOME_TEXT = """*Namaste!* Main aapki property helper hoon 🤝

Property ka message *seedha paste* karo — main save karke record rakhta hoon:
*kaun bheja*, *kis se baat karni hai*, *kis member ko kaam diya*.

• `meri leads` — aapka poora dashboard  
• `query adajan 3bhk` — purani listing dhundo  
• `assign 9328059281` — lead family ko do  
• `ho gaya 5` — kaam complete  

Subah-shaam *ek short message* — duplicate spam nahi."""

HELP_TEXT = """*Short guide (extra homework nahi):*

*1) Listing save*  
WhatsApp se jo property text aaye, paste kar do. Auto record:
– Bhejne wala (aap)  
– Broker/contact number  
– Lead # id  

*2) Kisi ko dena*  
`assign 9328059281` ya `assign 12 rahul`

*3) Dhundhna*  
`query vesu rent last 30 days`

*4) Apna kaam dekho*  
`meri leads`

*5) Ho gaya*  
`ho gaya 3`

*Roz 2 message:* subah plan, shaam halka check-in.

Sirf property related."""

REJECT_MSG = (
    "Shayad yeh property listing nahi hai.\n"
    "Area + BHK + rent/buy likh kar bhejo — main record bana dunga.\n"
    "Ya `help` / `hi`"
)

WHITELIST_MSG = "Yeh number abhi family list mein nahi. Admin se add karvayein."

QUERY_PARSE_FAIL = "Thoda clear likho: `query 3bhk adajan rent`"

QUERY_EMPTY = "Database mein match nahi mila. Pehle listing save karo ya alag keyword try karo."

ADD_OK_PREFIX = "✅ {count} listing save + lead record:\n\n"

QUERY_OK_PREFIX = "*Yeh mili listings:*\n\n"