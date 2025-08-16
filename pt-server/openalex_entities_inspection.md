# OpenAlex Entities Inspection Report

**Generated on:** /Users/pandrre/projects/papertrail/pt-server
**Parquet source:** `/Volumes/T7/openalex-parquet`

**Entities found:** 9
**Entity list:** authors, concepts, domains, fields, funders, publishers, sources, subfields, topics

---

## 1. AUTHORS

**Dimensions:** 103,480,180 rows × 17 columns
**Memory usage:** ~47.81 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `orcid` | `String` |
| 3 | `display_name` | `String` |
| 4 | `display_name_alternatives` | `List(String)` |
| 5 | `works_count` | `Int32` |
| 6 | `cited_by_count` | `Int32` |
| 7 | `summary_stats` | `Struct({'2yr_mean_citedness': Float64, 'h_index': Int32, 'i10_index': Int32})` |
| 8 | `ids` | `Struct({'openalex': String, 'orcid': String, 'scopus': String, 'twitter': String, 'wikipedia': String})` |
| 9 | `affiliations` | `List(Struct({'institution': Struct({'id': String, 'ror': String, 'display_name': String, 'country_code': String, 'type': String, 'lineage': List(String)}), 'years': List(Int32)}))` |
| 10 | `last_known_institutions` | `List(Struct({'id': String, 'ror': String, 'display_name': String, 'country_code': String, 'type': String, 'lineage': List(String)}))` |
| 11 | `topics` | `List(Struct({'id': String, 'display_name': String, 'count': Int32, 'subfield': Struct({'id': String, 'display_name': String}), 'field': Struct({'id': String, 'display_name': String}), 'domain': Struct({'id': String, 'display_name': String})}))` |
| 12 | `topic_share` | `List(Struct({'id': String, 'display_name': String, 'value': Float64, 'subfield': Struct({'id': String, 'display_name': String}), 'field': Struct({'id': String, 'display_name': String}), 'domain': Struct({'id': String, 'display_name': String})}))` |
| 13 | `x_concepts` | `List(Struct({'id': String, 'wikidata': String, 'display_name': String, 'level': Int32, 'score': Float64}))` |
| 14 | `counts_by_year` | `List(Struct({'year': Int32, 'works_count': Int32, 'cited_by_count': Int32}))` |
| 15 | `works_api_url` | `String` |
| 16 | `created_date` | `Date` |
| 17 | `updated_date` | `Datetime(time_unit='us', time_zone='UTC')` |

### Sample Data (100000 rows)

```
shape: (100_000, 17)
┌────────────────┬───────┬──────────────┬────────────────┬───┬────────────────┬────────────────┬──────────────┬────────────────┐
│ id             ┆ orcid ┆ display_name ┆ display_name_a ┆ … ┆ counts_by_year ┆ works_api_url  ┆ created_date ┆ updated_date   │
│ ---            ┆ ---   ┆ ---          ┆ lternatives    ┆   ┆ ---            ┆ ---            ┆ ---          ┆ ---            │
│ str            ┆ str   ┆ str          ┆ ---            ┆   ┆ list[struct[3] ┆ str            ┆ date         ┆ datetime[μs,   │
│                ┆       ┆              ┆ list[str]      ┆   ┆ ]              ┆                ┆              ┆ UTC]           │
╞════════════════╪═══════╪══════════════╪════════════════╪═══╪════════════════╪════════════════╪══════════════╪════════════════╡
│ https://openal ┆ null  ┆ Dina Tarek   ┆ []             ┆ … ┆ [{2023,1,0}]   ┆ https://api.op ┆ 2023-06-08   ┆ 2023-06-08     │
│ ex.org/A437973 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 00:00:00 UTC   │
│ 71…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆                │
│ https://openal ┆ null  ┆ Yitian Sun   ┆ []             ┆ … ┆ [{2023,1,0}]   ┆ https://api.op ┆ 2023-06-08   ┆ 2023-06-08     │
│ ex.org/A437973 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 00:00:00 UTC   │
│ 71…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆                │
│ https://openal ┆ null  ┆ Qinghai He   ┆ []             ┆ … ┆ [{2023,1,0}]   ┆ https://api.op ┆ 2023-06-08   ┆ 2023-06-08     │
│ ex.org/A437973 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 00:00:00 UTC   │
│ 71…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆                │
│ https://openal ┆ null  ┆ Hui Li       ┆ []             ┆ … ┆ [{2023,1,0}]   ┆ https://api.op ┆ 2023-06-08   ┆ 2023-06-08     │
│ ex.org/A437973 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 00:00:00 UTC   │
│ 71…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆                │
│ https://openal ┆ null  ┆ Tazi, Faiza  ┆ []             ┆ … ┆ [{2023,1,0}]   ┆ https://api.op ┆ 2023-06-13   ┆ 2023-06-13     │
│ ex.org/A438041 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 00:00:00 UTC   │
│ 48…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆                │
│ …              ┆ …     ┆ …            ┆ …              ┆ … ┆ …              ┆ …              ┆ …            ┆ …              │
│ https://openal ┆ null  ┆ Ien U        ┆ ["Ien U"]      ┆ … ┆ []             ┆ https://api.op ┆ 2023-07-21   ┆ 2024-05-06 22: │
│ ex.org/A504604 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 46:23.212399   │
│ 73…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆ UTC            │
│ https://openal ┆ null  ┆ 山元 一      ┆ ["山元 一"]    ┆ … ┆ [{2017,1,0}]   ┆ https://api.op ┆ 2023-07-21   ┆ 2024-05-06 23: │
│ ex.org/A504604 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 47:58.748772   │
│ 89…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆ UTC            │
│ https://openal ┆ null  ┆ 云丽春       ┆ ["云丽春"]     ┆ … ┆ [{2016,1,0}]   ┆ https://api.op ┆ 2023-07-21   ┆ 2024-05-06 23: │
│ ex.org/A504604 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 32:31.467677   │
│ 92…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆ UTC            │
│ https://openal ┆ null  ┆ 林蔵 飯島    ┆ ["林蔵 飯島"]  ┆ … ┆ []             ┆ https://api.op ┆ 2023-07-21   ┆ 2024-05-06 23: │
│ ex.org/A504604 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 31:30.971961   │
│ 93…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆ UTC            │
│ https://openal ┆ null  ┆ 周荣林       ┆ ["周荣林"]     ┆ … ┆ [{2015,1,0}]   ┆ https://api.op ┆ 2023-07-21   ┆ 2024-05-06 22: │
│ ex.org/A504604 ┆       ┆              ┆                ┆   ┆                ┆ enalex.org/wor ┆              ┆ 25:03.052103   │
│ 95…            ┆       ┆              ┆                ┆   ┆                ┆ ks…            ┆              ┆ UTC            │
└────────────────┴───────┴──────────────┴────────────────┴───┴────────────────┴────────────────┴──────────────┴────────────────┘
```
---

## 2. CONCEPTS

