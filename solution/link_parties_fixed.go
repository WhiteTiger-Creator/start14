// Stage two of the reference: the corrected party-linkage engine.
//
// Every governing value is traced to its final dated entry in
// /app/incident/stewardship_governance_log.md; match_contract.json supplies the
// output contract only and no derivation rule.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
	"strings"
	"unicode"
)

type record struct {
	RecordID     string `json:"record_id"`
	SourceSystem string `json:"source_system"`
	GivenName    string `json:"given_name"`
	FamilyName   string `json:"family_name"`
	Street       string `json:"street"`
	City         string `json:"city"`
	PostalCode   string `json:"postal_code"`
	BornOn       string `json:"born_on"`
	LoadedOnDay  int    `json:"loaded_on_day"`
}

type policy struct {
	Default map[string]int `json:"default"`
}

type blockedPair struct {
	Left  string `json:"left"`
	Right string `json:"right"`
}

type goldenRecord struct {
	ClusterID   string   `json:"cluster_id"`
	SurvivorID  string   `json:"survivor_id"`
	MemberIDs   []string `json:"member_ids"`
	GivenName   string   `json:"given_name"`
	FamilyName  string   `json:"family_name"`
	Street      string   `json:"street"`
	City        string   `json:"city"`
	PostalCode  string   `json:"postal_code"`
	BornOn      string   `json:"born_on"`
	MemberCount int      `json:"member_count"`
	Completeness int     `json:"completeness"`
}

type reviewRow struct {
	Left   string `json:"left"`
	Right  string `json:"right"`
	Score  int    `json:"score"`
	Reason string `json:"reason"`
}

