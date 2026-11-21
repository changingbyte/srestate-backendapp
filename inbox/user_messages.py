"""Seedhe, simple Hindi — bina technical shabd ke."""

WELCOME_TEXT = """*Namaste ji!* 🙏

Main ghar waalon ke liye property likhne- sumbhálné wala helper hoon.

*Bas property ka jo message WhatsApp par aaya hai, yahan copy-paste kar dena.*
Main yaad rakhunga — kisne bheja, kisko phone karna hai.

*Aap yeh bhi likh sakte ho:*
• *meri list* — aaj kya kaam bacha hai
• *khojo adajan 3bhk* — purani property dhundo
• *de do 93…* — kaam kisi aur family member ko
• *ho gaya* — phone / kaam ho chuka

Subah aur shaam *sirf ek chhota sa message* aayega — baar-baar pareshan nahi.

Kuch samajh na aaye to *madad* likh dena."""

HELP_TEXT = """*Aram se — 4 cheez yaad rakho:*

*1) Save*
Property ka poora message yahi bhej do. Khud hi likh liya jayega.

*2) Purana dhundhna*
`khojo vesu rent` ya `dhundo 3bhk adajan`

*3) Kisko dena hai*
`de do 9328059281` (number)
ya `de do rahul` (naam — admin ne naam set kiya ho)

*4) Apna hisaab*
`meri list` — kaunsi enquiry aap par hai, kisko aapne diya

*Ho chuka?*
`ho gaya` ya `ho gaya 3` (number list mein dikhta hai)

Sirf property wali baat — baaki main nahi likhta."""

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

ADD_OK_PREFIX = "✅ {count} property save ho gayi:\n\n"

QUERY_OK_PREFIX = "*Yeh mili hain:*\n\n"