**Dimensions:** 65,073 rows × 19 columns
**Memory usage:** ~229.31 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `wikidata` | `String` |
| 3 | `display_name` | `String` |
| 4 | `level` | `Int64` |
| 5 | `description` | `String` |
| 6 | `works_count` | `Int64` |
| 7 | `cited_by_count` | `Int64` |
| 8 | `summary_stats` | `Struct({'2yr_mean_citedness': Float64, 'h_index': Int64, 'i10_index': Int64, 'oa_percent': Float64, 'works_count': Int64, 'cited_by_count': Int64, '2yr_works_count': Int64, '2yr_cited_by_count': Int64, '2yr_i10_index': Int64, '2yr_h_index': Int64})` |
| 9 | `ids` | `Struct({'openalex': String, 'wikidata': String, 'wikipedia': String, 'umls_aui': List(String), 'umls_cui': List(String), 'mag': Int64})` |
| 10 | `image_url` | `String` |
| 11 | `image_thumbnail_url` | `String` |
| 12 | `international` | `Struct({'display_name': Struct({'zh': String, 'et': String, 'az': String, 'io': String, 'lfn': String, 'olo': String, 'gl': String, 'en': String, 'frr': String, 'hu': String, 'pt-br': String, 'eu': String, 'sco': String, 'tl': String, 'da': String, 'ia': String, 'war': String, 'br': String, 'zh-hans': String, 'zh-cn': String, 'ast': String, 'my': String, 'cy': String, 'is': String, 'en-ca': String, 'sk': String, 'tr': String, 'bn': String, 'el': String, 'he': String, 'mk': String, 'rue': String, 'yue': String, 'sl': String, 'hi': String, 'nn': String, 'kk': String, 'te': String, 'bg': String, 'eo': String, 'es': String, 'ceb': String, 'lzh': String, 'fa': String, 'arz': String, 'oc': String, 'de': String, 'ca': String, 'lv': String, 'sh': String, 'ro': String, 'ru': String, 'it': String, 'hy': String, 'an': String, 'wuu': String, 'af': String, 'ga': String, 'ie': String, 'ms': String, 'ko': String, 'ja': String, 'be-tarask': String, 'ku': String, 'la': String, 'sw': String, 'th': String, 'tt': String, 'vi': String, 'zh-hant': String, 'ar': String, 'sr': String, 'nl': String, 'pl': String, 'kbd': String, 'pt': String, 'ka': String, 'en-gb': String, 'fi': String, 'sq': String, 'lt': String, 'azb': String, 'se': String, 'cs': String, 'hr': String, 'ml': String, 'ext': String, 'sv': String, 'nv': String, 'vo': String, 'ba': String, 'gu': String, 'nb': String, 'zea': String, 'uk': String, 'fy': String, 'id': String, 'ckb': String, 'pnb': String, 'be': String, 'ta': String, 'fr': String, 'kk-arab': String, 'kk-cyrl': String, 'ky': String, 'uz': String, 'kk-latn': String, 'zh-hk': String, 'zh-sg': String, 'zh-tw': String, 'sr-ec': String, 'sr-el': String, 'hsb': String, 'lmo': String, 'os': String, 'pa': String, 'ne': String, 'vec': String, 'ty': String, 'mnw': String, 'su': String, 'nah': String, 'to': String, 'lb': String, 'dag': String, 'mad': String, 'min': String, 'jv': String, 'dsb': String, 'szl': String, 'wa': String, 'kk-tr': String, 'bjn': String, 'new': String, 'mcn': String, 'yi': String, 'tk': String, 'sd': String, 'nqo': String, 'kk-kz': String, 'mr': String, 'lg': String, 'kk-cn': String, 'scn': String, 'de-ch': String, 'eml': String, 'kn': String, 'or': String, 'qu': String, 'tt-cyrl': String, 'crh': String, 'fo': String, 'roa-tara': String, 'ht': String, 'cv': String, 'bs': String, 'hyw': String, 'nan': String, 'so': String, 'yo': String, 'zh-my': String, 'si': String, 'jbo': String, 'gan': String, 'li': String, 'jam': String, 'gcr': String, 'krc': String, 'nso': String, 'hif': String, 'sgs': String, 'tyv': String, 'cu': String, 'fur': String, 'km': String, 'gd': String, 'vls': String, 'ur': String, 'ab': String, 'pap': String, 'mn': String, 'ms-arab': String, 'sc': String, 'nds': String, 'ilo': String, 'gsw': String, 'zh-mo': String, 'as': String, 'ksh': String, 'lij': String, 'ku-arab': String, 'za': String, 'arc': String, 'ku-latn': String, 'kab': String, 'nap': String, 'chr': String, 'mg': String, 'sn': String, 'ps': String, 'bo': String, 'tet': String, 'tg': String, 'tg-latn': String, 'iu': String, 'mdf': String, 'kg': String, 'de-at': String, 'nds-nl': String, 'wo': String, 'rm': String, 'co': String, 'pcd': String, 'pms': String, 'bar': String, 'frp': String, 'nrm': String, 'zu': String, 'simple': String, 'kl': String, 'om': String, 'zgh': String, 'fj': String, 'ha': String, 'xmf': String, 'stq': String, 'ug': String, 'ltg': String, 'bho': String, 'mai': String, 'mi': String, 'inh': String, 'mzn': String, 'sah': String, 'hak': String, 'diq': String, 'ang': String, 'vro': String, 'tt-latn': String, 'pdc': String, 'bpy': String, 'lad': String, 'mhr': String, 'glk': String, 'smn': String, 'cdo': String, 'koi': String, 'gn': String, 'kbp': String, 'ln': String, 'kv': String, 'gom-latn': String, 'bxr': String, 'pi': String, 'gom': String, 'xh': String, 'kw': String, 'am': String, 'mni': String, 'lo': String, 'myv': String, 'gv': String, 'mt': String, 'lld': String, 'tcy': String, 'sms': String, 'pam': String, 'gom-deva': String, 'lez': String, 'vep': String, 'bcl': String, 'haw': String, 'mrj': String, 'ki': String, 'ary': String, 'xal': String, 'ce': String, 'ban': String, 'rup': String, 'es-419': String, 'rmy': String, 'tn': String, 'dtp': String, 'ak': String, 'chy': String, 'udm': String, 'rmf': String, 'sm': String, 'shi': String, 'aeb-arab': String, 'nia': String, 'tpi': String, 'sa': String, 'gpe': String, 'blk': String, 'map-bms': String, 'bew': String, 'st': String, 'btm': String, 'ks': String, 'awa': String, 'crh-ro': String, 'dv': String, 'iba': String, 'mag': String, 'smj': String, 'kaa': String, 'knc': String, 'ch': String, 'tg-cyrl': String, 'av': String, 'gor': String, 'bi': String, 'nov': String, 'tly': String, 'bug': String, 'din': String, 'lrc': String, 'pih': String, 'ss': String, 'sma': String, 'avk': String, 'csb': String, 'ts': String, 'cbk-zam': String, 'skr': String, 'mwl': String, 'crh-latn': String, 'ti': String, 'pfl': String, 'frc': String, 'ay': String, 'bm': String, 'sat': String, 'shn': String, 'tok': String, 'rki': String, 'tum': String, 'ace': String, 'dz': String, 'grc': String, 'srn': String, 'ig': String, 'kge': String, 'sjd': String, 'anp': String, 'tdd': String, 'tw': String, 'pag': String, 've': String, 'dty': String, 'ko-kp': String, 'sg': String, 'pcm': String, 'rw': String, 'en-us': String, 'kcg': String, 'got': String, 'pnt': String, 'guc': String, 'hil': String, 'qug': String, 'ff': String, 'alt': String, 'ng': String, 'bbc': String, 'syl': String, 'als': String, 'ik': String, 'lbe': String, 'ee': String, 'szy': String, 'krj': String, 'ady': String, 'arq': String, 'mo': String, 'gan-hans': String, 'gan-hant': String, 'aeb-latn': String, 'na': String, 'ny': String, 'rn': String, 'gag': String, 'mul': String, 'nr': String, 'tay': String, 'guw': String, 'ami': String, 'fon': String, 'pwn': String, 'trv': String, 'atj': String, 'nys': String, 'mos': String, 'brh': String, 'ryu': String, 'nan-hant': String, 'nan-latn-pehoeji': String, 'dga': String, 'nup': String, 'liv': String, 'kea': String, 'bgn': String, 'nan-hani': String, 'nan-latn-tailo': String, 'cr': String, 'vmf': String, 'kjp': String, 'ban-bali': String, 'aa': String, 'sty': String, 'rsk': String, 'bas': String, 'nod': String, 'ybb': String, 'ann': String, 'arn': String, 'ug-arab': String, 'ug-latn': String, 'agq': String, 'ike-latn': String, 'ike-cans': String, 'bdr': String, 'lzz': String, 'pap-aw': String, 'pdt': String, 'sje': String, 'aeb': String, 'bkh': String, 'bqi': String, 'fmp': String, 'tzm': String, 'ii': String, 'aln': String, 'eto': String, 'ewo': String, 'dua': String, 'wes': String, 'etu': String, 'mcp': String, 'ker': String, 'tvu': String, 'isu': String, 'nnh': String, 'gya': String, 'bbj': String, 'nmg': String, 'lem': String, 'yat': String, 'byv': String, 'bkm': String, 'lns': String, 'mua': String, 'yas': String, 'yav': String, 'bag': String, 'bkc': String, 'vut': String, 'tig': String, 'fit': String, 'sdc': String, 'nla': String, 'lua': String, 'cho': String, 'kus': String, 'ks-arab': String, 'sli': String}), 'description': Struct({'uk': String, 'et': String, 'sco': String, 'zh': String, 'pt-br': String, 'pa': String, 'gl': String, 'en': String, 'hu': String, 'de-at': String, 'eu': String, 'tt-latn': String, 'da': String, 'zh-hans': String, 'zh-cn': String, 'ast': String, 'is': String, 'sk': String, 'en-ca': String, 'tr': String, 'yue': String, 'bn': String, 'el': String, 'he': String, 'mk': String, 'sl': String, 'hi': String, 'nn': String, 'te': String, 'bg': String, 'eo': String, 'es': String, 'tt-cyrl': String, 'fa': String, 'de': String, 'bs': String, 'ca': String, 'lv': String, 'yi': String, 'ro': String, 'ru': String, 'zh-hk': String, 'it': String, 'hy': String, 'an': String, 'yo': String, 'ms': String, 'zh-tw': String, 'ko': String, 'ja': String, 'zh-hant': String, 'sw': String, 'tg-cyrl': String, 'tg-latn': String, 'tt': String, 'lb': String, 'vi': String, 'ar': String, 'sr': String, 'nl': String, 'pl': String, 'zh-my': String, 'pt': String, 'ka': String, 'en-gb': String, 'fi': String, 'sq': String, 'nds': String, 'cs': String, 'hr': String, 'tg': String, 'ml': String, 'sv': String, 'mr': String, 'zh-sg': String, 'min': String, 'li': String, 'gsw': String, 'zh-mo': String, 'gu': String, 'nb': String, 'zea': String, 'de-ch': String, 'as': String, 'fy': String, 'id': String, 'ckb': String, 'kn': String, 'be': String, 'or': String, 'fr': String, 'io': String, 'ia': String, 'cy': String, 'oc': String, 'af': String, 'be-tarask': String, 'la': String, 'scn': String, 'arz': String, 'ta': String, 'ace': String, 'ga': String, 'ne': String, 'th': String, 'nqo': String, 'az': String, 'my': String, 'ilo': String, 'br': String, 'sr-ec': String, 'tl': String, 'gd': String, 'sd': String, 'pcd': String, 'so': String, 'ht': String, 'vo': String, 'hsb': String, 'dag': String, 'udm': String, 'nia': String, 'mt': String, 'pap': String, 'si': String, 'ba': String, 'rmy': String, 'kk': String, 'crh-ro': String, 'bho': String, 'ha': String, 'mag': String, 'vec': String, 'lzh': String, 'om': String, 'sh': String, 'lad': String, 'mi': String, 'bo': String, 'ku': String, 'bar': String, 'ti': String, 'zu': String, 'uz': String, 'aeb-arab': String, 'wa': String, 'rue': String, 'gv': String, 'lfn': String, 'lij': String, 'szl': String, 'nov': String, 'bjn': String, 'ur': String, 'ie': String, 'shi': String, 'kab': String, 'eml': String, 'ary': String, 'ig': String, 'kl': String, 'mai': String, 'sr-el': String, 'lt': String, 'pnb': String, 'mnw': String, 'mn': String, 'en-us': String, 'kcg': String, 'mcn': String, 'new': String, 'co': String, 'ff': String, 'ch': String, 'bm': String, 'nds-nl': String, 'roa-tara': String, 'sat': String, 'sah': String, 'sc': String, 'smn': String, 'zgh': String, 'sms': String, 'se': String, 'fo': String, 'mni': String, 'jam': String, 'sa': String, 'kw': String, 'mdf': String, 'myv': String, 'wuu': String, 'crh': String, 'ps': String, 'gn': String, 'kaa': String, 'am': String, 'jv': String, 'ks': String, 'qu': String, 'kk-cyrl': String, 'ceb': String, 'xmf': String, 'km': String, 'st': String, 'ki': String, 'frr': String, 'ku-latn': String, 'es-419': String, 'sgs': String, 'hif': String, 'ce': String, 'cdo': String, 'pwn': String, 'gpe': String, 'pcm': String, 'nan': String, 'su': String, 'gor': String, 'hak': String, 'syl': String, 'tw': String, 'atj': String, 'kk-kz': String, 'ky': String, 'blk': String, 'shn': String, 'hyw': String, 'ryu': String, 'tok': String, 'vep': String, 'kg': String, 'csb': String, 'lld': String, 'nan-hani': String, 'nan-hant': String, 'nan-latn-pehoeji': String, 'ms-arab': String, 'nan-latn-tailo': String, 'cv': String, 'tk': String, 'dga': String, 'ban': String, 'diq': String, 'nod': String, 'bug': String, 've': String, 'xh': String, 'lo': String, 'nso': String, 'nap': String, 'pms': String, 'ay': String, 'bcl': String, 'azb': String, 'mzn': String, 'ext': String, 'frp': String, 'ty': String, 'wo': String, 'fur': String, 'glk': String, 'av': String, 'lmo': String, 'mg': String, 'arn': String, 'rup': String, 'gcr': String, 'war': String, 'dtp': String, 'kge': String, 'bew': String, 'arq': String, 'tcy': String, 'inh': String, 'ab': String, 'ny': String, 'srn': String, 'pam': String, 'frc': String, 'map-bms': String, 'tpi': String, 'nrm': String, 'stq': String, 'mwl': String, 'os': String, 'ksh': String, 'ts': String, 'vls': String, 'din': String, 'ang': String, 'ku-arab': String, 'avk': String, 'grc': String, 'sn': String, 'tet': String, 'mad': String, 'vmf': String, 'bpy': String, 'bas': String, 'ban-bali': String, 'hil': String, 'pih': String, 'cu': String, 'haw': String, 'sdc': String, 'knc': String, 'mos': String, 'gan-hans': String, 'kea': String, 'ss': String, 'rw': String, 'jbo': String, 'dty': String, 'dsb': String, 'olo': String, 'gan-hant': String, 'bxr': String, 'sje': String, 'smj': String, 'sma': String, 'anp': String, 'krc': String, 'cbk-zam': String, 'aln': String, 'brh': String, 'ee': String, 'kv': String, 'arc': String, 'aeb-latn': String, 'gan': String, 'nys': String, 'iba': String, 'ug': String, 'szy': String, 'ak': String, 'iu': String, 'mhr': String, 'crh-latn': String, 'tay': String, 'bi': String, 'chr': String})})` |
| 13 | `ancestors` | `List(Struct({'id': String, 'wikidata': String, 'display_name': String, 'level': Int64}))` |
| 14 | `related_concepts` | `List(Struct({'id': String, 'wikidata': Null, 'display_name': String, 'level': Int64, 'score': Float64}))` |
| 15 | `counts_by_year` | `List(Struct({'year': Int64, 'works_count': Int64, 'oa_works_count': Int64, 'cited_by_count': Int64}))` |
| 16 | `works_api_url` | `String` |
| 17 | `updated_date` | `String` |
| 18 | `created_date` | `String` |
| 19 | `updated` | `String` |

