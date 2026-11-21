"""Seedhe, simple Hindi — family bot."""

WELCOME_TEXT = """*Namaste - Shreeshyam helper*

*3 kaam:*
1) Broker message -> copy-paste (*save*)
2) Dhundhna -> *Query 3bhk vesu*
3) Buyer hai -> *I have buyer 3bhk vesu* (save nahi)

*Naya save -> JP / Jitendra par auto.*

*meri list* | *madad* | *team*"""

HELP_TEXT = """*Seedhi guide*

*Save* - property paste / `Add ...`
*Dhundho* - `Query ...` ya `I have buyer ...`
*List* - `meri list`
*Ho gaya* - `ho gaya` ya `ho gaya 5`
*Team* - `team` (Prince admin: `hatado naam` / `jodo 99... Naam`)

Sale: `Query buy` = diary ki *sell* listings.
Rent: `kiraye par lena ...` | `tenant dhundo ...`"""

REJECT_MSG = (
    "Yeh listing jaisi nahi lagi.\n"
    "Jaise: *3 BHK Vesu sell 85 lakh*\n"
    "Ya *madad*"
)

WHITELIST_MSG = "Yeh number allowed nahi. Prince se team mein jodwa lein."

QUERY_PARSE_FAIL = "Thoda detail likho: *Query 3bhk vesu sell*"

QUERY_EMPTY = "Diary mein nahi mili. Pehle save, phir Query."

QUERY_EMPTY_STOCK = (
    "Client ke liye listing nahi.\n"
    "Pehle broker message *Add* karo."
)

QUERY_EMPTY_DEMAND = (
    "Kharidar enquiry nahi.\n"
    "Buyer requirement save karo, phir *kharidar dhundo ...*"
)

ADD_OK_PREFIX = "OK. {count} property save ho gayi:\n\n"

QUERY_OK_PREFIX = "*Yeh mili:*\n\n"
QUERY_OK_STOCK = "*Client ko (sale/rent):*\n\n"
QUERY_OK_DEMAND = "*Kharidar enquiry:*\n\n"
QUERY_OK_RENT_STOCK = "*Kiraye par rehne ke liye:*\n\n"
QUERY_OK_RENT_DEMAND = "*Tenant chahiye:*\n\n"

QUERY_EMPTY_RENT_STOCK = "Rent listing nahi. Pehle save.\n*kiraye par lena 3bhk vesu*"
QUERY_EMPTY_RENT_DEMAND = "Tenant enquiry nahi.\n*tenant dhundo 3bhk vesu*"