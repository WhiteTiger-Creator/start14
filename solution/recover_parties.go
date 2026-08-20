// Stage one of the reference: rebuild the party master the failed migration
// truncated at /app/data/party_records.json.
//
// Governed by #MDM-3170 (replay semantics) and #MDM-3174 (shape of the result).
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
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

type change struct {
	Seq      int    `json:"seq"`
	RecordID string `json:"record_id"`
	Kind     string `json:"kind"`
	Field    string `json:"field"`
	Value    string `json:"value"`
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

func setField(r *record, field, value string) {
	switch field {
	case "given_name":
		r.GivenName = value
	case "family_name":
		r.FamilyName = value
	case "street":
		r.Street = value
	case "city":
		r.City = value
	case "postal_code":
		r.PostalCode = value
	case "born_on":
		r.BornOn = value
	}
}

func main() {
	var snapshot []record
	var journal []change
	readJSON("/app/data/party_snapshot_pre_migration.json", &snapshot)
	readJSON("/app/data/party_change_journal.json", &journal)

	live := make(map[string]*record, len(snapshot))
	for i := range snapshot {
		r := snapshot[i]
		live[r.RecordID] = &r
	}
	// #MDM-3170: a withdrawal takes the record out but the stewards keep it, so a
	// later reinstatement puts it back exactly as it stood when it was withdrawn --
	// corrections posted before the withdrawal survive, and any correction posted
	// while it was out is ignored.
	held := map[string]record{}

	sort.Slice(journal, func(i, j int) bool { return journal[i].Seq < journal[j].Seq })

	for _, c := range journal {
		switch c.Kind {
		case "correct":
			if r, ok := live[c.RecordID]; ok {
				setField(r, c.Field, c.Value)
			}
		case "withdraw":
			if r, ok := live[c.RecordID]; ok {
				held[c.RecordID] = *r
				delete(live, c.RecordID)
			}
		case "reinstate":
			if r, ok := held[c.RecordID]; ok {
				restored := r
				live[c.RecordID] = &restored
				delete(held, c.RecordID)
			}
		}
	}

	out := make([]record, 0, len(live))
	for _, r := range live {
		out = append(out, *r)
	}
	// #MDM-3174: ascending record_id; journal bookkeeping never survives.
	sort.Slice(out, func(i, j int) bool { return out[i].RecordID < out[j].RecordID })

	encoded, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := os.WriteFile("/app/data/party_records.json", append(encoded, '\n'), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "recovered %d records\n", len(out))
}