### Sample Data (100000 rows)

```
shape: (65_073, 19)
┌────────────────┬────────────────┬────────────────┬───────┬───┬────────────────┬───────────────┬──────────────┬───────────────┐
│ id             ┆ wikidata       ┆ display_name   ┆ level ┆ … ┆ works_api_url  ┆ updated_date  ┆ created_date ┆ updated       │
│ ---            ┆ ---            ┆ ---            ┆ ---   ┆   ┆ ---            ┆ ---           ┆ ---          ┆ ---           │
│ str            ┆ str            ┆ str            ┆ i64   ┆   ┆ str            ┆ str           ┆ str          ┆ str           │
╞════════════════╪════════════════╪════════════════╪═══════╪═══╪════════════════╪═══════════════╪══════════════╪═══════════════╡
│ https://openal ┆ https://www.wi ┆ Clausius–Clape ┆ 2     ┆ … ┆ https://api.op ┆ 2023-06-07    ┆ 2016-06-24   ┆ 2023-06-07    │
│ ex.org/C127086 ┆ kidata.org/wik ┆ yron relation  ┆       ┆   ┆ enalex.org/wor ┆               ┆              ┆               │
│ 82…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ Euler's        ┆ 5     ┆ … ┆ https://api.op ┆ 2023-06-07    ┆ 2016-06-24   ┆ 2023-06-07    │
│ ex.org/C144403 ┆ kidata.org/wik ┆ factorization  ┆       ┆   ┆ enalex.org/wor ┆               ┆              ┆               │
│ 53…            ┆ i/…            ┆ method         ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ Coandă effect  ┆ 3     ┆ … ┆ https://api.op ┆ 2023-06-07    ┆ 2016-06-24   ┆ 2023-06-07    │
│ ex.org/C169426 ┆ kidata.org/wik ┆                ┆       ┆   ┆ enalex.org/wor ┆               ┆              ┆               │
│ 31…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ Schmidt        ┆ 5     ┆ … ┆ https://api.op ┆ 2023-06-07    ┆ 2016-06-24   ┆ 2023-06-07    │
│ ex.org/C191463 ┆ kidata.org/wik ┆ decomposition  ┆       ┆   ┆ enalex.org/wor ┆               ┆              ┆               │
│ 24…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ Embryonic      ┆ 4     ┆ … ┆ https://api.op ┆ 2023-06-07    ┆ 2016-06-24   ┆ 2023-06-07    │
│ ex.org/C199789 ┆ kidata.org/wik ┆ diapause       ┆       ┆   ┆ enalex.org/wor ┆               ┆              ┆               │
│ 17…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ …              ┆ …              ┆ …              ┆ …     ┆ … ┆ …              ┆ …             ┆ …            ┆ …             │
│ https://openal ┆ https://www.wi ┆ Low-pressure   ┆ 3     ┆ … ┆ https://api.op ┆ 2025-05-29T02 ┆ 2016-06-24   ┆ 2025-05-29T02 │
│ ex.org/C174711 ┆ kidata.org/wik ┆ area           ┆       ┆   ┆ enalex.org/wor ┆ :00:29.224919 ┆              ┆ :00:29.224919 │
│ 10…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ English        ┆ 3     ┆ … ┆ https://api.op ┆ 2025-05-29T07 ┆ 2020-05-01   ┆ 2025-05-29T07 │
│ ex.org/C301791 ┆ kidata.org/wik ┆ vocabulary     ┆       ┆   ┆ enalex.org/wor ┆ :42:11.956590 ┆              ┆ :42:11.956590 │
│ 46…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ Physiological  ┆ 2     ┆ … ┆ https://api.op ┆ 2025-05-29T10 ┆ 2020-05-01   ┆ 2025-05-29T10 │
│ ex.org/C301788 ┆ kidata.org/wik ┆ saline         ┆       ┆   ┆ enalex.org/wor ┆ :18:08.540259 ┆              ┆ :18:08.540259 │
│ 55…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ Oxygen gas     ┆ 3     ┆ … ┆ https://api.op ┆ 2025-05-30T01 ┆ 2019-12-13   ┆ 2025-05-30T01 │
│ ex.org/C299178 ┆ kidata.org/wik ┆                ┆       ┆   ┆ enalex.org/wor ┆ :44:22.425747 ┆              ┆ :44:22.425747 │
│ 80…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
│ https://openal ┆ https://www.wi ┆ Radar display  ┆ 5     ┆ … ┆ https://api.op ┆ 2025-05-30T09 ┆ 2016-06-24   ┆ 2025-05-30T09 │
│ ex.org/C144695 ┆ kidata.org/wik ┆                ┆       ┆   ┆ enalex.org/wor ┆ :54:44.413199 ┆              ┆ :54:44.413199 │
│ 92…            ┆ i/…            ┆                ┆       ┆   ┆ ks…            ┆               ┆              ┆               │
└────────────────┴────────────────┴────────────────┴───────┴───┴────────────────┴───────────────┴──────────────┴───────────────┘
```
---

