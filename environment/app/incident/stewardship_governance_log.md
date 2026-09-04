# Planning governance log

How the party-linkage engine is *meant* to behave -- the recovery of the truncated party master, normalisation, blocking, pair scoring, the do-not-merge register, cluster formation and survivorship -- was settled incrementally by the data stewardship board, and those decisions live in the review entries below, not in any single summary. Where two entries speak to the same stage, the later dated decision governs. `/app/docs/match_contract.json` is the output contract only.

- 2026-02-17: Stewardship stand-up cleared the week's queue with nothing carried forward. The manual review backlog was cleared with no amendment raised. Raised with the source owner; the matching parameters were not touched.

> **Board minute (2026-02-06 - #MDM-3020)** Rosa: rebuild the truncated master by concatenating the pre-migration extract with the change journal and keeping the last record seen for each id; a withdrawn record is simply absent and a reinstatement re-reads it from the extract.

> **Board minute (2026-02-13 - #MDM-3026)** Anders: candidate pairs are drawn across the whole file, since blocking risks missing a match whose key differs.

> **Board minute (2026-02-19 - #MDM-3032)** Marek: where several records survive a merge the LATEST loaded record is the survivor, being the freshest view of the party.

- 2026-02-23: The change board noted a low-risk change against the linkage service. The archive job skipped a directory that had already been swept. The desk confirmed no downstream impact.

- 2026-02-02: The training lead confirmed the annual refresher dates. An out-of-office reply bounced a notification back into the queue.

- 2026-02-16: The retention schedule for archived extracts was reread and confirmed. A scheduled restart moved by twenty minutes with no downstream effect. No change to any published figure.

- 2026-02-04: The source owner for the billing extract answered a question from last cycle. A report was regenerated after someone opened it mid-write. No follow-up was requested.

- 2026-02-09: A desk supervisor filed a staffing note for the coming month. Late input arrived from one source system and was loaded before the cut.

- 2026-02-20: An access request that had been sitting open was reviewed and granted. One field arrived null where the source normally sends an empty string. Resolved without escalation.

- 2026-02-07: An intake form was reworded after two people misread the same field. A typo in a reference record was corrected before the load started. Signed off at the weekly slot.

- 2026-02-19: An on-call steward recorded an overnight alert that cleared itself. Disk usage on the log volume fell after the retention change took effect.

- 2026-02-19: A capacity note was filed against the staging environment. A single record arrived twice after a mid-cycle correction upstream. Left open pending the next walkthrough.

- 2026-02-12: A steward wrote up a question that came in from the contact centre. The published calendar was reissued with the bank-holiday dates corrected. Closed once the supplier confirmed.

- 2026-02-26: A steward on duty logged a short note about the portal sign-up path. Duplicate-rate drift sat inside its usual band and nothing was adjusted.

- 2026-02-07: The vendor-management lead summarised a call with the address-validation supplier. A stale credential was rotated on schedule rather than in response to anything. Referred to the dated decisions and closed.

- 2026-02-03: The documentation owner tidied a stale link in the steward runbook. A duplicate pair flagged last month was confirmed as two genuine parties. The owner acknowledged and closed it.

- 2026-02-23: The dashboard owner rebuilt a tile that had stopped refreshing. One party's contact details were refreshed at their own request.

- 2026-02-23: The legacy import queue was drained on schedule and the run written up. The weekly file was a few kilobytes larger than usual, entirely in padding. Closed with no policy change.

- 2026-02-02: The service-desk queue was reviewed at the usual weekly slot. The record count sat a little above the running mean, entirely from a backfill. No action was carried forward.

- 2026-02-12: The monthly extract was signed off by the receiving team. The clock on a test host had drifted and was resynchronised.

- 2026-02-11: The data-quality desk closed a ticket raised against the CRM feed. The nightly reconciliation matched exactly and the file was released. Raised with the source owner; the matching parameters were not touched.

- 2026-02-02: A quarterly walkthrough revisited a control the auditors had asked about. An extract ran twice because an operator retried a step that had succeeded. The desk confirmed no downstream impact.

- 2026-02-25: A supplier advisory was circulated for information. Storage on the staging host was extended after the extract outgrew its allocation.

- 2026-02-04: A note was added to the handover after a quiet weekend. A supplier's status page showed a brief degradation that did not reach us. No change to any published figure.

- 2026-02-24: A reviewer asked after a figure on the duplicate-rate dashboard. Incomplete addresses from one feed rose slightly and fell back the next day. No follow-up was requested.

- 2026-02-08: The reference-data team logged a correction request from a business unit. Two tickets covering the same request were merged.

- 2026-03-02: A colleague asked whether an old ticket could finally be closed. The manual review backlog was cleared with no amendment raised. Resolved without escalation.

> **Board minute (2026-03-05 - #MDM-3044)** Priya: a pair on the do-not-merge register is skipped silently and not reported.

- 2026-03-08: Stewardship stand-up cleared the week's queue with nothing carried forward. The archive job skipped a directory that had already been swept. Signed off at the weekly slot.

- 2026-03-04: The change board noted a low-risk change against the linkage service. An out-of-office reply bounced a notification back into the queue.

- 2026-03-08: The training lead confirmed the annual refresher dates. A scheduled restart moved by twenty minutes with no downstream effect. Left open pending the next walkthrough.

- 2026-03-22: The retention schedule for archived extracts was reread and confirmed. A report was regenerated after someone opened it mid-write. Closed once the supplier confirmed.

- 2026-03-20: The source owner for the billing extract answered a question from last cycle. Late input arrived from one source system and was loaded before the cut.

- 2026-03-23: A desk supervisor filed a staffing note for the coming month. One field arrived null where the source normally sends an empty string. Referred to the dated decisions and closed.

- 2026-03-12: An access request that had been sitting open was reviewed and granted. A typo in a reference record was corrected before the load started. The owner acknowledged and closed it.

- 2026-03-25: An intake form was reworded after two people misread the same field. Disk usage on the log volume fell after the retention change took effect.

- 2026-03-10: An on-call steward recorded an overnight alert that cleared itself. A single record arrived twice after a mid-cycle correction upstream. Closed with no policy change.

- 2026-03-18: A capacity note was filed against the staging environment. The published calendar was reissued with the bank-holiday dates corrected. No action was carried forward.

- 2026-03-06: A steward wrote up a question that came in from the contact centre. Duplicate-rate drift sat inside its usual band and nothing was adjusted.

- 2026-03-04: A steward on duty logged a short note about the portal sign-up path. A stale credential was rotated on schedule rather than in response to anything. Raised with the source owner; the matching parameters were not touched.

- 2026-03-19: The vendor-management lead summarised a call with the address-validation supplier. A duplicate pair flagged last month was confirmed as two genuine parties. The desk confirmed no downstream impact.

- 2026-03-25: The documentation owner tidied a stale link in the steward runbook. One party's contact details were refreshed at their own request.

- 2026-03-03: The dashboard owner rebuilt a tile that had stopped refreshing. The weekly file was a few kilobytes larger than usual, entirely in padding. No change to any published figure.

- 2026-03-27: The legacy import queue was drained on schedule and the run written up. The record count sat a little above the running mean, entirely from a backfill. No follow-up was requested.

- 2026-03-04: The service-desk queue was reviewed at the usual weekly slot. The clock on a test host had drifted and was resynchronised.

- 2026-04-11: The monthly extract was signed off by the receiving team. The nightly reconciliation matched exactly and the file was released. Resolved without escalation.

- 2026-04-01: The data-quality desk closed a ticket raised against the CRM feed. An extract ran twice because an operator retried a step that had succeeded. Signed off at the weekly slot.

- 2026-04-10: A quarterly walkthrough revisited a control the auditors had asked about. Storage on the staging host was extended after the extract outgrew its allocation.

- 2026-04-03: A supplier advisory was circulated for information. A supplier's status page showed a brief degradation that did not reach us. Left open pending the next walkthrough.

- 2026-04-25: A note was added to the handover after a quiet weekend. Incomplete addresses from one feed rose slightly and fell back the next day. Closed once the supplier confirmed.

- 2026-04-04: A reviewer asked after a figure on the duplicate-rate dashboard. Two tickets covering the same request were merged.

- 2026-04-19: The reference-data team logged a correction request from a business unit. The manual review backlog was cleared with no amendment raised. Referred to the dated decisions and closed.

- 2026-04-13: A colleague asked whether an old ticket could finally be closed. The archive job skipped a directory that had already been swept. The owner acknowledged and closed it.

- 2026-04-21: Stewardship stand-up cleared the week's queue with nothing carried forward. An out-of-office reply bounced a notification back into the queue.

- 2026-04-04: The change board noted a low-risk change against the linkage service. A scheduled restart moved by twenty minutes with no downstream effect. Closed with no policy change.

- 2026-04-02: The training lead confirmed the annual refresher dates. A report was regenerated after someone opened it mid-write. No action was carried forward.

- 2026-04-09: The retention schedule for archived extracts was reread and confirmed. Late input arrived from one source system and was loaded before the cut.

- 2026-04-27: The source owner for the billing extract answered a question from last cycle. One field arrived null where the source normally sends an empty string. Raised with the source owner; the matching parameters were not touched.

- 2026-04-14: A desk supervisor filed a staffing note for the coming month. A typo in a reference record was corrected before the load started. The desk confirmed no downstream impact.

- 2026-04-22: An access request that had been sitting open was reviewed and granted. Disk usage on the log volume fell after the retention change took effect.

- 2026-04-02: An intake form was reworded after two people misread the same field. A single record arrived twice after a mid-cycle correction upstream. No change to any published figure.

- 2026-04-20: An on-call steward recorded an overnight alert that cleared itself. The published calendar was reissued with the bank-holiday dates corrected. No follow-up was requested.

- 2026-04-19: A capacity note was filed against the staging environment. Duplicate-rate drift sat inside its usual band and nothing was adjusted.

- 2026-04-08: A steward wrote up a question that came in from the contact centre. A stale credential was rotated on schedule rather than in response to anything. Resolved without escalation.

- 2026-04-21: A steward on duty logged a short note about the portal sign-up path. A duplicate pair flagged last month was confirmed as two genuine parties. Signed off at the weekly slot.

- 2026-04-01: The vendor-management lead summarised a call with the address-validation supplier. One party's contact details were refreshed at their own request.

- 2026-04-14: The documentation owner tidied a stale link in the steward runbook. The weekly file was a few kilobytes larger than usual, entirely in padding. Left open pending the next walkthrough.

- 2026-04-24: The dashboard owner rebuilt a tile that had stopped refreshing. The record count sat a little above the running mean, entirely from a backfill. Closed once the supplier confirmed.

- 2026-04-01: The legacy import queue was drained on schedule and the run written up. The clock on a test host had drifted and was resynchronised.

- 2026-05-02: The service-desk queue was reviewed at the usual weekly slot. The nightly reconciliation matched exactly and the file was released. Referred to the dated decisions and closed.

> **Board minute (2026-05-05 - #MDM-3150)** Priya: Input paths, final. The linkage policy and the do-not-merge register are always read from their fixed absolute paths under /app/data; `--input` selects the party records only. Both `--input` and `--output-dir` keep their documented defaults.

> **Board minute (2026-05-08 - #MDM-3170)** Yusuf: Master recovery, final. Start from the pre-migration extract and replay the change journal in ascending `seq`, never in file order. A `correct` overwrites the named field in place. A `withdraw` takes the record out of the master, but the stewards keep it as it stood at that moment. A `reinstate` puts a withdrawn record back EXACTLY as it stood when it was withdrawn: corrections posted before the withdrawal survive, and any correction posted while it was out is ignored. A change naming a record the extract never carried is ignored, and a reinstatement of a record that was never withdrawn does nothing.

> **Board minute (2026-05-09 - #MDM-3174)** Yusuf: Recovered shape, final. The rebuilt master is a JSON array ascending by `record_id`, and each record carries exactly the nine source fields -- the journal's bookkeeping (`seq`, `kind`, `posted_by`) never survives the replay.

> **Board minute (2026-05-13 - #MDM-3182)** Lena: Normalisation, final. Before any comparison a value is folded to lower case, every character that is not a letter or a digit is dropped, and runs of whitespace collapse to a single space with the ends trimmed. The postal code is normalised the same way and then has its spaces removed entirely. Normalisation is for comparison only: the values written out are the survivor's own, unnormalised.

> **Board minute (2026-05-15 - #MDM-3184)** Lena: Blocking, final. Candidate pairs are drawn only from within a block, never across the whole file. A record's block key is the first `block_prefix_len` characters of its normalised family name, then a vertical bar, then the first character of its normalised given name; a record whose normalised family name is empty joins no block and is compared with nothing. Where the normalised GIVEN name is empty the key still carries the bar with nothing after it, so such records block together and are compared with each other rather than being set aside: only an empty family name takes a record out of blocking.

> **Board minute (2026-05-18 - #MDM-3186)** Marek: Pair scoring, final. A pair scores the sum of the weights of the fields that agree once normalised: family name 30, given name 22, date of birth 20, postal code 18, street 12, town 8. A field that is empty on either side contributes nothing rather than counting as a disagreement. A pair at or above `match_threshold` links; a pair at or above `review_floor` but below the threshold is queued as `below_threshold`.

> **Board minute (2026-05-22 - #MDM-3190)** Yusuf: Do-not-merge register, final. A pair named on the register never links, however well it scores, and unlike the interim it IS queued -- as `do_not_merge`, carrying the score it reached. The register is consulted only where a pair would otherwise have linked, which is to say where it scores at or above the match threshold. A registered pair scoring below the threshold was never going to link, and it is treated exactly like any other sub-threshold pair: queued as `below_threshold` where it reaches the review floor, and not queued at all beneath it.

> **Board minute (2026-05-25 - #MDM-3194)** Priya: Oversized clusters, final. Records link transitively, so a chain of pairwise links forms one cluster. A cluster holding more than `max_cluster_size` records is not trusted: it is dissolved, every one of its records is emitted as its own single-member cluster, and every one of them is queued as `cluster_too_large` with a score of zero. Such a row concerns one record rather than a pair, so it carries that record's own id on BOTH sides: `left` and `right` are the same id, which is also what the queue sorts on.

> **Board minute (2026-05-27 - #MDM-3196)** Marek: Survivorship, final. The survivor of a cluster is the record with the most non-empty fields among the six compared fields. A tie goes to the EARLIEST loaded record, on the reasoning that the oldest surviving view is the one the downstream ledgers were opened against, and a remaining tie to the lexicographically smallest record id. The golden record takes its values from the survivor alone; fields are never merged across the cluster.

> **Board minute (2026-05-29 - #MDM-3198)** Lena: Emission order, final. A cluster is identified by the lexicographically smallest record id it holds, and the golden records ascend by that cluster id with their member ids ascending within. The review queue descends by score, then ascends by left and then right record id.

- 2026-05-01: The monthly extract was signed off by the receiving team. An extract ran twice because an operator retried a step that had succeeded. The owner acknowledged and closed it.

- 2026-05-26: The data-quality desk closed a ticket raised against the CRM feed. Storage on the staging host was extended after the extract outgrew its allocation.

- 2026-05-09: A quarterly walkthrough revisited a control the auditors had asked about. A supplier's status page showed a brief degradation that did not reach us. Closed with no policy change.

- 2026-05-09: A supplier advisory was circulated for information. Incomplete addresses from one feed rose slightly and fell back the next day. No action was carried forward.

- 2026-05-11: A note was added to the handover after a quiet weekend. Two tickets covering the same request were merged.

- 2026-05-10: A reviewer asked after a figure on the duplicate-rate dashboard. The manual review backlog was cleared with no amendment raised. Raised with the source owner; the matching parameters were not touched.

- 2026-05-24: The reference-data team logged a correction request from a business unit. The archive job skipped a directory that had already been swept. The desk confirmed no downstream impact.

- 2026-05-08: A colleague asked whether an old ticket could finally be closed. An out-of-office reply bounced a notification back into the queue.

- 2026-05-08: Stewardship stand-up cleared the week's queue with nothing carried forward. A scheduled restart moved by twenty minutes with no downstream effect. No change to any published figure.

- 2026-05-08: The change board noted a low-risk change against the linkage service. A report was regenerated after someone opened it mid-write. No follow-up was requested.

- 2026-05-21: The training lead confirmed the annual refresher dates. Late input arrived from one source system and was loaded before the cut.

- 2026-05-19: The retention schedule for archived extracts was reread and confirmed. One field arrived null where the source normally sends an empty string. Resolved without escalation.

- 2026-05-02: The source owner for the billing extract answered a question from last cycle. A typo in a reference record was corrected before the load started. Signed off at the weekly slot.

- 2026-05-05: A desk supervisor filed a staffing note for the coming month. Disk usage on the log volume fell after the retention change took effect.

- 2026-05-12: An access request that had been sitting open was reviewed and granted. A single record arrived twice after a mid-cycle correction upstream. Left open pending the next walkthrough.

- 2026-05-23: An intake form was reworded after two people misread the same field. The published calendar was reissued with the bank-holiday dates corrected. Closed once the supplier confirmed.

- 2026-05-13: An on-call steward recorded an overnight alert that cleared itself. Duplicate-rate drift sat inside its usual band and nothing was adjusted.

- 2026-05-18: A capacity note was filed against the staging environment. A stale credential was rotated on schedule rather than in response to anything. Referred to the dated decisions and closed.

- 2026-05-10: A steward wrote up a question that came in from the contact centre. A duplicate pair flagged last month was confirmed as two genuine parties. The owner acknowledged and closed it.

- 2026-06-22: A steward on duty logged a short note about the portal sign-up path. One party's contact details were refreshed at their own request.

> **Board minute (2026-06-03 - #MDM-3220)** Rosa: golden record assembly, final. This settles what #MDM-3196 left open by naming only the survivor. The survivor still identifies the cluster and supplies `survivor_id`, but the golden record is ASSEMBLED rather than copied: each of `given_name`, `family_name`, `street`, `city`, `postal_code` and `born_on` is taken independently from the cluster member with the highest completeness that carries a non-empty value for THAT field, ties going to the earliest loaded record and then to the lexicographically smallest record id. A field no member fills stays empty. `completeness` reports the completeness of the ASSEMBLED record, not of the survivor, so a golden record can be more complete than any single member of its cluster. Reading the survivor's row straight through leaves gaps a sibling could have filled and is wrong; a singleton cluster is unaffected because it assembles from itself.

> **Board minute (2026-06-09 - #MDM-3230)** Rosa: chained clusters, final (amends #MDM-3194 on what a cluster is; the cap that decision sets is untouched and now falls on what this one leaves behind). Records still link transitively, but a cluster the stewards can only reach by walking a chain is not one the board will publish: a cluster of THREE or more records must be COHESIVE, meaning every pair of its members -- not merely the pairs that linked, and not merely the pairs a block ever proposed -- scores at or above `match_threshold` under #MDM-3186, and no pair of its members is named on the do-not-merge register, which is never cohesive whatever it scores. A cluster of three or more that is not cohesive has its WEAKEST accepted link cut -- the accepted link between its members carrying the lowest #MDM-3186 score, and where two tie on score the pair that sorts first ascending by left then right -- and is formed again from the accepted links that remain among those same records; whatever that leaves, cohesive or not, is judged the same way in turn. A link cut this way is gone: it is never re-formed, it is queued for review as `chain_broken` carrying its own score, and the run's summary counts the cuts in `chain_broken_link_count`. It stays counted in `link_count`, which #MDM-3198 keeps as a count of the pairs that qualified and linked, not of the links a cluster ends up standing on. A cluster of one or two records is cohesive by definition and is never cut. The #MDM-3194 cap is read against the clusters this leaves, not against the chained ones the links first produced.

> **Board minute (2026-06-03 - #MDM-3210)** Priya: Linkage policy baseline, read from /app/data/linkage_policy.json at that fixed absolute path. Any field the policy file omits keeps its baseline: match_threshold = 62; review_floor = 48; block_prefix_len = 4; max_cluster_size = 12.

- 2026-06-09: The vendor-management lead summarised a call with the address-validation supplier. The weekly file was a few kilobytes larger than usual, entirely in padding. Closed with no policy change.

- 2026-06-23: The documentation owner tidied a stale link in the steward runbook. The record count sat a little above the running mean, entirely from a backfill. No action was carried forward.

- 2026-06-17: The dashboard owner rebuilt a tile that had stopped refreshing. The clock on a test host had drifted and was resynchronised.

- 2026-06-13: The legacy import queue was drained on schedule and the run written up. The nightly reconciliation matched exactly and the file was released. Raised with the source owner; the matching parameters were not touched.

- 2026-06-27: The service-desk queue was reviewed at the usual weekly slot. An extract ran twice because an operator retried a step that had succeeded. The desk confirmed no downstream impact.

- 2026-06-05: The monthly extract was signed off by the receiving team. Storage on the staging host was extended after the extract outgrew its allocation.

- 2026-06-02: The data-quality desk closed a ticket raised against the CRM feed. A supplier's status page showed a brief degradation that did not reach us. No change to any published figure.

- 2026-06-17: A quarterly walkthrough revisited a control the auditors had asked about. Incomplete addresses from one feed rose slightly and fell back the next day. No follow-up was requested.

- 2026-06-20: A supplier advisory was circulated for information. Two tickets covering the same request were merged.

- 2026-06-09: A note was added to the handover after a quiet weekend. The manual review backlog was cleared with no amendment raised. Resolved without escalation.

- 2026-06-21: A reviewer asked after a figure on the duplicate-rate dashboard. The archive job skipped a directory that had already been swept. Signed off at the weekly slot.

- 2026-06-25: The reference-data team logged a correction request from a business unit. An out-of-office reply bounced a notification back into the queue.

- 2026-06-02: A colleague asked whether an old ticket could finally be closed. A scheduled restart moved by twenty minutes with no downstream effect. Left open pending the next walkthrough.

- 2026-06-03: Stewardship stand-up cleared the week's queue with nothing carried forward. A report was regenerated after someone opened it mid-write. Closed once the supplier confirmed.

- 2026-06-03: The change board noted a low-risk change against the linkage service. Late input arrived from one source system and was loaded before the cut.

- 2026-06-22: The training lead confirmed the annual refresher dates. One field arrived null where the source normally sends an empty string. Referred to the dated decisions and closed.

- 2026-06-27: The retention schedule for archived extracts was reread and confirmed. A typo in a reference record was corrected before the load started. The owner acknowledged and closed it.

- 2026-06-27: The source owner for the billing extract answered a question from last cycle. Disk usage on the log volume fell after the retention change took effect.

- 2026-06-21: A desk supervisor filed a staffing note for the coming month. A single record arrived twice after a mid-cycle correction upstream. Closed with no policy change.

- 2026-06-09: An access request that had been sitting open was reviewed and granted. The published calendar was reissued with the bank-holiday dates corrected. No action was carried forward.

- 2026-06-16: An intake form was reworded after two people misread the same field. Duplicate-rate drift sat inside its usual band and nothing was adjusted.

- 2026-06-17: An on-call steward recorded an overnight alert that cleared itself. A stale credential was rotated on schedule rather than in response to anything. Raised with the source owner; the matching parameters were not touched.

- 2026-06-13: A capacity note was filed against the staging environment. A duplicate pair flagged last month was confirmed as two genuine parties. The desk confirmed no downstream impact.
