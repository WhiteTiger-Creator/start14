// Party-linkage engine shipped by the failed migration.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
	"strings"
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

// Text is folded to a comparable form before anything is matched on it.
func normalise(s string) string {
	var b strings.Builder
	lastSpace := true
	for _, r := range strings.ToLower(s) {
		switch {
		case r >= 'a' && r <= 'z', r >= '0' && r <= '9', r == '.', r == ',':
			b.WriteRune(r)
			lastSpace = false
		case r == ' ' || r == '\t':
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

// Weighted field agreement, summed across the record.
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

func main() {
	input := flag.String("input", "/app/data/party_records.json", "party records")
	outputDir := flag.String("output-dir", "/app/output", "output directory")
	flag.Parse()

	var records []record
	var pol policy
	var blocked []blockedPair
	// the policy and the register live at fixed paths; --input selects the
	// party records only
	readJSON("/app/data/linkage_policy.json", &pol)
	readJSON("/app/data/do_not_merge.json", &blocked)
	readJSON(*input, &records)

	threshold := pol.Default["match_threshold"]
	reviewFloor := pol.Default["review_floor"]
	prefixLen := pol.Default["block_prefix_len"]
	maxCluster := pol.Default["max_cluster_size"]

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

	// candidates are drawn from a block key built off the normalised name
	blocks := map[string][]int{}
	for i, r := range records {
		fam := normalise(r.FamilyName)
		giv := normalise(r.GivenName)
		if fam == "" {
			continue
		}
		key := fam
		if len(key) > prefixLen {
			key = key[:prefixLen]
		}
		if giv != "" {
			key += "|" + giv[:1]
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
						// the register holds this pair apart
						blockedHits++
						continue
					}
					union(members[x], members[y])
					linkCount++
				} else if s >= reviewFloor {
					reviews = append(reviews, reviewRow{l, r, s, "below_threshold"})
				}
			}
		}
	}

	groups := map[int][]int{}
	for i := range records {
		root := find(i)
		groups[root] = append(groups[root], i)
	}

	roots := make([]int, 0, len(groups))
	for root := range groups {
		roots = append(roots, root)
	}
	sort.Slice(roots, func(i, j int) bool {
		return records[groups[roots[i]][0]].RecordID < records[groups[roots[j]][0]].RecordID
	})

	golden := make([]goldenRecord, 0, len(groups))
	oversized := 0
	for _, root := range roots {
		members := groups[root]
		sort.Slice(members, func(i, j int) bool {
			return records[members[i]].RecordID < records[members[j]].RecordID
		})
		// a cluster far past the policy cap is broken back up into singletons
		if len(members) > 2*maxCluster {
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
		// the survivor is the most complete record, then the load order, then
		// the record id
		best := members[0]
		for _, m := range members[1:] {
			cm, cb := completeness(records[m]), completeness(records[best])
			switch {
			case cm > cb:
				best = m
			case cm == cb && records[m].LoadedOnDay > records[best].LoadedOnDay:
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
		s := records[best]
		golden = append(golden, goldenRecord{
			ClusterID: records[members[0]].RecordID, SurvivorID: s.RecordID,
			MemberIDs: ids, GivenName: s.GivenName, FamilyName: s.FamilyName,
			Street: s.Street, City: s.City, PostalCode: s.PostalCode, BornOn: s.BornOn,
			MemberCount: len(members), Completeness: completeness(s),
		})
	}

	// emission order for the two artifacts
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