## 3. DOMAINS

**Dimensions:** 4 rows × 13 columns
**Memory usage:** ~0.01 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `display_name` | `String` |
| 3 | `description` | `String` |
| 4 | `display_name_alternatives` | `List(String)` |
| 5 | `ids` | `Struct({'wikidata': String, 'wikipedia': String})` |
| 6 | `fields` | `List(Struct({'id': String, 'display_name': String}))` |
| 7 | `siblings` | `List(Struct({'id': String, 'display_name': String}))` |
| 8 | `works_count` | `Int64` |
| 9 | `cited_by_count` | `Int64` |
| 10 | `works_api_url` | `String` |
| 11 | `updated_date` | `String` |
| 12 | `created_date` | `String` |
| 13 | `updated` | `String` |

### Sample Data (100000 rows)

```
shape: (4, 13)
┌───────────────┬───────────────┬───────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬──────────────┐
│ id            ┆ display_name  ┆ description   ┆ display_name ┆ … ┆ works_api_ur ┆ updated_date ┆ created_date ┆ updated      │
│ ---           ┆ ---           ┆ ---           ┆ _alternative ┆   ┆ l            ┆ ---          ┆ ---          ┆ ---          │
│ str           ┆ str           ┆ str           ┆ s            ┆   ┆ ---          ┆ str          ┆ str          ┆ str          │
│               ┆               ┆               ┆ ---          ┆   ┆ str          ┆              ┆              ┆              │
│               ┆               ┆               ┆ list[str]    ┆   ┆              ┆              ┆              ┆              │
╞═══════════════╪═══════════════╪═══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪══════════════╡
│ https://opena ┆ Physical      ┆ branch of     ┆ []           ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/domai ┆ Sciences      ┆ natural       ┆              ┆   ┆ openalex.org ┆ 4:50:55.5830 ┆              ┆ 4:50:55.5830 │
│ ns/3          ┆               ┆ science that… ┆              ┆   ┆ /works…      ┆ 31           ┆              ┆ 31           │
│ https://opena ┆ Health        ┆ branch of     ┆ ["medical    ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/domai ┆ Sciences      ┆ science       ┆ sciences",   ┆   ┆ openalex.org ┆ 4:50:50.4162 ┆              ┆ 4:50:50.4162 │
│ ns/4          ┆               ┆ focused on h… ┆ "biomedic…   ┆   ┆ /works…      ┆ 13           ┆              ┆ 13           │
│ https://opena ┆ Life Sciences ┆ branch of     ┆ ["bioscience ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/domai ┆               ┆ science that  ┆ ",           ┆   ┆ openalex.org ┆ 4:50:55.7209 ┆              ┆ 4:50:55.7209 │
│ ns/1          ┆               ┆ involve…      ┆ "biological  ┆   ┆ /works…      ┆ 15           ┆              ┆ 15           │
│               ┆               ┆               ┆ sci…         ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ Social        ┆ branch of     ┆ ["political  ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/domai ┆ Sciences      ┆ science       ┆ sciences"]   ┆   ┆ openalex.org ┆ 4:50:50.1467 ┆              ┆ 4:50:50.1467 │
│ ns/2          ┆               ┆ focused on s… ┆              ┆   ┆ /works…      ┆ 88           ┆              ┆ 88           │
└───────────────┴───────────────┴───────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴──────────────┘
```
---

## 4. FIELDS

**Dimensions:** 26 rows × 14 columns
**Memory usage:** ~0.16 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `display_name` | `String` |
| 3 | `description` | `String` |
| 4 | `display_name_alternatives` | `List(String)` |
| 5 | `ids` | `Struct({'wikidata': String, 'wikipedia': String})` |
| 6 | `domain` | `Struct({'id': String, 'display_name': String})` |
| 7 | `subfields` | `List(Struct({'id': String, 'display_name': String}))` |
| 8 | `siblings` | `List(Struct({'id': String, 'display_name': String}))` |
| 9 | `works_count` | `Int64` |
| 10 | `cited_by_count` | `Int64` |
| 11 | `works_api_url` | `String` |
| 12 | `updated_date` | `String` |
| 13 | `created_date` | `String` |
| 14 | `updated` | `String` |

### Sample Data (100000 rows)

```
shape: (26, 14)
┌───────────────┬───────────────┬───────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬──────────────┐
│ id            ┆ display_name  ┆ description   ┆ display_name ┆ … ┆ works_api_ur ┆ updated_date ┆ created_date ┆ updated      │
│ ---           ┆ ---           ┆ ---           ┆ _alternative ┆   ┆ l            ┆ ---          ┆ ---          ┆ ---          │
│ str           ┆ str           ┆ str           ┆ s            ┆   ┆ ---          ┆ str          ┆ str          ┆ str          │
│               ┆               ┆               ┆ ---          ┆   ┆ str          ┆              ┆              ┆              │
│               ┆               ┆               ┆ list[str]    ┆   ┆              ┆              ┆              ┆              │
╞═══════════════╪═══════════════╪═══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪══════════════╡
│ https://opena ┆ Medicine      ┆ field of      ┆ ["healthcare ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/field ┆               ┆ study for     ┆ sciences"]   ┆   ┆ openalex.org ┆ 4:37:08.8472 ┆              ┆ 4:37:08.8472 │
│ s/27          ┆               ┆ diagnosing,…  ┆              ┆   ┆ /works…      ┆ 05           ┆              ┆ 05           │
│ https://opena ┆ Biochemistry, ┆ study of      ┆ ["biological ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/field ┆ Genetics and  ┆ chemical      ┆ chemistry",  ┆   ┆ openalex.org ┆ 4:36:42.9595 ┆              ┆ 4:36:42.9595 │
│ s/13          ┆ Mol…          ┆ processes in… ┆ "geno…       ┆   ┆ /works…      ┆ 68           ┆              ┆ 68           │
│ https://opena ┆ Engineering   ┆ practice of   ┆ ["engineerin ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/field ┆               ┆ using natural ┆ g sciences"] ┆   ┆ openalex.org ┆ 4:37:29.7301 ┆              ┆ 4:37:29.7301 │
│ s/22          ┆               ┆ scie…         ┆              ┆   ┆ /works…      ┆ 46           ┆              ┆ 46           │
│ https://opena ┆ Environmental ┆ interdiscipli ┆ ["green      ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/field ┆ Science       ┆ nary field    ┆ science",    ┆   ┆ openalex.org ┆ 4:36:27.2418 ┆              ┆ 4:36:27.2418 │
│ s/23          ┆               ┆ that s…       ┆ "environment ┆   ┆ /works…      ┆ 31           ┆              ┆ 31           │
│               ┆               ┆               ┆ …            ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ Physics and   ┆ study of      ┆ ["general    ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/field ┆ Astronomy     ┆ matter and    ┆ physics",    ┆   ┆ openalex.org ┆ 4:36:37.6131 ┆              ┆ 4:36:37.6131 │
│ s/31          ┆               ┆ its motion…   ┆ "physical …  ┆   ┆ /works…      ┆ 65           ┆              ┆ 65           │
│ …             ┆ …             ┆ …             ┆ …            ┆ … ┆ …            ┆ …            ┆ …            ┆ …            │
│ https://opena ┆ Health        ┆ field         ┆ ["health     ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/field ┆ Professions   ┆ encompassing  ┆ sciences"]   ┆   ┆ openalex.org ┆ 7:54:07.5044 ┆              ┆ 7:54:07.5044 │
│ s/36          ┆               ┆ a wide rang…  ┆              ┆   ┆ /works…      ┆ 62           ┆              ┆ 62           │
│ https://opena ┆ Decision      ┆ branch of     ┆ ["decision   ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/field ┆ Sciences      ┆ applied       ┆ theory",     ┆   ┆ openalex.org ┆ 7:54:06.8232 ┆              ┆ 7:54:06.8232 │
│ s/18          ┆               ┆ probability … ┆ "theory of…  ┆   ┆ /works…      ┆ 61           ┆              ┆ 61           │
│ https://opena ┆ Energy        ┆ study of      ┆ ["energy     ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/field ┆               ┆ energy in     ┆ studies",    ┆   ┆ openalex.org ┆ 7:54:07.3080 ┆              ┆ 7:54:07.3080 │
│ s/21          ┆               ┆ physical sy…  ┆ "energy sci… ┆   ┆ /works…      ┆ 68           ┆              ┆ 68           │
│ https://opena ┆ Dentistry     ┆ branch of     ┆ ["dental     ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/field ┆               ┆ medicine      ┆ medicine",   ┆   ┆ openalex.org ┆ 7:54:07.0820 ┆              ┆ 7:54:07.0820 │
│ s/35          ┆               ┆ dealing wit…  ┆ "oral medi…  ┆   ┆ /works…      ┆ 87           ┆              ┆ 87           │
│ https://opena ┆ Veterinary    ┆ branch of     ┆ ["veterinary ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/field ┆               ┆ medicine that ┆ science",    ┆   ┆ openalex.org ┆ 7:54:07.7076 ┆              ┆ 7:54:07.7076 │
│ s/34          ┆               ┆ deals …       ┆ "veteri…     ┆   ┆ /works…      ┆ 35           ┆              ┆ 35           │
└───────────────┴───────────────┴───────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴──────────────┘
```
---