func readJSON(path string, into interface{}) {
	raw, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := json.Unmarshal(raw, into); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func writeJSON(path string, value interface{}) {
	encoded, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := os.WriteFile(path, append(encoded, '\n'), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

// #MDM-3182: normalisation folds case, collapses internal whitespace and drops
// every character that is not a letter, a digit or a single separating space.
// The postal code additionally drops spaces entirely.
func normalise(s string) string {
	var b strings.Builder
	lastSpace := true
	for _, r := range strings.ToLower(s) {
		switch {
		// #MDM-3182 drops every character that is not a letter or a digit, and a
		// letter is a letter whatever alphabet it comes from. Testing a-z and 0-9
		// dropped e-acute and every other non-ASCII letter instead of keeping it,
		// which silently shortened the value the block key and the field scores
		// are taken from.
		case unicode.IsLetter(r), unicode.IsDigit(r):
			b.WriteRune(r)
			lastSpace = false
		case unicode.IsSpace(r):
			// #MDM-3182 collapses runs of WHITESPACE, not runs of space and tab.
			// Treating a newline as an ordinary droppable character joined the
			// words either side of it and changed the field's agreement score.
			if !lastSpace {
				b.WriteRune(' ')
				lastSpace = true
			}
		}
	}
	return strings.TrimSpace(b.String())
}

func normalisePostal(s string) string {
	return strings.ReplaceAll(normalise(s), " ", "")
}

// #MDM-3186: the field weights the board settled on. A field missing on either
// side scores nothing rather than counting as disagreement.
func score(a, b record) int {
	total := 0
	add := func(x, y string, weight int) {
		if x == "" || y == "" {
			return
		}
		if x == y {
			total += weight
		}
	}
	add(normalise(a.FamilyName), normalise(b.FamilyName), 30)
	add(normalise(a.GivenName), normalise(b.GivenName), 22)
	add(normalise(a.BornOn), normalise(b.BornOn), 20)
	add(normalisePostal(a.PostalCode), normalisePostal(b.PostalCode), 18)
	add(normalise(a.Street), normalise(b.Street), 12)
	add(normalise(a.City), normalise(b.City), 8)
	return total
}

func completeness(r record) int {
	n := 0
	for _, v := range []string{r.GivenName, r.FamilyName, r.Street, r.City, r.PostalCode, r.BornOn} {
		if normalise(v) != "" {
			n++
		}
	}
	return n
}

// #MDM-3210: the policy is read from its fixed absolute path, and any field the
// file omits keeps its governed baseline. A missing key is NOT zero.
func policyValue(pol policy, field string, baseline int) int {
	if value, ok := pol.Default[field]; ok {
		return value
	}
	return baseline
}

// acceptedLink is a pair that scored at or above the threshold and was not held
// apart by the register, kept because #MDM-3230 may have to form a cluster again
// from the links that survive a cut.
type acceptedLink struct {
	a, b  int
	score int
}

// cohesive reports whether every pair of these records may sit in one cluster:
// #MDM-3230 asks each pair for its own score, not merely the pairs that linked,
// and a pair the register names is never cohesive whatever it scores.
func cohesive(members []int, records []record, forbidden map[[2]string]bool, threshold int) bool {
	if len(members) < 3 {
		return true
	}
	for x := 0; x < len(members); x++ {
		for y := x + 1; y < len(members); y++ {
			a, b := records[members[x]], records[members[y]]
			l, r := a.RecordID, b.RecordID
			if l > r {
				l, r = r, l
			}
			if forbidden[[2]string{l, r}] {
				return false
			}
			if score(a, b) < threshold {
				return false
			}
		}
	}
	return true
}

// settle turns one chained group into the cohesive clusters #MDM-3230 publishes.
// A group of three or more that is not cohesive loses its weakest accepted link
// -- lowest score, ties going to the pair that sorts first -- and is formed
// again from the links that remain; each part is then judged the same way.
func settle(members []int, links []acceptedLink, records []record,
	forbidden map[[2]string]bool, threshold int) ([][]int, []acceptedLink) {
	if cohesive(members, records, forbidden, threshold) {
		return [][]int{members}, nil
	}
	pairKey := func(link acceptedLink) [2]string {
		l, r := records[link.a].RecordID, records[link.b].RecordID
		if l > r {
			l, r = r, l
		}
		return [2]string{l, r}
	}
	weakest := 0
	for i := 1; i < len(links); i++ {
		if links[i].score != links[weakest].score {
			if links[i].score < links[weakest].score {
				weakest = i
			}
			continue
		}
		here, best := pairKey(links[i]), pairKey(links[weakest])
		if here[0] < best[0] || (here[0] == best[0] && here[1] < best[1]) {
			weakest = i
		}
	}
	cut := links[weakest]
	remaining := make([]acceptedLink, 0, len(links)-1)
	remaining = append(remaining, links[:weakest]...)
	remaining = append(remaining, links[weakest+1:]...)

	// form the group again from what is left of its links
	root := map[int]int{}
	for _, m := range members {
		root[m] = m
	}
	var find func(int) int
	find = func(x int) int {
		for root[x] != x {
			root[x] = root[root[x]]
			x = root[x]
		}
		return x
	}
	for _, link := range remaining {
		ra, rb := find(link.a), find(link.b)
		if ra != rb {
			if ra < rb {
				root[rb] = ra
			} else {
				root[ra] = rb
			}
		}
	}
	parts := map[int][]int{}
	for _, m := range members {
		parts[find(m)] = append(parts[find(m)], m)
	}
	order := make([]int, 0, len(parts))
	for key := range parts {
		order = append(order, key)
	}
	sort.Slice(order, func(i, j int) bool {
		return records[parts[order[i]][0]].RecordID < records[parts[order[j]][0]].RecordID
	})

	clusters := make([][]int, 0, len(parts))
	cuts := []acceptedLink{cut}
	for _, key := range order {
		part := parts[key]
		sort.Slice(part, func(i, j int) bool {
			return records[part[i]].RecordID < records[part[j]].RecordID
		})
		inside := make([]acceptedLink, 0, len(remaining))
		for _, link := range remaining {
			if find(link.a) == key {
				inside = append(inside, link)
			}
		}
		deeper, deeperCuts := settle(part, inside, records, forbidden, threshold)
		clusters = append(clusters, deeper...)
		cuts = append(cuts, deeperCuts...)
	}
	return clusters, cuts
}

func main() {
	input := flag.String("input", "/app/data/party_records.json", "party records")
	outputDir := flag.String("output-dir", "/app/output", "output directory")
	flag.Parse()

	var records []record
	var pol policy
	var blocked []blockedPair
	// #MDM-3150: the policy and the do-not-merge register are always read from
	// their fixed absolute paths; --input selects the party records only.
	readJSON("/app/data/linkage_policy.json", &pol)
	readJSON("/app/data/do_not_merge.json", &blocked)
	readJSON(*input, &records)

	threshold := policyValue(pol, "match_threshold", 62)
	reviewFloor := policyValue(pol, "review_floor", 48)
	prefixLen := policyValue(pol, "block_prefix_len", 4)
	maxCluster := policyValue(pol, "max_cluster_size", 12)

	sort.Slice(records, func(i, j int) bool { return records[i].RecordID < records[j].RecordID })
	index := make(map[string]int, len(records))
	for i, r := range records {
		index[r.RecordID] = i
	}

	forbidden := make(map[[2]string]bool, len(blocked))
	for _, p := range blocked {
		l, r := p.Left, p.Right
		if l > r {
			l, r = r, l
		}
		forbidden[[2]string{l, r}] = true
	}

	// #MDM-3184: candidates are drawn from a block, never from the whole file.
	// The block key is the first block_prefix_len characters of the normalised
	// family name followed by the first character of the normalised given name.
	blocks := map[string][]int{}
	for i, r := range records {
		fam := normalise(r.FamilyName)
		giv := normalise(r.GivenName)
		if fam == "" {
			continue
		}
		// characters, not bytes: slicing a UTF-8 string by byte offset cuts a
		// multi-byte letter in half, so two names sharing only a leading byte
		// would block together and one letter would be split into a fragment
		famRunes := []rune(fam)
		if len(famRunes) > prefixLen {
			famRunes = famRunes[:prefixLen]
		}
		key := string(famRunes)
		if giv != "" {
			key += "|" + string([]rune(giv)[0])
		} else {
			key += "|"
		}
		blocks[key] = append(blocks[key], i)
	}

	parent := make([]int, len(records))
	for i := range parent {
		parent[i] = i
	}
	var find func(int) int
	find = func(x int) int {
		for parent[x] != x {
			parent[x] = parent[parent[x]]
			x = parent[x]
		}
		return x
	}
	union := func(a, b int) {
		ra, rb := find(a), find(b)
		if ra != rb {
			if ra < rb {
				parent[rb] = ra
			} else {
				parent[ra] = rb
			}
		}
	}

	reviews := make([]reviewRow, 0)
	accepted := make([]acceptedLink, 0)
	linkCount := 0
	blockedHits := 0
	keys := make([]string, 0, len(blocks))
	for k := range blocks {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		members := blocks[k]
		for x := 0; x < len(members); x++ {
			for y := x + 1; y < len(members); y++ {
				a, b := records[members[x]], records[members[y]]
				l, r := a.RecordID, b.RecordID
				if l > r {
					l, r = r, l
				}
				s := score(a, b)
				if s >= threshold {
					if forbidden[[2]string{l, r}] {
						// #MDM-3190: a pair the stewards have ruled apart never links,
						// however well it scores, and is queued for review instead.
						blockedHits++
						reviews = append(reviews, reviewRow{l, r, s, "do_not_merge"})
						continue
					}
					union(members[x], members[y])
					accepted = append(accepted, acceptedLink{members[x], members[y], s})
					linkCount++
				} else if s >= reviewFloor {
					reviews = append(reviews, reviewRow{l, r, s, "below_threshold"})
				}
			}
		}
	}

	chained := map[int][]int{}
	for i := range records {
		root := find(i)
		chained[root] = append(chained[root], i)
	}

	// #MDM-3230: a cluster reached only by walking a chain is not published. Each
	// chained group is settled into cohesive parts before anything downstream
	// reads it, and every link cut on the way is queued and counted.
	chainRoots := make([]int, 0, len(chained))
	for root := range chained {
		chainRoots = append(chainRoots, root)
	}
	sort.Slice(chainRoots, func(i, j int) bool {
		return records[chained[chainRoots[i]][0]].RecordID < records[chained[chainRoots[j]][0]].RecordID
	})
	byMember := map[int][]acceptedLink{}
	for _, link := range accepted {
		root := find(link.a)
		byMember[root] = append(byMember[root], link)
	}
	settled := make([][]int, 0, len(chained))
	chainCuts := 0
	for _, root := range chainRoots {
		members := append([]int{}, chained[root]...)
		sort.Slice(members, func(i, j int) bool {
			return records[members[i]].RecordID < records[members[j]].RecordID
		})
		parts, cuts := settle(members, byMember[root], records, forbidden, threshold)
		settled = append(settled, parts...)
		for _, cut := range cuts {
			l, r := records[cut.a].RecordID, records[cut.b].RecordID
			if l > r {
				l, r = r, l
			}
			reviews = append(reviews, reviewRow{l, r, cut.score, "chain_broken"})
		}
		chainCuts += len(cuts)
	}
	sort.Slice(settled, func(i, j int) bool {
		return records[settled[i][0]].RecordID < records[settled[j][0]].RecordID
	})

	golden := make([]goldenRecord, 0, len(settled))
	oversized := 0
	capLimit := maxCluster
	if capLimit < 0 {
		capLimit = 0
	}

	for _, members := range settled {
		// #MDM-3194: a cluster holding MORE THAN max_cluster_size records is not
		// trusted; its members are emitted as singletons and every one is queued.
		// The comparison is direct, so it holds at every value the cap can take --
		// guarding on maxCluster > 0 made a cap of zero mean no cap at all.
		if len(members) > capLimit {
			oversized++
			for _, m := range members {
				reviews = append(reviews, reviewRow{
					records[m].RecordID, records[m].RecordID, 0, "cluster_too_large"})
			}
			for _, m := range members {
				r := records[m]
				golden = append(golden, goldenRecord{
					ClusterID: r.RecordID, SurvivorID: r.RecordID,
					MemberIDs: []string{r.RecordID}, GivenName: r.GivenName,
					FamilyName: r.FamilyName, Street: r.Street, City: r.City,
					PostalCode: r.PostalCode, BornOn: r.BornOn,
					MemberCount: 1, Completeness: completeness(r),
				})
			}
			continue
		}
		// #MDM-3196: the survivor is the most complete record; ties go to the
		// EARLIEST load, and then to the lexicographically smallest record id.
		best := members[0]
		for _, m := range members[1:] {
			cm, cb := completeness(records[m]), completeness(records[best])
			switch {
			case cm > cb:
				best = m
			case cm == cb && records[m].LoadedOnDay < records[best].LoadedOnDay:
				best = m
			case cm == cb && records[m].LoadedOnDay == records[best].LoadedOnDay &&
				records[m].RecordID < records[best].RecordID:
				best = m
			}
		}
		ids := make([]string, 0, len(members))
		for _, m := range members {
			ids = append(ids, records[m].RecordID)
		}
		// #MDM-3220: the golden record is ASSEMBLED, not copied off the survivor.
		// Each field is taken from the most complete member carrying a non-empty
		// value for that field, ties to the earliest load then the smallest id, so
		// a gap in the survivor's row is filled by a sibling that has it.
		s := records[best]
		pick := func(get func(record) string) string {
			chosen := -1
			for _, m := range members {
				if normalise(get(records[m])) == "" {
					continue
				}
				if chosen < 0 {
					chosen = m
					continue
				}
				cm, cc := completeness(records[m]), completeness(records[chosen])
				switch {
				case cm > cc:
					chosen = m
				case cm == cc && records[m].LoadedOnDay < records[chosen].LoadedOnDay:
					chosen = m
				case cm == cc && records[m].LoadedOnDay == records[chosen].LoadedOnDay &&
					records[m].RecordID < records[chosen].RecordID:
					chosen = m
				}
			}
			if chosen < 0 {
				return ""
			}
			return get(records[chosen])
		}
		assembled := record{
			GivenName:  pick(func(r record) string { return r.GivenName }),
			FamilyName: pick(func(r record) string { return r.FamilyName }),
			Street:     pick(func(r record) string { return r.Street }),
			City:       pick(func(r record) string { return r.City }),
			PostalCode: pick(func(r record) string { return r.PostalCode }),
			BornOn:     pick(func(r record) string { return r.BornOn }),
		}
		golden = append(golden, goldenRecord{
			ClusterID: records[members[0]].RecordID, SurvivorID: s.RecordID,
			MemberIDs: ids, GivenName: assembled.GivenName, FamilyName: assembled.FamilyName,
			Street: assembled.Street, City: assembled.City, PostalCode: assembled.PostalCode,
			BornOn: assembled.BornOn,
			// completeness of the assembled record, which can exceed the survivor's
			MemberCount: len(members), Completeness: completeness(assembled),
		})
	}

	// #MDM-3198: golden records ascend by cluster id; the review queue descends by
	// score, then ascends by left and right record id.
	sort.Slice(golden, func(i, j int) bool { return golden[i].ClusterID < golden[j].ClusterID })
	sort.Slice(reviews, func(i, j int) bool {
		if reviews[i].Score != reviews[j].Score {
			return reviews[i].Score > reviews[j].Score
		}
		if reviews[i].Left != reviews[j].Left {
			return reviews[i].Left < reviews[j].Left
		}
		return reviews[i].Right < reviews[j].Right
	})

	merged := 0
	for _, g := range golden {
		if g.MemberCount > 1 {
			merged++
		}
	}

	// A run writes exactly the three contracted artifacts, so anything an earlier
	// run left behind is cleared first rather than presented as this run's output.
	if entries, err := os.ReadDir(*outputDir); err == nil {
		for _, entry := range entries {
			// RemoveAll, not Remove: a directory an earlier run left behind would
			// otherwise survive and the directory would hold more than the three
			// contracted artifacts.
			os.RemoveAll(*outputDir + "/" + entry.Name())
		}
	}
	if err := os.MkdirAll(*outputDir, 0o755); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	summary := map[string]interface{}{
		"schema_version":            "party-link-v1",
		"record_count":              len(records),
		"block_count":               len(blocks),
		"link_count":                linkCount,
		"cluster_count":             len(golden),
		"merged_cluster_count":      merged,
		"oversized_cluster_count":   oversized,
		"do_not_merge_block_count":  blockedHits,
		"chain_broken_link_count":   chainCuts,
		"review_count":              len(reviews),
		"effective_match_threshold": threshold,
		"effective_review_floor":    reviewFloor,
		"effective_block_prefix":    prefixLen,
		"effective_max_cluster":     maxCluster,
	}
	writeJSON(*outputDir+"/summary.json", summary)
	writeJSON(*outputDir+"/golden_records.json", golden)

	handle, err := os.Create(*outputDir + "/review_queue.jsonl")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer handle.Close()
	enc := json.NewEncoder(handle)
	for _, row := range reviews {
		if err := enc.Encode(row); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	fmt.Fprintf(os.Stderr, "linked %d pairs into %d clusters\n", linkCount, len(golden))
}
