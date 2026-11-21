"""Seedhe, simple Hindi — bina technical shabd ke."""

WELCOME_TEXT = """*Namaste ji!* 🙏

Main ghar waalon ke liye property likhne- sumbhálné wala helper hoon.

*Bas property ka jo message WhatsApp par aaya hai, yahan copy-paste kar dena.*
Main yaad rakhunga — kisne bheja, kisko phone karna hai.

*Aap yeh bhi likh sakte ho:*
• *meri list* — aaj kya kaam bacha hai
• *khojo buyer ke liye 3bhk vesu* — client ko sale listings
• *kharidar dhundo 3bhk vesu* — aap bech rahe ho to buyer enquiry
• *kiraye par lena 3bhk vesu* — rehne ke liye rent flat
• *tenant dhundo 3bhk vesu* — aap rent dena chahte ho
• *khojo adajan 3bhk* — purani property dhundo
• *de do 93…* — kaam kisi aur family member ko
• *ho gaya* — phone / kaam ho chuka

Subah aur shaam *sirf ek chhota sa message* aayega — baar-baar pareshan nahi.

Kuch samajh na aaye to *madad* likh dena."""

HELP_TEXT = """*Aram se — 4 cheez yaad rakho:*

*1) Save*
Property ka poora message yahi bhej do. Khud hi likh liya jayega.

*2) Client ko flat dikhana (aapke paas buyer hai)*
`khojo buyer ke liye 3bhk vesu furnished`
(ya seedha `buyer ke liye 3bhk vesu` — diary ki *sale* listings)

*3) Aap bech rahe ho — kharidar dhundho*
`kharidar dhundo 3bhk vesu`
(diary mein *kharidi / requirement* wale message)

*4) Rent par rehna (client ko rent flat)*
`kiraye par lena 3bhk vesu furnished`
(diary ki *kiraye par* listings)

*5) Rent dena (tenant dhundo)*
`tenant dhundo 3bhk vesu`
ya `kiraye par dena — tenant chahiye`

*6) Purana dhundhna (simple)*
`khojo vesu rent` ya `dhundo 3bhk adajan`

*7) Kisko dena hai*
`de do 9328059281` (number)
ya `de do rahul` (naam — admin ne naam set kiya ho)

*8) Apna hisaab*
`meri list` — kaunsi enquiry aap par hai, kisko aapne diya

*Ho chuka?*
`ho gaya` ya `ho gaya 3` (number list mein dikhta hai)

Sirf property wali baat — baaki main nahi likhta.

*English bhi chalega:*
• *I have buyer for 3bhk vesu* — search (save nahi)
• *Query / Add* se pehle likhna — save vs dhundh clear rehta hai."""

REJECT_MSG = (
    "Lagta hai yeh property ki listing nahi hai.\n\n"
    "Jaise likhte ho waise bhej do:\n"
    "• 3 BHK Adajan rent 25000\n"
    "• Vesu flat sell 85 lakh\n\n"
    "Ya *madad* likh kar pooch lo."
)

WHITELIST_MSG = "Yeh mobile number abhi family ki list mein nahi hai. Jisne bot lagaya hai unse number jodwa lein."

QUERY_PARSE_FAIL = "Thoda aasaan likho, jaise:\n*khojo adajan 3 bhk rent*"

QUERY_EMPTY = "Aisi property abhi diary mein nahi mili.\nPehle ek message save karo, phir khojo."

QUERY_EMPTY_STOCK = (
    "Abhi client ke liye matching *sale/rent* listing diary mein nahi.\n\n"
    "Broker ka *for sale* message pehle save karo.\n"
    "Phir: *khojo buyer ke liye 3bhk vesu*"
)

QUERY_EMPTY_DEMAND = (
    "Abhi aapke flat jaisi *kharidar enquiry* diary mein nahi.\n\n"
    "Buyer ka requirement paste karke save karo.\n"
    "Phir: *kharidar dhundo 3bhk vesu*"
)

ADD_OK_PREFIX = "✅ {count} property save ho gayi:\n\n"

QUERY_OK_PREFIX = "*Yeh mili hain:*\n\n"
QUERY_OK_STOCK = "*Client ko dikhane ke liye (sale / rent par):*\n\n"
QUERY_OK_DEMAND = "*Kharidne wale ki enquiry (aap bech rahe ho to yeh call karo):*\n\n"
QUERY_OK_RENT_STOCK = "*Rehne ke liye (kiraye par mili listings):*\n\n"
QUERY_OK_RENT_DEMAND = "*Tenant / kirayedar ki enquiry (aap rent dena chahte ho):*\n\n"

QUERY_EMPTY_RENT_STOCK = (
    "Abhi *kiraye par* matching flat diary mein nahi.\n\n"
    "Broker ka rent message save karo.\n"
    "Phir: *kiraye par lena 3bhk vesu*"
)

QUERY_EMPTY_RENT_DEMAND = (
    "Abhi *tenant* wali enquiry diary mein nahi.\n\n"
    "Tenant required message save karo.\n"
    "Phir: *tenant dhundo 3bhk vesu*"
)