## 5. FUNDERS

**Dimensions:** 32,437 rows × 17 columns
**Memory usage:** ~28.84 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `display_name` | `String` |
| 3 | `description` | `String` |
| 4 | `alternate_titles` | `List(String)` |
| 5 | `ids` | `Struct({'openalex': String, 'ror': String, 'wikidata': String, 'crossref': String, 'doi': String})` |
| 6 | `country_code` | `String` |
| 7 | `homepage_url` | `String` |
| 8 | `image_url` | `String` |
| 9 | `image_thumbnail_url` | `String` |
| 10 | `works_count` | `Int32` |
| 11 | `cited_by_count` | `Int32` |
| 12 | `grants_count` | `Int32` |
| 13 | `summary_stats` | `Struct({'2yr_mean_citedness': Float64, 'h_index': Int32, 'i10_index': Int32})` |
| 14 | `roles` | `List(Struct({'role': String, 'id': String, 'works_count': Int32}))` |
| 15 | `counts_by_year` | `List(Struct({'year': Int32, 'works_count': Int32, 'cited_by_count': Int32}))` |
| 16 | `created_date` | `String` |
| 17 | `updated_date` | `String` |

### Sample Data (100000 rows)

```
shape: (32_437, 17)
┌───────────────┬───────────────┬───────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬──────────────┐
│ id            ┆ display_name  ┆ description   ┆ alternate_ti ┆ … ┆ roles        ┆ counts_by_ye ┆ created_date ┆ updated_date │
│ ---           ┆ ---           ┆ ---           ┆ tles         ┆   ┆ ---          ┆ ar           ┆ ---          ┆ ---          │
│ str           ┆ str           ┆ str           ┆ ---          ┆   ┆ list[struct[ ┆ ---          ┆ str          ┆ str          │
│               ┆               ┆               ┆ list[str]    ┆   ┆ 3]]          ┆ list[struct[ ┆              ┆              │
│               ┆               ┆               ┆              ┆   ┆              ┆ 3]]          ┆              ┆              │
╞═══════════════╪═══════════════╪═══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪══════════════╡
│ https://opena ┆ National      ┆ Chinese       ┆ ["NNSF of    ┆ … ┆ [{"instituti ┆ [{2024,54398 ┆ 2023-02-13   ┆ 2024-02-07T1 │
│ lex.org/F4320 ┆ Natural       ┆ government    ┆ China",      ┆   ┆ on","https:/ ┆ ,1516422},   ┆              ┆ 7:22:26.1691 │
│ 3210…         ┆ Science       ┆ body          ┆ "Guójiā      ┆   ┆ /opena…      ┆ {2023,3…     ┆              ┆ 32           │
│               ┆ Found…        ┆               ┆ Zìrá…        ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ Associated    ┆ null          ┆ ["AWU",      ┆ … ┆ [{"funder"," ┆ []           ┆ 2023-02-13   ┆ 2024-03-19T1 │
│ lex.org/F4320 ┆ Western       ┆               ┆ "Associated  ┆   ┆ https://open ┆              ┆              ┆ 8:47:45.8615 │
│ 3105…         ┆ Universitie…  ┆               ┆ Western Un…  ┆   ┆ alex.o…      ┆              ┆              ┆ 80           │
│ https://opena ┆ National      ┆ government    ┆ ["National   ┆ … ┆ [{"funder"," ┆ []           ┆ 2023-02-13   ┆ 2024-03-19T1 │
│ lex.org/F4320 ┆ Advisory      ┆ organization  ┆ Advisory     ┆   ┆ https://open ┆              ┆              ┆ 8:55:29.8130 │
│ 3218…         ┆ Council for … ┆ in Aus…       ┆ Council fo…  ┆   ┆ alex.o…      ┆              ┆              ┆ 14           │
│ https://opena ┆ Herman A. and ┆ foundation in ┆ []           ┆ … ┆ [{"funder"," ┆ [{2016,0,1}] ┆ 2023-02-13   ┆ 2024-03-19T2 │
│ lex.org/F4320 ┆ Amelia S.     ┆ United States ┆              ┆   ┆ https://open ┆              ┆              ┆ 1:34:55.7718 │
│ 3092…         ┆ Ehrman…       ┆ of…           ┆              ┆   ┆ alex.o…      ┆              ┆              ┆ 38           │
│ https://opena ┆ Canadian      ┆ null          ┆ ["CITR"]     ┆ … ┆ [{"funder"," ┆ []           ┆ 2023-02-13   ┆ 2024-03-19T1 │
│ lex.org/F4320 ┆ Institute for ┆               ┆              ┆   ┆ https://open ┆              ┆              ┆ 8:38:47.2912 │
│ 3381…         ┆ Telecom…      ┆               ┆              ┆   ┆ alex.o…      ┆              ┆              ┆ 91           │
│ …             ┆ …             ┆ …             ┆ …            ┆ … ┆ …            ┆ …            ┆ …            ┆ …            │
│ https://opena ┆ Clinical      ┆ facility in   ┆ ["CNRC"]     ┆ … ┆ [{"instituti ┆ []           ┆ 2023-02-13   ┆ 2025-05-30T0 │
│ lex.org/F4320 ┆ Nutrition     ┆ Singapore,    ┆              ┆   ┆ on","https:/ ┆              ┆              ┆ 5:56:37.5562 │
│ 3370…         ┆ Research Ce…  ┆ Singapo…      ┆              ┆   ┆ /opena…      ┆              ┆              ┆ 41           │
│ https://opena ┆ Marine Corps  ┆ university    ┆ ["Marine     ┆ … ┆ [{"funder"," ┆ []           ┆ 2023-02-13   ┆ 2025-05-30T0 │
│ lex.org/F4320 ┆ War College   ┆ for the U.S.  ┆ Corps War    ┆   ┆ https://open ┆              ┆              ┆ 5:54:34.9830 │
│ 3376…         ┆               ┆ Marine…       ┆ College at … ┆   ┆ alex.o…      ┆              ┆              ┆ 63           │
│ https://opena ┆ American      ┆ organization  ┆ ["The        ┆ … ┆ [{"publisher ┆ [{2023,1,0}] ┆ 2023-02-13   ┆ 2025-05-30T1 │
│ lex.org/F4320 ┆ Institute of  ┆               ┆ American     ┆   ┆ ","https://o ┆              ┆              ┆ 0:59:29.2386 │
│ 3379…         ┆ Biologic…     ┆               ┆ Institute of ┆   ┆ penale…      ┆              ┆              ┆ 99           │
│               ┆               ┆               ┆ Bi…          ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ Michoud       ┆ NASA rocket   ┆ ["NASA's     ┆ … ┆ [{"funder"," ┆ []           ┆ 2023-02-13   ┆ 2025-05-30T0 │
│ lex.org/F4320 ┆ Assembly      ┆ manufacturing ┆ Michoud      ┆   ┆ https://open ┆              ┆              ┆ 9:50:17.4324 │
│ 3380…         ┆ Facility      ┆ comp…         ┆ Assembly     ┆   ┆ alex.o…      ┆              ┆              ┆ 27           │
│               ┆               ┆               ┆ Faci…        ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ Landstuhl     ┆ U.S. Army     ┆ ["LRMC"]     ┆ … ┆ [{"funder"," ┆ [{2024,1,0}, ┆ 2023-02-13   ┆ 2025-05-30T1 │
│ lex.org/F4320 ┆ Regional      ┆ post and      ┆              ┆   ┆ https://open ┆ {2023,1,0}]  ┆              ┆ 1:06:23.5653 │
│ 3383…         ┆ Medical Cen…  ┆ hospital in…  ┆              ┆   ┆ alex.o…      ┆              ┆              ┆ 92           │
└───────────────┴───────────────┴───────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴──────────────┘
```
---

## 6. PUBLISHERS

