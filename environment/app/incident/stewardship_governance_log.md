# Planning governance log

How the party-linkage engine is *meant* to behave -- the recovery of the truncated party master, normalisation, blocking, pair scoring, the do-not-merge register, cluster formation and survivorship -- was settled incrementally by the data stewardship board, and those decisions live in the review entries below, not in any single summary. Several stages deliberately deviate from a textbook linkage run. The February draft proposals were revisited during the 2026-05 stewardship review and several were reversed; where a draft or interim conflicts with a later decision, the later dated decision governs. `/app/docs/match_contract.json` is the output contract only.

- 2026-02-17: Stewardship stand-up recorded a routine note against the portal sign-up path for window 1002. The manual review backlog was cleared with no amendment raised.

> **Recovery draft proposal (2026-02-06 - #MDM-3020)** Rosa: rebuild the truncated master by concatenating the pre-migration extract with the change journal and keeping the last record seen for each id; a withdrawn record is simply absent and a reinstatement re-reads it from the extract *(Superseded -- reversed in the 2026-05 stewardship review.)*

> **Recovery draft proposal (2026-02-13 - #MDM-3026)** Anders: candidate pairs are drawn across the whole file, since blocking risks missing a match whose key differs *(Superseded -- reversed in the 2026-05 stewardship review.)*

> **Recovery draft proposal (2026-02-19 - #MDM-3032)** Marek: where several records survive a merge the LATEST loaded record is the survivor, being the freshest view of the party *(Superseded -- reversed in the 2026-05 stewardship review.)*

- 2026-02-23: Steward on duty logged a routine observation for the billing extract during review window 1003. Duplicate-rate drift reviewed; no policy change requested.

- 2026-02-02: Stewardship stand-up recorded a routine note against the legacy import queue for window 1006. The manual review backlog was cleared with no amendment raised.

- 2026-02-16: Data-quality desk noted a rise in incomplete addresses from the CRM feed in window 1007. Raised with the source owner; the matching parameters were not touched.

- 2026-02-04: Steward on duty logged a routine observation for the portal sign-up path during review window 1009. Duplicate-rate drift reviewed; no policy change requested.

- 2026-02-09: Steward on duty logged a routine observation for the CRM feed during review window 1010. Duplicate-rate drift reviewed; no policy change requested.

- 2026-02-20: Governance review of the billing extract in window 1011 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-07: Stewardship stand-up recorded a routine note against the portal sign-up path for window 1012. The manual review backlog was cleared with no amendment raised.

- 2026-02-19: Stewardship stand-up recorded a routine note against the address-cleansing service for window 1014. The manual review backlog was cleared with no amendment raised.

- 2026-02-19: Governance review of the address-cleansing service in window 1016 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-12: Steward on duty logged a routine observation for the CRM feed during review window 1019. Duplicate-rate drift reviewed; no policy change requested.

- 2026-02-26: Data-quality desk noted a rise in incomplete addresses from the CRM feed in window 1021. Raised with the source owner; the matching parameters were not touched.

- 2026-02-07: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1024. Raised with the source owner; the matching parameters were not touched.

- 2026-02-03: Stewardship stand-up recorded a routine note against the portal sign-up path for window 1026. The manual review backlog was cleared with no amendment raised.

- 2026-02-23: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1027. Raised with the source owner; the matching parameters were not touched.

- 2026-02-23: Stewardship stand-up recorded a routine note against the CRM feed for window 1030. The manual review backlog was cleared with no amendment raised.

- 2026-02-02: Governance review of the CRM feed in window 1031 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-12: Stewardship stand-up recorded a routine note against the CRM feed for window 1034. The manual review backlog was cleared with no amendment raised.

- 2026-02-11: Steward on duty logged a routine observation for the address-cleansing service during review window 1036. Duplicate-rate drift reviewed; no policy change requested.

- 2026-02-02: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1037. Raised with the source owner; the matching parameters were not touched.

- 2026-02-25: Governance review of the CRM feed in window 1040 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-04: Steward on duty logged a routine observation for the address-cleansing service during review window 1042. Duplicate-rate drift reviewed; no policy change requested.

- 2026-02-24: Data-quality desk noted a rise in incomplete addresses from the address-cleansing service in window 1045. Raised with the source owner; the matching parameters were not touched.

- 2026-02-08: Governance review of the legacy import queue in window 1048 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-02: Stewardship stand-up recorded a routine note against the billing extract for window 1050. The manual review backlog was cleared with no amendment raised.

> **Interim decision (2026-03-05 - #MDM-3044)** Priya: a pair on the do-not-merge register is skipped silently and not reported *(Revised -- see the 2026-05 stewardship review.)*

- 2026-03-08: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1053. Raised with the source owner; the matching parameters were not touched.

- 2026-03-04: Stewardship stand-up recorded a routine note against the legacy import queue for window 1056. The manual review backlog was cleared with no amendment raised.

- 2026-03-08: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1057. Raised with the source owner; the matching parameters were not touched.

- 2026-03-22: Stewardship stand-up recorded a routine note against the legacy import queue for window 1060. The manual review backlog was cleared with no amendment raised.

- 2026-03-20: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1061. Raised with the source owner; the matching parameters were not touched.

- 2026-03-23: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1062. Raised with the source owner; the matching parameters were not touched.

- 2026-03-12: Stewardship stand-up recorded a routine note against the address-cleansing service for window 1063. The manual review backlog was cleared with no amendment raised.

- 2026-03-25: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1064. Raised with the source owner; the matching parameters were not touched.

- 2026-03-10: Stewardship stand-up recorded a routine note against the address-cleansing service for window 1065. The manual review backlog was cleared with no amendment raised.

- 2026-03-18: Governance review of the CRM feed in window 1066 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-06: Stewardship stand-up recorded a routine note against the billing extract for window 1069. The manual review backlog was cleared with no amendment raised.

- 2026-03-04: Steward on duty logged a routine observation for the legacy import queue during review window 1070. Duplicate-rate drift reviewed; no policy change requested.

- 2026-03-19: Governance review of the address-cleansing service in window 1071 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-25: Steward on duty logged a routine observation for the address-cleansing service during review window 1074. Duplicate-rate drift reviewed; no policy change requested.

- 2026-03-03: Data-quality desk noted a rise in incomplete addresses from the address-cleansing service in window 1077. Raised with the source owner; the matching parameters were not touched.

- 2026-03-27: Data-quality desk noted a rise in incomplete addresses from the portal sign-up path in window 1079. Raised with the source owner; the matching parameters were not touched.

- 2026-03-04: Data-quality desk noted a rise in incomplete addresses from the portal sign-up path in window 1080. Raised with the source owner; the matching parameters were not touched.

- 2026-04-11: Data-quality desk noted a rise in incomplete addresses from the CRM feed in window 1082. Raised with the source owner; the matching parameters were not touched.

- 2026-04-01: Governance review of the legacy import queue in window 1085 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-10: Governance review of the legacy import queue in window 1088 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-03: Data-quality desk noted a rise in incomplete addresses from the portal sign-up path in window 1089. Raised with the source owner; the matching parameters were not touched.

- 2026-04-25: Data-quality desk noted a rise in incomplete addresses from the address-cleansing service in window 1090. Raised with the source owner; the matching parameters were not touched.

- 2026-04-04: Stewardship stand-up recorded a routine note against the CRM feed for window 1091. The manual review backlog was cleared with no amendment raised.

- 2026-04-19: Steward on duty logged a routine observation for the billing extract during review window 1092. Duplicate-rate drift reviewed; no policy change requested.

- 2026-04-13: Stewardship stand-up recorded a routine note against the legacy import queue for window 1093. The manual review backlog was cleared with no amendment raised.

- 2026-04-21: Governance review of the legacy import queue in window 1094 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-04: Governance review of the CRM feed in window 1097 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-02: Stewardship stand-up recorded a routine note against the portal sign-up path for window 1100. The manual review backlog was cleared with no amendment raised.

- 2026-04-09: Stewardship stand-up recorded a routine note against the legacy import queue for window 1101. The manual review backlog was cleared with no amendment raised.

- 2026-04-27: Governance review of the billing extract in window 1104 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-14: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1107. Raised with the source owner; the matching parameters were not touched.

- 2026-04-22: Governance review of the billing extract in window 1110 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-02: Governance review of the CRM feed in window 1111 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-20: Steward on duty logged a routine observation for the CRM feed during review window 1114. Duplicate-rate drift reviewed; no policy change requested.

- 2026-04-19: Governance review of the address-cleansing service in window 1115 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-08: Data-quality desk noted a rise in incomplete addresses from the CRM feed in window 1117. Raised with the source owner; the matching parameters were not touched.

- 2026-04-21: Stewardship stand-up recorded a routine note against the address-cleansing service for window 1120. The manual review backlog was cleared with no amendment raised.

- 2026-04-01: Governance review of the portal sign-up path in window 1123 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-14: Data-quality desk noted a rise in incomplete addresses from the portal sign-up path in window 1126. Raised with the source owner; the matching parameters were not touched.

- 2026-04-24: Steward on duty logged a routine observation for the portal sign-up path during review window 1127. Duplicate-rate drift reviewed; no policy change requested.

- 2026-04-01: Data-quality desk noted a rise in incomplete addresses from the CRM feed in window 1130. Raised with the source owner; the matching parameters were not touched.

- 2026-05-02: Governance review of the legacy import queue in window 1132 closed with no action; the standing thresholds were reconfirmed as they are.

> **Governance decision (2026-05-05 - #MDM-3150)** Priya: Input paths, final. The linkage policy and the do-not-merge register are always read from their fixed absolute paths under /app/data; `--input` selects the party records only. Both `--input` and `--output-dir` keep their documented defaults.

> **Governance decision (2026-05-08 - #MDM-3170)** Yusuf: Master recovery, final (supersedes #MDM-3020). Start from the pre-migration extract and replay the change journal in ascending `seq`, never in file order. A `correct` overwrites the named field in place. A `withdraw` takes the record out of the master, but the stewards keep it as it stood at that moment. A `reinstate` puts a withdrawn record back EXACTLY as it stood when it was withdrawn: corrections posted before the withdrawal survive, and any correction posted while it was out is ignored. A change naming a record the extract never carried is ignored, and a reinstatement of a record that was never withdrawn does nothing.

> **Governance decision (2026-05-09 - #MDM-3174)** Yusuf: Recovered shape, final. The rebuilt master is a JSON array ascending by `record_id`, and each record carries exactly the nine source fields -- the journal's bookkeeping (`seq`, `kind`, `posted_by`) never survives the replay.

> **Governance decision (2026-05-13 - #MDM-3182)** Lena: Normalisation, final. Before any comparison a value is folded to lower case, every character that is not a letter or a digit is dropped, and runs of whitespace collapse to a single space with the ends trimmed. The postal code is normalised the same way and then has its spaces removed entirely. Normalisation is for comparison only: the values written out are the survivor's own, unnormalised.

> **Governance decision (2026-05-15 - #MDM-3184)** Lena: Blocking, final (supersedes #MDM-3026). Candidate pairs are drawn only from within a block, never across the whole file. A record's block key is the first `block_prefix_len` characters of its normalised family name, then a vertical bar, then the first character of its normalised given name; a record whose normalised family name is empty joins no block and is compared with nothing.

> **Governance decision (2026-05-18 - #MDM-3186)** Marek: Pair scoring, final. A pair scores the sum of the weights of the fields that agree once normalised: family name 30, given name 22, date of birth 20, postal code 18, street 12, town 8. A field that is empty on either side contributes nothing rather than counting as a disagreement. A pair at or above `match_threshold` links; a pair at or above `review_floor` but below the threshold is queued as `below_threshold`.

> **Governance decision (2026-05-22 - #MDM-3190)** Yusuf: Do-not-merge register, final (revises #MDM-3044). A pair named on the register never links, however well it scores, and unlike the interim it IS queued -- as `do_not_merge`, carrying the score it reached. The register is consulted only where a pair would otherwise have linked, which is to say where it scores at or above the match threshold. A registered pair scoring below the threshold was never going to link, and it is treated exactly like any other sub-threshold pair: queued as `below_threshold` where it reaches the review floor, and not queued at all beneath it.

> **Governance decision (2026-05-25 - #MDM-3194)** Priya: Oversized clusters, final. Records link transitively, so a chain of pairwise links forms one cluster. A cluster holding more than `max_cluster_size` records is not trusted: it is dissolved, every one of its records is emitted as its own single-member cluster, and every one of them is queued as `cluster_too_large` with a score of zero.

> **Governance decision (2026-05-27 - #MDM-3196)** Marek: Survivorship, final (supersedes #MDM-3032; deviates from a freshest-wins reading). The survivor of a cluster is the record with the most non-empty fields among the six compared fields. A tie goes to the EARLIEST loaded record, on the reasoning that the oldest surviving view is the one the downstream ledgers were opened against, and a remaining tie to the lexicographically smallest record id. The golden record takes its values from the survivor alone; fields are never merged across the cluster.

> **Governance decision (2026-05-29 - #MDM-3198)** Lena: Emission order, final. A cluster is identified by the lexicographically smallest record id it holds, and the golden records ascend by that cluster id with their member ids ascending within. The review queue descends by score, then ascends by left and then right record id.

- 2026-05-01: Stewardship stand-up recorded a routine note against the portal sign-up path for window 1134. The manual review backlog was cleared with no amendment raised.

- 2026-05-26: Steward on duty logged a routine observation for the billing extract during review window 1136. Duplicate-rate drift reviewed; no policy change requested.

- 2026-05-09: Stewardship stand-up recorded a routine note against the CRM feed for window 1138. The manual review backlog was cleared with no amendment raised.

- 2026-05-09: Stewardship stand-up recorded a routine note against the CRM feed for window 1141. The manual review backlog was cleared with no amendment raised.

- 2026-05-11: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1143. Raised with the source owner; the matching parameters were not touched.

- 2026-05-10: Data-quality desk noted a rise in incomplete addresses from the address-cleansing service in window 1145. Raised with the source owner; the matching parameters were not touched.

- 2026-05-24: Stewardship stand-up recorded a routine note against the address-cleansing service for window 1146. The manual review backlog was cleared with no amendment raised.

- 2026-05-08: Data-quality desk noted a rise in incomplete addresses from the portal sign-up path in window 1148. Raised with the source owner; the matching parameters were not touched.

- 2026-05-08: Stewardship stand-up recorded a routine note against the address-cleansing service for window 1151. The manual review backlog was cleared with no amendment raised.

- 2026-05-08: Steward on duty logged a routine observation for the legacy import queue during review window 1154. Duplicate-rate drift reviewed; no policy change requested.

- 2026-05-21: Steward on duty logged a routine observation for the address-cleansing service during review window 1155. Duplicate-rate drift reviewed; no policy change requested.

- 2026-05-19: Stewardship stand-up recorded a routine note against the legacy import queue for window 1156. The manual review backlog was cleared with no amendment raised.

- 2026-05-02: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1157. Raised with the source owner; the matching parameters were not touched.

- 2026-05-05: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1159. Raised with the source owner; the matching parameters were not touched.

- 2026-05-12: Stewardship stand-up recorded a routine note against the legacy import queue for window 1162. The manual review backlog was cleared with no amendment raised.

- 2026-05-23: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1164. Raised with the source owner; the matching parameters were not touched.

- 2026-05-13: Steward on duty logged a routine observation for the legacy import queue during review window 1165. Duplicate-rate drift reviewed; no policy change requested.

- 2026-05-18: Stewardship stand-up recorded a routine note against the legacy import queue for window 1168. The manual review backlog was cleared with no amendment raised.

- 2026-05-10: Stewardship stand-up recorded a routine note against the address-cleansing service for window 1171. The manual review backlog was cleared with no amendment raised.

- 2026-06-22: Stewardship stand-up recorded a routine note against the CRM feed for window 1174. The manual review backlog was cleared with no amendment raised.

> **Governance decision (2026-06-03 - #MDM-3210)** Priya: Linkage policy baseline, read from /app/data/linkage_policy.json at that fixed absolute path. Any field the policy file omits keeps its baseline: match_threshold = 62; review_floor = 48; block_prefix_len = 4; max_cluster_size = 12.

- 2026-06-09: Stewardship stand-up recorded a routine note against the CRM feed for window 1175. The manual review backlog was cleared with no amendment raised.

- 2026-06-23: Steward on duty logged a routine observation for the CRM feed during review window 1178. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-17: Data-quality desk noted a rise in incomplete addresses from the portal sign-up path in window 1179. Raised with the source owner; the matching parameters were not touched.

- 2026-06-13: Steward on duty logged a routine observation for the legacy import queue during review window 1181. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-27: Steward on duty logged a routine observation for the CRM feed during review window 1184. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-05: Stewardship stand-up recorded a routine note against the billing extract for window 1187. The manual review backlog was cleared with no amendment raised.

- 2026-06-02: Stewardship stand-up recorded a routine note against the portal sign-up path for window 1190. The manual review backlog was cleared with no amendment raised.

- 2026-06-17: Steward on duty logged a routine observation for the CRM feed during review window 1192. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-20: Governance review of the portal sign-up path in window 1195 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-09: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1197. Raised with the source owner; the matching parameters were not touched.

- 2026-06-21: Governance review of the legacy import queue in window 1200 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-25: Stewardship stand-up recorded a routine note against the CRM feed for window 1202. The manual review backlog was cleared with no amendment raised.

- 2026-06-02: Stewardship stand-up recorded a routine note against the legacy import queue for window 1205. The manual review backlog was cleared with no amendment raised.

- 2026-06-03: Governance review of the legacy import queue in window 1207 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-03: Steward on duty logged a routine observation for the CRM feed during review window 1209. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-22: Governance review of the CRM feed in window 1210 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-27: Data-quality desk noted a rise in incomplete addresses from the legacy import queue in window 1213. Raised with the source owner; the matching parameters were not touched.

- 2026-06-27: Steward on duty logged a routine observation for the portal sign-up path during review window 1216. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-21: Steward on duty logged a routine observation for the portal sign-up path during review window 1218. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-09: Governance review of the billing extract in window 1219 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-16: Steward on duty logged a routine observation for the address-cleansing service during review window 1221. Duplicate-rate drift reviewed; no policy change requested.

- 2026-06-17: Data-quality desk noted a rise in incomplete addresses from the billing extract in window 1222. Raised with the source owner; the matching parameters were not touched.

- 2026-06-13: Governance review of the billing extract in window 1223 closed with no action; the standing thresholds were reconfirmed as they are.
