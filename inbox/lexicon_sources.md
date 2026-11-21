# Estate lexicon provenance

All production values are lowercase and de-duplicated in `estate_lexicon.json`.
`_inferred: true` appears here—not in JSON—so the runtime file remains a simple
backward-compatible string lexicon. The old app loaded its area, status,
apartment, and type values from Mongo at runtime; no Mongo export or fixture is
reachable in this repository's Git history. Consequently, only the values below
with a concrete legacy sample/comment are legacy-extracted; the coverage set is
clearly marked.

| Value | Source file | Line or note |
| --- | --- | --- |
| `area`, `estate_status`, `apartment`, `property_type` | `property/estate/wputils.py` | `main:21-25`; confirms the four legacy Mongo field mappings (`area_name`, `estate_status_name`, `apartment_name`, `type_name`). |
| `with full furniture`; `full furnished`; `naked`; `fully furnished`; `semi furnished`; `luxurious furnished`; `furnished`; `renovated` | `property/estate/wputils.py` | `main:13-18`; normalised to lowercase. |
| `purchase`; `rent`; `buy`; `sell`; `sale` | `property/estate/wputils.py` | `main:239-250`; legacy status matcher. |
| `available`; `required` | `property/estate/wputils.py` | `main:305-312`; legacy rental-intent matcher. |
| `lk`; `lac`; `lakh`; `lak`; `lacs`; `cr` | `property/estate/wputils.py` | `main:177-194`; legacy price-unit matcher. |
| `sq yard`; `sq yards`; `sq`; `carpet`; `ft`; `sf`; `sft`; `sqft`; `vaar`; `vinga`; `square`; `feet` | `property/estate/wputils.py` | `main:177-180`; legacy size-unit matcher. |
| `city light` (`citylight` alias); `flat`; `furnished`; `3 bhk`; rent figures | `samplequery1.json` | `main:4-77`; parsed output from legacy WhatsApp copy. |
| `buy`; `flat`; `fully furnished`; `52 lac` | `samplequery2.json` | `main:3-20`; parsed legacy listing. |
| `floor_space`; `number_of_bedrooms`; `society`; `area`; `budget`; `estate_status`; `estate_type` | `property/message_mapping.py` | `main:3-22`; legacy message/query field vocabulary. |
| `royal paradise`; `keshav narayan`; `raj harmony`; `grandza`; `rayaltone`; `sun shine residency`; `anupam height`; `dev bhoomi`; `sns splendid`; `hitek avenue`; `surya green view`; `next orchid`; `veer exotica`; `capital greens`; `eco garden`; `ofira residency`; `srungal solitaire`; `rajhans royalton`; `utsav`; `meera`; `marvela`; `aakash expression`; `surya prakash residency`; `nisrag apartment`; `rajtilak apartment`; `surya please`; `aarnav apartment`; `surya darsan`; `kpm residency`; `murti residency`; `falcon avenue`; `aashirwad park`; `golden avenue`; `padma kurti`; `shimandhar apartment`; `bagvati ashish`; `megna park`; `shital park`; `navpad apartment`; `surya complex`; `palacio`; `opera house`; `aarjav apartment`; `maahi residency`; `magh sharmand`; `sakar residency`; `murlidhar`; `sangini residency` | `property/estate/wputils.py` | `main:254-257`; legacy commented seed list. Spelling normalisations are documented by the retained aliases/closest canonical strings. |
| `avadh elrica`; `raghuvir satva`; `happy elegance`; `pramukh satva`; `anand happy astoria`; `rajhans maxton` | MagicBricks Vesu RERA project search | Research-derived, `_inferred: false`; project names visibly listed in the results consulted 2026-11-22. |
| `raghuvir sheron`; `avadh bertina`; `sangini lakeville`; `kohinoor acacia`; `pramukh revanta`; `aakash evergreen`; `raghuvir spalex` | MagicBricks Vesu projects search | Research-derived, `_inferred: false`; project names visibly listed in the results consulted 2026-11-22. |
| `city light`; `athwa`; `rundh`; `piplod`; `bharthana`; `althan`; `pal`; `athwa gate`; `adajan gam`; `nanpura` | Housing.com City Light RERA project search | Research-derived, `_inferred: false`; localities visibly listed in the results consulted 2026-11-22. |
| `pal`; `palanpur`; `jahangirabad`; `bhimrad`; `vesu`; `ghod dod road`; `new city light`; `dumas road`; `vip road`; `ugat canal road`; `sarthana`; `pasodara`; `kamrej`; `paravat patiya`; `olpad` | Surat locality searches and legacy bot scope | `_inferred: true`; high-frequency Surat broker locality spelling/coverage, retained as terms rather than canonical geographic boundaries. |
| Remaining `area` values | Surat WhatsApp broker coverage | `_inferred: true`; Surat or immediately adjacent localities, added to achieve recall where no legacy DB export was committed. |
| Remaining `apartment` values | Surat projects/societies coverage | `_inferred: true`; realistic society/project phrase variants added because the legacy dynamic Mongo list is unavailable. Review against a future export before treating them as an authoritative directory. |
| `apartment`; `bungalow`; `commercial`; `farmhouse`; `godown`; `industrial shed`; `office`; `plot`; `row house`; `showroom`; `shop`; `studio`; `tenament`; `villa`; `warehouse` | Broker WhatsApp vocabulary | `_inferred: true`; real-estate-only type/slang coverage. |
| `lease`; `resale`; `new project`; `booking`; `to let`; `owner`; `tenant`; `unfurnished`; `25k pm`; `negotiable` | Broker WhatsApp vocabulary | `_inferred: true`; common real-estate intent/copy. Budget text stays regex-parsed, not a lexicon category. |