**Dimensions:** 10,741 rows × 22 columns
**Memory usage:** ~24.50 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `display_name` | `String` |
| 3 | `ids` | `Struct({'openalex': String, 'wikidata': String, 'ror': String})` |
| 4 | `alternate_titles` | `List(String)` |
| 5 | `parent_publisher` | `String` |
| 6 | `lineage` | `List(String)` |
| 7 | `hierarchy_level` | `Int64` |
| 8 | `country_codes` | `List(String)` |
| 9 | `homepage_url` | `String` |
| 10 | `image_url` | `String` |
| 11 | `image_thumbnail_url` | `String` |
| 12 | `roles` | `List(Struct({'role': String, 'id': String, 'works_count': Int64}))` |
| 13 | `works_count` | `Int64` |
| 14 | `cited_by_count` | `Int64` |
| 15 | `sources_count` | `Int64` |
| 16 | `summary_stats` | `Struct({'2yr_mean_citedness': Float64, 'h_index': Int64, 'i10_index': Int64})` |
| 17 | `counts_by_year` | `List(Struct({'year': Int64, 'works_count': Int64, 'oa_works_count': Int64, 'cited_by_count': Int64}))` |
| 18 | `x_concepts` | `List(Struct({'id': String, 'wikidata': String, 'display_name': String, 'level': Int64, 'score': Float64}))` |
| 19 | `sources_api_url` | `String` |
| 20 | `updated_date` | `String` |
| 21 | `created_date` | `String` |
| 22 | `updated` | `String` |

### Sample Data (100000 rows)

```
shape: (10_741, 22)
┌───────────────┬───────────────┬───────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬──────────────┐
│ id            ┆ display_name  ┆ ids           ┆ alternate_ti ┆ … ┆ sources_api_ ┆ updated_date ┆ created_date ┆ updated      │
│ ---           ┆ ---           ┆ ---           ┆ tles         ┆   ┆ url          ┆ ---          ┆ ---          ┆ ---          │
│ str           ┆ str           ┆ struct[3]     ┆ ---          ┆   ┆ ---          ┆ str          ┆ str          ┆ str          │
│               ┆               ┆               ┆ list[str]    ┆   ┆ str          ┆              ┆              ┆              │
╞═══════════════╪═══════════════╪═══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪══════════════╡
│ https://opena ┆ INFAD         ┆ {"https://ope ┆ []           ┆ … ┆ https://api. ┆ 2023-06-07   ┆ 2023-04-20   ┆ 2023-06-07   │
│ lex.org/P4366 ┆ Association   ┆ nalex.org/P43 ┆              ┆   ┆ openalex.org ┆              ┆              ┆              │
│ 3058…         ┆               ┆ 6630…         ┆              ┆   ┆ /sourc…      ┆              ┆              ┆              │
│ https://opena ┆ Centro de     ┆ {"https://ope ┆ []           ┆ … ┆ https://api. ┆ 2023-06-07   ┆ 2023-01-01   ┆ 2023-06-07   │
│ lex.org/P4310 ┆ Estudios de   ┆ nalex.org/P43 ┆              ┆   ┆ openalex.org ┆              ┆              ┆              │
│ 3224…         ┆ Historia…     ┆ 1032…         ┆              ┆   ┆ /sourc…      ┆              ┆              ┆              │
│ https://opena ┆ Diretório     ┆ {"https://ope ┆ []           ┆ … ┆ https://api. ┆ 2023-06-07   ┆ 2023-01-01   ┆ 2023-06-07   │
│ lex.org/P4310 ┆ Acadêmico de  ┆ nalex.org/P43 ┆              ┆   ┆ openalex.org ┆              ┆              ┆              │
│ 3120…         ┆ Letras        ┆ 1031…         ┆              ┆   ┆ /sourc…      ┆              ┆              ┆              │
│ https://opena ┆ Gabriel       ┆ {"https://ope ┆ []           ┆ … ┆ https://api. ┆ 2023-06-07   ┆ 2023-01-01   ┆ 2023-06-07   │
│ lex.org/P4310 ┆ Dumont        ┆ nalex.org/P43 ┆              ┆   ┆ openalex.org ┆              ┆              ┆              │
│ 3130…         ┆ Institute     ┆ 1031…         ┆              ┆   ┆ /sourc…      ┆              ┆              ┆              │
│ https://opena ┆ Muzeum Małego ┆ {"https://ope ┆ []           ┆ … ┆ https://api. ┆ 2023-06-07   ┆ 2023-01-01   ┆ 2023-06-07   │
│ lex.org/P4310 ┆ Miasta w      ┆ nalex.org/P43 ┆              ┆   ┆ openalex.org ┆              ┆              ┆              │
│ 3173…         ┆ Bieżuni…      ┆ 1031…         ┆              ┆   ┆ /sourc…      ┆              ┆              ┆              │
│ …             ┆ …             ┆ …             ┆ …            ┆ … ┆ …            ┆ …            ┆ …            ┆ …            │
│ https://opena ┆ The           ┆ {"https://ope ┆ ["Geological ┆ … ┆ https://api. ┆ 2025-05-30T1 ┆ 2023-04-03   ┆ 2025-05-30T1 │
│ lex.org/P4361 ┆ Geological    ┆ nalex.org/P43 ┆ Society",    ┆   ┆ openalex.org ┆ 1:31:59.8778 ┆              ┆ 1:31:59.8778 │
│ 7275…         ┆ Society       ┆ 6172…         ┆ "The Ge…     ┆   ┆ /sourc…      ┆ 42           ┆              ┆ 42           │
│ https://opena ┆ Pomeranian    ┆ {"https://ope ┆ ["Pomorski   ┆ … ┆ https://api. ┆ 2025-05-30T0 ┆ 2023-04-10   ┆ 2025-05-30T0 │
│ lex.org/P4362 ┆ Medical       ┆ nalex.org/P43 ┆ Uniwersytet  ┆   ┆ openalex.org ┆ 4:59:37.3227 ┆              ┆ 4:59:37.3227 │
│ 7248…         ┆ University    ┆ 6272…         ┆ Medyczn…     ┆   ┆ /sourc…      ┆ 97           ┆              ┆ 97           │
│ https://opena ┆ College of    ┆ {"https://ope ┆ ["College of ┆ … ┆ https://api. ┆ 2025-05-30T1 ┆ 2023-04-18   ┆ 2025-05-30T1 │
│ lex.org/P4366 ┆ Intensive     ┆ nalex.org/P43 ┆ Intensive    ┆   ┆ openalex.org ┆ 1:34:41.5566 ┆              ┆ 1:34:41.5566 │
│ 0648…         ┆ Care Medi…    ┆ 6606…         ┆ Care Me…     ┆   ┆ /sourc…      ┆ 85           ┆              ┆ 85           │
│ https://opena ┆ Shanghai      ┆ {"https://ope ┆ ["Shànghǎi   ┆ … ┆ https://api. ┆ 2025-05-30T1 ┆ 2023-04-20   ┆ 2025-05-30T1 │
│ lex.org/P4366 ┆ University    ┆ nalex.org/P43 ┆ Dàxué"]      ┆   ┆ openalex.org ┆ 1:34:05.6487 ┆              ┆ 1:34:05.6487 │
│ 3058…         ┆               ┆ 6630…         ┆              ┆   ┆ /sourc…      ┆ 27           ┆              ┆ 27           │
│ https://opena ┆ Institute of  ┆ {"https://ope ┆ ["IHEEM"]    ┆ … ┆ https://api. ┆ 2025-05-30T1 ┆ 2023-04-21   ┆ 2025-05-30T1 │
│ lex.org/P4366 ┆ Healthcare    ┆ nalex.org/P43 ┆              ┆   ┆ openalex.org ┆ 0:48:32.5141 ┆              ┆ 0:48:32.5141 │
│ 3710…         ┆ Engine…       ┆ 6637…         ┆              ┆   ┆ /sourc…      ┆ 37           ┆              ┆ 37           │
└───────────────┴───────────────┴───────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴──────────────┘
```
---

## 7. SOURCES

**Dimensions:** 260,798 rows × 27 columns
**Memory usage:** ~163.36 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `display_name` | `String` |
| 3 | `abbreviated_title` | `String` |
| 4 | `ids` | `Struct({'openalex': String, 'issn_l': String, 'issn': List(String), 'mag': Int64, 'fatcat': String, 'wikidata': String})` |
| 5 | `issn_l` | `String` |
| 6 | `issn` | `List(String)` |
| 7 | `alternate_titles` | `List(String)` |
| 8 | `host_organization` | `String` |
| 9 | `host_organization_name` | `String` |
| 10 | `host_organization_lineage` | `List(String)` |
| 11 | `country_code` | `String` |
| 12 | `homepage_url` | `String` |
| 13 | `type` | `String` |
| 14 | `is_oa` | `Boolean` |
| 15 | `is_in_doaj` | `Boolean` |
| 16 | `is_core` | `Boolean` |
| 17 | `apc_prices` | `List(Struct({'price': Int32, 'currency': String}))` |
| 18 | `apc_usd` | `Int32` |
| 19 | `societies` | `List(Struct({'url': String, 'organization': String}))` |
| 20 | `summary_stats` | `Struct({'2yr_mean_citedness': Float64, 'h_index': Int32, 'i10_index': Int32})` |
| 21 | `works_count` | `Int32` |
| 22 | `cited_by_count` | `Int32` |
| 23 | `counts_by_year` | `List(Struct({'year': Int32, 'works_count': Int32, 'cited_by_count': Int32}))` |
| 24 | `x_concepts` | `List(Struct({'id': String, 'wikidata': String, 'display_name': String, 'level': Int32, 'score': Float64}))` |
| 25 | `works_api_url` | `String` |
| 26 | `created_date` | `String` |
| 27 | `updated_date` | `String` |

### Sample Data (100000 rows)

```
shape: (100_000, 27)
┌───────────────┬───────────────┬───────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬──────────────┐
│ id            ┆ display_name  ┆ abbreviated_t ┆ ids          ┆ … ┆ x_concepts   ┆ works_api_ur ┆ created_date ┆ updated_date │
│ ---           ┆ ---           ┆ itle          ┆ ---          ┆   ┆ ---          ┆ l            ┆ ---          ┆ ---          │
│ str           ┆ str           ┆ ---           ┆ struct[6]    ┆   ┆ list[struct[ ┆ ---          ┆ str          ┆ str          │
│               ┆               ┆ str           ┆              ┆   ┆ 5]]          ┆ str          ┆              ┆              │
╞═══════════════╪═══════════════╪═══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪══════════════╡
│ https://opena ┆ Revista ibero ┆ Rev. iberoam. ┆ {"https://op ┆ … ┆ [{"https://o ┆ https://api. ┆ 2022-02-03   ┆ 2023-08-02   │
│ lex.org/S4210 ┆ americana de  ┆ bioecon.      ┆ enalex.org/S ┆   ┆ penalex.org/ ┆ openalex.org ┆              ┆              │
│ 2377…         ┆ bioe…         ┆ cambio …      ┆ 421023…      ┆   ┆ C14236…      ┆ /works…      ┆              ┆              │
│ https://opena ┆ npj           ┆ npj Biol.     ┆ {"https://op ┆ … ┆ []           ┆ https://api. ┆ 2024-11-07   ┆ 2024-11-08T0 │
│ lex.org/S4404 ┆ Biological    ┆ Phys. Mech.   ┆ enalex.org/S ┆   ┆              ┆ openalex.org ┆              ┆ 1:58:21.8288 │
│ 1269…         ┆ Physics and   ┆               ┆ 440412…      ┆   ┆              ┆ /works…      ┆              ┆ 50           │
│               ┆ Mec…          ┆               ┆              ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ npj           ┆ npj Biol.     ┆ {"https://op ┆ … ┆ []           ┆ https://api. ┆ 2024-11-07   ┆ 2024-11-08T0 │
│ lex.org/S4404 ┆ Biological    ┆ Phys. Mech.   ┆ enalex.org/S ┆   ┆              ┆ openalex.org ┆              ┆ 2:03:28.8936 │
│ 1270…         ┆ Physics and   ┆               ┆ 440412…      ┆   ┆              ┆ /works…      ┆              ┆ 89           │
│               ┆ Mec…          ┆               ┆              ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ Journal of    ┆ null          ┆ {"https://op ┆ … ┆ []           ┆ https://api. ┆ 2024-11-21   ┆ 2024-11-21T1 │
│ lex.org/S4404 ┆ energy        ┆               ┆ enalex.org/S ┆   ┆              ┆ openalex.org ┆              ┆ 3:28:12.0020 │
│ 5717…         ┆ resources te… ┆               ┆ 440457…      ┆   ┆              ┆ /works…      ┆              ┆ 64           │
│ https://opena ┆ Jurnal Alaqoh ┆ Jurnal Alaqoh ┆ {"https://op ┆ … ┆ []           ┆ https://api. ┆ 2024-11-25   ┆ 2024-11-25T2 │
│ lex.org/S4404 ┆               ┆               ┆ enalex.org/S ┆   ┆              ┆ openalex.org ┆              ┆ 0:35:20.2357 │
│ 6735…         ┆               ┆               ┆ 440467…      ┆   ┆              ┆ /works…      ┆              ┆ 13           │
│ …             ┆ …             ┆ …             ┆ …            ┆ … ┆ …            ┆ …            ┆ …            ┆ …            │
│ https://opena ┆ Revue         ┆ null          ┆ {"https://op ┆ … ┆ [{"https://o ┆ https://api. ┆ 2022-10-17   ┆ 2025-05-18T2 │
│ lex.org/S4306 ┆ générale du   ┆               ┆ enalex.org/S ┆   ┆ penalex.org/ ┆ openalex.org ┆              ┆ 1:54:20.2413 │
│ 5283…         ┆ caoutchouc e… ┆               ┆ 430652…      ┆   ┆ C13888…      ┆ /works…      ┆              ┆ 73           │
│ https://opena ┆ Rocznik       ┆ null          ┆ {"https://op ┆ … ┆ [{"https://o ┆ https://api. ┆ 2022-10-17   ┆ 2025-05-18T1 │
│ lex.org/S4306 ┆ Lwowski       ┆               ┆ enalex.org/S ┆   ┆ penalex.org/ ┆ openalex.org ┆              ┆ 6:42:31.5704 │
│ 5287…         ┆               ┆               ┆ 430652…      ┆   ┆ C13888…      ┆ /works…      ┆              ┆ 79           │
│ https://opena ┆ Salud Jalisco ┆ null          ┆ {"https://op ┆ … ┆ [{"https://o ┆ https://api. ┆ 2022-10-17   ┆ 2025-05-18T1 │
│ lex.org/S4306 ┆               ┆               ┆ enalex.org/S ┆   ┆ penalex.org/ ┆ openalex.org ┆              ┆ 5:02:10.6577 │
│ 5290…         ┆               ┆               ┆ 430652…      ┆   ┆ C71924…      ┆ /works…      ┆              ┆ 77           │
│ https://opena ┆ 학교수학 =    ┆ null          ┆ {"https://op ┆ … ┆ [{"https://o ┆ https://api. ┆ 2022-10-17   ┆ 2025-05-18T1 │
│ lex.org/S4306 ┆ School        ┆               ┆ enalex.org/S ┆   ┆ penalex.org/ ┆ openalex.org ┆              ┆ 0:44:54.0446 │
│ 5291…         ┆ Mathematics   ┆               ┆ 430652…      ┆   ┆ C41008…      ┆ /works…      ┆              ┆ 11           │
│ https://opena ┆ SEMINÁRIO     ┆ null          ┆ {"https://op ┆ … ┆ [{"https://o ┆ https://api. ┆ 2022-10-17   ┆ 2025-05-18T2 │
│ lex.org/S4306 ┆ INTEGRADO -   ┆               ┆ enalex.org/S ┆   ┆ penalex.org/ ┆ openalex.org ┆              ┆ 0:57:34.8086 │
│ 5295…         ┆ ISSN 198…     ┆               ┆ 430652…      ┆   ┆ C13888…      ┆ /works…      ┆              ┆ 41           │
└───────────────┴───────────────┴───────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴──────────────┘
```
---

## 8. SUBFIELDS

**Dimensions:** 252 rows × 15 columns
**Memory usage:** ~3.98 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `display_name` | `String` |
| 3 | `description` | `String` |
| 4 | `display_name_alternatives` | `List(String)` |
| 5 | `ids` | `Struct({'wikidata': String, 'wikipedia': String})` |
| 6 | `field` | `Struct({'id': String, 'display_name': String})` |
| 7 | `domain` | `Struct({'id': String, 'display_name': String})` |
| 8 | `topics` | `List(Struct({'id': String, 'display_name': String}))` |
| 9 | `siblings` | `List(Struct({'id': String, 'display_name': String}))` |
| 10 | `works_count` | `Int64` |
| 11 | `cited_by_count` | `Int64` |
| 12 | `works_api_url` | `String` |
| 13 | `updated_date` | `String` |
| 14 | `created_date` | `String` |
| 15 | `updated` | `String` |

### Sample Data (100000 rows)

```
shape: (252, 15)
┌───────────────┬───────────────┬───────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬──────────────┐
│ id            ┆ display_name  ┆ description   ┆ display_name ┆ … ┆ works_api_ur ┆ updated_date ┆ created_date ┆ updated      │
│ ---           ┆ ---           ┆ ---           ┆ _alternative ┆   ┆ l            ┆ ---          ┆ ---          ┆ ---          │
│ str           ┆ str           ┆ str           ┆ s            ┆   ┆ ---          ┆ str          ┆ str          ┆ str          │
│               ┆               ┆               ┆ ---          ┆   ┆ str          ┆              ┆              ┆              │
│               ┆               ┆               ┆ list[str]    ┆   ┆              ┆              ┆              ┆              │
╞═══════════════╪═══════════════╪═══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪══════════════╡
│ https://opena ┆ Pathology and ┆ study and     ┆ []           ┆ … ┆ https://api. ┆ 2024-03-18T0 ┆ 2024-01-23   ┆ 2024-03-18T0 │
│ lex.org/subfi ┆ Forensic      ┆ diagnosis of  ┆              ┆   ┆ openalex.org ┆ 5:16:20.1004 ┆              ┆ 5:16:20.1004 │
│ elds…         ┆ Medicin…      ┆ disease       ┆              ┆   ┆ /works…      ┆ 81           ┆              ┆ 81           │
│ https://opena ┆ Economics and ┆ social        ┆ ["economics  ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/subfi ┆ Econometrics  ┆ science that  ┆ as a         ┆   ┆ openalex.org ┆ 4:29:03.1269 ┆              ┆ 4:29:03.1269 │
│ elds…         ┆               ┆ studies th…   ┆ science"]    ┆   ┆ /works…      ┆ 82           ┆              ┆ 82           │
│ https://opena ┆ Infectious    ┆ disease       ┆ ["pestilence ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/subfi ┆ Diseases      ┆ caused by     ┆ ", "disease  ┆   ┆ openalex.org ┆ 4:29:24.1257 ┆              ┆ 4:29:24.1257 │
│ elds…         ┆               ┆ infection of… ┆ by inf…      ┆   ┆ /works…      ┆ 82           ┆              ┆ 82           │
│ https://opena ┆ Electronic,   ┆ substance     ┆ ["substance  ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/subfi ┆ Optical and   ┆ that can      ┆ with uniform ┆   ┆ openalex.org ┆ 4:28:52.7492 ┆              ┆ 4:28:52.7492 │
│ elds…         ┆ Magnet…       ┆ occur in di…  ┆ chara…       ┆   ┆ /works…      ┆ 46           ┆              ┆ 46           │
│ https://opena ┆ Developmental ┆ scientific    ┆ []           ┆ … ┆ https://api. ┆ 2024-04-01T0 ┆ 2024-01-23   ┆ 2024-04-01T0 │
│ lex.org/subfi ┆ and           ┆ study of      ┆              ┆   ┆ openalex.org ┆ 4:29:24.8678 ┆              ┆ 4:29:24.8678 │
│ elds…         ┆ Educational … ┆ changes th…   ┆              ┆   ┆ /works…      ┆ 50           ┆              ┆ 50           │
│ …             ┆ …             ┆ …             ┆ …            ┆ … ┆ …            ┆ …            ┆ …            ┆ …            │
│ https://opena ┆ General Arts  ┆ study of the  ┆ ["arts and   ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/subfi ┆ and           ┆ products of   ┆ humanities"] ┆   ┆ openalex.org ┆ 7:54:43.3235 ┆              ┆ 7:54:43.3235 │
│ elds…         ┆ Humanities    ┆ human…        ┆              ┆   ┆ /works…      ┆ 10           ┆              ┆ 10           │
│ https://opena ┆ Life-span and ┆ duration of   ┆ ["life       ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/subfi ┆ Life-course   ┆ life for an   ┆ span",       ┆   ┆ openalex.org ┆ 7:54:49.9108 ┆              ┆ 7:54:49.9108 │
│ elds…         ┆ Stud…         ┆ organi…       ┆ "lifespan"]  ┆   ┆ /works…      ┆ 54           ┆              ┆ 54           │
│ https://opena ┆ Medical       ┆ language used ┆ ["terminolog ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/subfi ┆ Terminology   ┆ in the field  ┆ y of         ┆   ┆ openalex.org ┆ 7:54:18.8800 ┆              ┆ 7:54:18.8800 │
│ elds…         ┆               ┆ of …          ┆ medicine"]   ┆   ┆ /works…      ┆ 56           ┆              ┆ 56           │
│ https://opena ┆ Nuclear       ┆ power         ┆ ["nuclear    ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/subfi ┆ Energy and    ┆ generated     ┆ energy",     ┆   ┆ openalex.org ┆ 7:54:22.6820 ┆              ┆ 7:54:22.6820 │
│ elds…         ┆ Engineering   ┆ from nuclear  ┆ "atomic ene… ┆   ┆ /works…      ┆ 87           ┆              ┆ 87           │
│               ┆               ┆ r…            ┆              ┆   ┆              ┆              ┆              ┆              │
│ https://opena ┆ Drug          ┆ the process   ┆ []           ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/subfi ┆ Discovery     ┆ by which new  ┆              ┆   ┆ openalex.org ┆ 7:54:26.0253 ┆              ┆ 7:54:26.0253 │
│ elds…         ┆               ┆ candi…        ┆              ┆   ┆ /works…      ┆ 04           ┆              ┆ 04           │
└───────────────┴───────────────┴───────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴──────────────┘
```
---

## 9. TOPICS

**Dimensions:** 4,516 rows × 15 columns
**Memory usage:** ~126.53 MB (sample)

### Schema

| # | Column Name | Data Type |
|---|-------------|-----------|
| 1 | `id` | `String` |
| 2 | `display_name` | `String` |
| 3 | `subfield` | `Struct({'id': String, 'display_name': String})` |
| 4 | `field` | `Struct({'id': String, 'display_name': String})` |
| 5 | `domain` | `Struct({'id': String, 'display_name': String})` |
| 6 | `description` | `String` |
| 7 | `keywords` | `List(String)` |
| 8 | `ids` | `Struct({'openalex': String, 'wikipedia': String})` |
| 9 | `siblings` | `List(Struct({'id': String, 'display_name': String}))` |
| 10 | `works_count` | `Int64` |
| 11 | `cited_by_count` | `Int64` |
| 12 | `works_api_url` | `String` |
| 13 | `updated_date` | `String` |
| 14 | `created_date` | `String` |
| 15 | `updated` | `String` |

### Sample Data (100000 rows)

```
shape: (4_516, 15)
┌───────────────┬───────────────┬───────────────┬──────────────┬───┬──────────────┬──────────────┬──────────────┬──────────────┐
│ id            ┆ display_name  ┆ subfield      ┆ field        ┆ … ┆ works_api_ur ┆ updated_date ┆ created_date ┆ updated      │
│ ---           ┆ ---           ┆ ---           ┆ ---          ┆   ┆ l            ┆ ---          ┆ ---          ┆ ---          │
│ str           ┆ str           ┆ struct[2]     ┆ struct[2]    ┆   ┆ ---          ┆ str          ┆ str          ┆ str          │
│               ┆               ┆               ┆              ┆   ┆ str          ┆              ┆              ┆              │
╞═══════════════╪═══════════════╪═══════════════╪══════════════╪═══╪══════════════╪══════════════╪══════════════╪══════════════╡
│ https://opena ┆ Pelvic Floor  ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2024-03-04T0 ┆ 2024-01-23   ┆ 2024-03-04T0 │
│ lex.org/T1041 ┆ Disorders     ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 5:03:34.2697 ┆              ┆ 5:03:34.2697 │
│ 8             ┆               ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 22           ┆              ┆ 22           │
│ https://opena ┆ Gamma-Aminobu ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2024-03-04T0 ┆ 2024-01-23   ┆ 2024-03-04T0 │
│ lex.org/T1314 ┆ tyric Acid    ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 4:59:34.2879 ┆              ┆ 4:59:34.2879 │
│ 2             ┆ Metabo…       ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 41           ┆              ┆ 41           │
│ https://opena ┆ Financing of  ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2024-03-04T0 ┆ 2024-01-23   ┆ 2024-03-04T0 │
│ lex.org/T1153 ┆ Health Care   ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 5:02:08.0369 ┆              ┆ 5:02:08.0369 │
│ 1             ┆ Syste…        ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 58           ┆              ┆ 58           │
│ https://opena ┆ Evolutionary  ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2024-03-11T0 ┆ 2024-01-23   ┆ 2024-03-11T0 │
│ lex.org/T1200 ┆ History of    ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 5:10:46.6576 ┆              ┆ 5:10:46.6576 │
│ 1             ┆ Insect…       ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 55           ┆              ┆ 55           │
│ https://opena ┆ Oral History  ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2024-03-18T0 ┆ 2024-01-23   ┆ 2024-03-18T0 │
│ lex.org/T1359 ┆ and           ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 5:25:00.3146 ┆              ┆ 5:25:00.3146 │
│ 0             ┆ Narratives    ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 84           ┆              ┆ 84           │
│               ┆ in…           ┆               ┆              ┆   ┆              ┆              ┆              ┆              │
│ …             ┆ …             ┆ …             ┆ …            ┆ … ┆ …            ┆ …            ┆ …            ┆ …            │
│ https://opena ┆ Afro-Latin    ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/T1386 ┆ American      ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 7:59:52.2582 ┆              ┆ 7:59:52.2582 │
│ 8             ┆ Studies       ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 72           ┆              ┆ 72           │
│ https://opena ┆ Innovative    ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/T1388 ┆ Education     ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 8:10:37.9514 ┆              ┆ 8:10:37.9514 │
│ 0             ┆ Methods a…    ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 21           ┆              ┆ 21           │
│ https://opena ┆ COVID-19,     ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/T1444 ┆ Geopolitics,  ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 8:01:28.1592 ┆              ┆ 8:01:28.1592 │
│ 3             ┆ Technol…      ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 71           ┆              ┆ 71           │
│ https://opena ┆ Education     ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/T1343 ┆ Methods and   ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 8:08:05.6686 ┆              ┆ 8:08:05.6686 │
│ 1             ┆ Integrat…     ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 99           ┆              ┆ 99           │
│ https://opena ┆ Governance,   ┆ {"https://ope ┆ {"https://op ┆ … ┆ https://api. ┆ 2025-05-26T0 ┆ 2024-01-23   ┆ 2025-05-26T0 │
│ lex.org/T1361 ┆ Compliance,   ┆ nalex.org/sub ┆ enalex.org/f ┆   ┆ openalex.org ┆ 8:08:10.8062 ┆              ┆ 8:08:10.8062 │
│ 6             ┆ and Su…       ┆ fiel…         ┆ ields/…      ┆   ┆ /works…      ┆ 82           ┆              ┆ 82           │
└───────────────┴───────────────┴───────────────┴──────────────┴───┴──────────────┴──────────────┴──────────────┴──────────────┘
```

🎉 Entity inspection completed!
