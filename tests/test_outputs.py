"""Verifier tests for this task.

Every test below corresponds to something instruction.md states is graded.
Shared machinery lives in harness.py.
"""

def _source_string_literals(source: str) -> list[str]:
    """Interpreted string literals in a Go file, skipping comments and raw strings.

    A raw substring scan over the whole source would reject a correct program that
    merely names one of these in a comment.
    """
    out: list[str] = []
    i, n = 0, len(source)
    while i < n:
        if source.startswith("//", i):
            k = source.find("\n", i)
            i = n if k < 0 else k + 1
            continue
        if source.startswith("/*", i):
            k = source.find("*/", i + 2)
            i = n if k < 0 else k + 2
            continue
        c = source[i]
        if c == "`":
            k = source.find("`", i + 1)
            i = n if k < 0 else k + 1
            continue
        if c == '"':
            i += 1
            buf = []
            while i < n and source[i] != '"':
                if source[i] == "\\":
                    i += 2
                    continue
                buf.append(source[i])
                i += 1
            out.append("".join(buf))
            i += 1
            continue
        i += 1
    return out


# harness.py sets __all__ explicitly, so the underscored helpers come across too.
from harness import *  # noqa: F401,F403

@pytest.fixture(scope="session")
def primary_outputs():
    return _run_pipeline()


@pytest.fixture(scope="session")
def alternate_outputs():
    return _run_pipeline(input_path=ALT_INPUT)



# --------------------------------------------------------------------------
# Step one: the truncated master must be rebuilt before anything is matched
# --------------------------------------------------------------------------
def test_recovery_sources_are_intact():
    """The extract, journal, policy, register and minute book are read, not rewritten."""
    live = {n: hashlib.sha256(Path(p).read_bytes()).hexdigest() for n, p in (
        ("extract", EXTRACT_PATH), ("journal", JOURNAL_PATH),
        ("policy", DATA / "linkage_policy.json"), ("dnm", DATA / "do_not_merge.json"),
        # instruction.md names the contract among the files that come back
        # byte-identical, and the schema comparison beside this one is satisfied
        # by any file that merely parses the same.
        ("contract", SPEC_PATH),
        ("log", LOG_PATH))}
    assert _digest(live) == FIXTURE["rule_sources_digest"]


def test_master_was_recovered():
    """The rebuilt master matches the governed replay exactly."""
    recovered = _load_json(MASTER_PATH)
    assert len(recovered) == FIXTURE["recovered_record_count"]
    assert _digest(recovered) == FIXTURE["recovered_master_digest"]


def test_recovered_records_carry_only_the_source_fields():
    """Journal bookkeeping never survives the replay."""
    for row in _load_json(MASTER_PATH):
        assert set(row) == RECORD_KEYS


def test_recovered_master_is_sorted():
    """The master ascends by record_id."""
    ids = [r["record_id"] for r in _load_json(MASTER_PATH)]
    assert ids == sorted(ids)


def test_the_rebuilt_master_uses_the_serialisation_the_contract_states():
    """The master is graded on its bytes too, not only on its content.

    reconciled_inputs in the contract spells the rebuilt file out as a
    two-space-indented JSON array with a trailing newline, and every other check
    on it goes through the whitespace-insensitive digest, which one long
    unindented line would satisfy just as well.
    """
    raw = MASTER_PATH.read_text(encoding="utf-8")
    assert raw.endswith("\n") and not raw.endswith("\n\n"), "no trailing newline"
    assert _as_contract_layout(raw) == json.dumps(
        json.loads(raw), indent=2, ensure_ascii=False) + "\n", (
        "the rebuilt master is not two-space-indented JSON")


def _as_contract_layout(raw: str) -> str:
    """The text with encoder-specific escaping normalised away.

    The contract fixes the LAYOUT -- two-space indent, trailing newline -- not the
    escape style, and the two encoders disagree: Go's json.Marshal writes `<`, `>`
    and `&` as \\u003c, \\u003e and \\u0026 and emits non-ASCII as literal UTF-8,
    while Python's json.dumps does the opposite on both counts. Comparing raw bytes
    against Python's rendering therefore failed a correct Go engine the moment any
    of those characters reached the data -- and the normalisation this task grades
    keeps letters that are not ASCII. Normalising both sides leaves the indent and
    the newline pinned exactly, which is what the contract actually states.
    """
    for escaped, literal in (("\\u003c", "<"), ("\\u003e", ">"), ("\\u0026", "&")):
        raw = raw.replace(escaped, literal)
    return raw


def test_wrong_replays_differ_from_the_governed_master():
    """Three plausible misreadings of the replay each give a different master.

    Concatenating the sources, replaying in file order instead of by sequence, and
    letting a reinstatement re-read the extract rather than the held state all
    diverge, so matching the sealed digest is evidence of the governed rule.
    """
    expected = FIXTURE["recovered_master_digest"]
    assert FIXTURE["shipped_truncated_digest"] != expected
    extract = {r["record_id"]: r for r in _load_json(EXTRACT_PATH)}
    journal = _load_json(JOURNAL_PATH)

    def replay(by_seq: bool, reinstate_from_extract: bool):
        live = {k: dict(v) for k, v in extract.items()}
        held = {}
        for c in (sorted(journal, key=lambda x: x["seq"]) if by_seq else journal):
            rid, kind = c["record_id"], c["kind"]
            if kind == "correct" and rid in live:
                live[rid][c["field"]] = c["value"]
            elif kind == "withdraw" and rid in live:
                held[rid] = dict(live.pop(rid))
            elif kind == "reinstate":
                if reinstate_from_extract:
                    if rid in extract and rid not in live:
                        live[rid] = dict(extract[rid])
                elif rid in held:
                    live[rid] = held.pop(rid)
        return _digest(sorted(live.values(), key=lambda r: r["record_id"]))

    assert replay(False, False) != expected
    assert replay(True, True) != expected


# --------------------------------------------------------------------------
# Step two: the match itself
# --------------------------------------------------------------------------
def test_primary_summary_matches_fixture(primary_outputs):
    """Every summary field matches the sealed reference run."""
    _, summary, _, _ = primary_outputs
    assert summary == FIXTURE["primary"]["summary"]


def test_primary_artifacts_match_fixture(primary_outputs):
    """Golden records and the review queue match the sealed digests."""
    _, _, golden, reviews = primary_outputs
    assert _digest(golden) == FIXTURE["primary"]["golden_digest"]
    assert _digest(reviews) == FIXTURE["primary"]["review_digest"]


def test_alternate_master_matches_fixture(alternate_outputs):
    """A held-out master the agent never sees produces the sealed result."""
    _, summary, golden, reviews = alternate_outputs
    assert summary == FIXTURE["alternate"]["summary"]
    assert _digest(golden) == FIXTURE["alternate"]["golden_digest"]
    assert _digest(reviews) == FIXTURE["alternate"]["review_digest"]


def test_output_dir_contains_exactly_three_files(primary_outputs):
    """A run writes the three contracted artifacts and nothing else."""
    out_dir, _, _, _ = primary_outputs
    assert sorted(p.name for p in out_dir.iterdir()) == [
        "golden_records.json", "review_queue.jsonl", "summary.json"]


def test_summary_schema_and_types(primary_outputs):
    """The summary carries exactly the contracted fields at the contracted types."""
    _, summary, _, _ = primary_outputs
    assert set(summary) == SUMMARY_KEYS
    for field, kind in SPEC["outputs"]["summary"]["field_types"].items():
        value = summary[field]
        if kind == "integer":
            assert isinstance(value, int) and not isinstance(value, bool), field
        else:
            assert isinstance(value, str), field


def test_golden_schema_and_sorting(primary_outputs):
    """Golden records carry the contracted fields and the contracted order."""
    _, _, golden, _ = primary_outputs
    assert [g["cluster_id"] for g in golden] == sorted(g["cluster_id"] for g in golden)
    for g in golden:
        assert set(g) == GOLDEN_KEYS
        assert g["member_ids"] == sorted(g["member_ids"])
        assert g["member_count"] == len(g["member_ids"])
        assert g["survivor_id"] in g["member_ids"]
        assert g["cluster_id"] == g["member_ids"][0]


def test_review_schema_and_sorting(primary_outputs):
    """Review rows carry the contracted fields and descend by score."""
    _, _, _, reviews = primary_outputs
    keys = [(-r["score"], r["left"], r["right"]) for r in reviews]
    assert keys == sorted(keys)
    for r in reviews:
        assert set(r) == REVIEW_KEYS
        assert r["reason"] in REVIEW_REASONS


def test_every_record_lands_in_exactly_one_cluster(primary_outputs):
    """Clustering partitions the master: no record is lost or duplicated."""
    _, summary, golden, _ = primary_outputs
    members = [m for g in golden for m in g["member_ids"]]
    assert len(members) == len(set(members))
    assert set(members) == {r["record_id"] for r in _load_json(MASTER_PATH)}
    assert summary["cluster_count"] == len(golden)
    assert summary["record_count"] == len(members)


def test_every_documented_review_reason_occurs(primary_outputs):
    """The graded master exercises every review reason the contract documents."""
    _, _, _, reviews = primary_outputs
    assert {r["reason"] for r in reviews} == REVIEW_REASONS


# --------------------------------------------------------------------------
# Each reversed rule, pinned on an instance where the drafts disagree
# --------------------------------------------------------------------------
BASE_POLICY = {"default": {"match_threshold": 62, "review_floor": 48,
                           "block_prefix_len": 4, "max_cluster_size": 12}}


def _rec(rid, family, given="alpha", day=0, **kw):
    base = {"record_id": rid, "source_system": "crm", "given_name": given,
            "family_name": family, "street": "12 oak street", "city": "arden",
            "postal_code": "A11", "born_on": "1980-01-01", "loaded_on_day": day}
    base.update(kw)
    return base


def _probe(records, policy=None, do_not_merge=None):
    """Run the submitted engine over a crafted master and return its artifacts."""
    saved = {name: (DATA / name).read_text(encoding="utf-8")
             for name in ("linkage_policy.json", "do_not_merge.json")}
    staged = _CWORK / f"probe-{next(_run_ctr)}.json"
    try:
        _write_json(DATA / "linkage_policy.json", policy or BASE_POLICY)
        _write_json(DATA / "do_not_merge.json", do_not_merge or [])
        _write_json(staged, records)
        os.chmod(staged, 0o644)
        return _run_pipeline(input_path=staged)
    finally:
        for name, text in saved.items():
            (DATA / name).write_text(text, encoding="utf-8")


def test_candidates_come_only_from_a_shared_block():
    """Two records that agree on everything but the family name never meet.

    Their normalised family-name prefixes differ, so they fall in different
    blocks and are never scored against each other -- a file-wide comparison
    would link them on the strength of every other field.
    """
    _, summary, golden, _ = _probe([
        _rec("REC-000001", "aaaaxx"),
        _rec("REC-000002", "bbbbxx"),
    ])
    assert summary["link_count"] == 0
    assert [g["member_count"] for g in golden] == [1, 1]


def test_normalisation_keeps_letters_that_are_not_ascii():
    """#MDM-3182 drops what is not a letter or a digit, and keeps what is.

    A letter is a letter whatever alphabet it comes from. An engine that tests
    a-z instead drops the accented characters, which shortens the value the
    block key is cut from: "Bo\u00e9tie" normalises to "botie" there and blocks
    on "boti", while "Botie" blocks on "boti" too, so the two are compared and
    linked when the governed reading keeps them apart on "boet" against "boti".
    """
    _, summary, golden, _ = _probe([
        _rec("REC-000001", "Bo\u00e9tie"),
        _rec("REC-000002", "Botie"),
    ])
    assert summary["link_count"] == 0, (
        "the accented letter was dropped rather than kept, so two records that "
        "block apart under the governed normalisation were compared")
    assert [g["member_count"] for g in golden] == [1, 1]


def test_the_block_key_is_cut_in_characters_not_bytes():
    """#MDM-3184 counts characters, and UTF-8 makes the two readings differ.

    The accented case above passes whichever way the string is sliced, because
    the first four bytes of "bo\u00e9tie" still differ from those of "botie". These
    two pairs separate the readings: each pair shares a leading byte sequence and
    differs in the character that byte sequence begins, so an engine slicing by
    byte offset puts them in one block and compares them, while the governed
    reading keeps them apart. Every other field agrees, so a comparison that
    happens at all scores far above the threshold and links.
    """
    # the family prefix: "bo\u00e9tie" and "bo\u00e9xyz" share their first four BYTES
    # ("b", "o" and the two bytes of "\u00e9") but differ in their fourth CHARACTER
    _, summary, golden, _ = _probe([
        _rec("REC-000001", "Bo\u00e9tie"),
        _rec("REC-000002", "Bo\u00e9xyz"),
    ])
    assert summary["link_count"] == 0, (
        "the family prefix was cut at four bytes rather than four characters, so "
        "two names that block apart were compared and linked")
    assert [g["member_count"] for g in golden] == [1, 1]

    # the given initial: "\u00e1ngel" and "\u00e0urea" begin with different characters that
    # share their first byte, so a one-byte slice makes the initials equal
    _, summary, golden, _ = _probe([
        _rec("REC-000001", "Marsh", given="\u00c1ngel"),
        _rec("REC-000002", "Marsh", given="\u00c0urea"),
    ])
    assert summary["link_count"] == 0, (
        "the given initial was taken as one byte rather than one character, so "
        "two records whose initials differ were compared and linked")
    assert [g["member_count"] for g in golden] == [1, 1]


def test_the_byte_and_character_readings_really_do_differ_here():
    """Otherwise the test above would pass on an engine that slices bytes."""
    for left, right, prefix in (("bo\u00e9tie", "bo\u00e9xyz", 4), ("\u00e1ngel", "\u00e0urea", 1)):
        assert left.encode()[:prefix] == right.encode()[:prefix], (left, right)
        assert left[:prefix] != right[:prefix], (left, right)


def test_a_record_with_no_family_name_joins_no_block():
    """#MDM-3184: an empty family name takes a record out of blocking entirely.

    Two such records agree on every other field and would score far above the
    threshold if they were ever compared. They are not, because neither is in a
    block, so each is published on its own.
    """
    _, summary, golden, _ = _probe([
        _rec("REC-000001", "", given="alpha"),
        _rec("REC-000002", "", given="alpha"),
    ])
    assert summary["link_count"] == 0, "records without a family name were compared"
    assert [g["member_count"] for g in golden] == [1, 1]


def test_records_with_no_given_name_still_block_together():
    """#MDM-3184: only an empty FAMILY name takes a record out of blocking.

    Where the given name is empty the key still carries the bar with nothing
    after it, so these two share a block and are compared. Setting them aside
    alongside the empty-family case would lose the link.
    """
    _, summary, golden, _ = _probe([
        _rec("REC-000001", "smithxx", given=""),
        _rec("REC-000002", "smithxx", given=""),
    ])
    assert summary["link_count"] == 1, "records without a given name were not compared"
    assert [g["member_count"] for g in golden] == [2]


def test_a_dissolved_cluster_queues_one_row_per_record_naming_it_twice():
    """#MDM-3194: a cluster_too_large row concerns one record, not a pair.

    It carries that record's own id on both sides and a score of zero, which is
    also what the queue sorts on.
    """
    policy = {"default": dict(BASE_POLICY["default"], max_cluster_size=2)}
    records = [_rec(f"REC-{i:06d}", "smithxx", day=i) for i in range(1, 4)]
    _, summary, golden, reviews = _probe(records, policy=policy)
    dissolved = [r for r in reviews if r["reason"] == "cluster_too_large"]
    assert len(dissolved) == 3, dissolved
    for row in dissolved:
        assert row["left"] == row["right"], row
        assert row["score"] == 0, row
    assert {row["left"] for row in dissolved} == {r["record_id"] for r in records}
    assert [g["member_count"] for g in golden] == [1, 1, 1]


def test_do_not_merge_pair_is_queued_not_silently_dropped():
    """A pair on the register does not link and IS reported, per the revision."""
    _, summary, golden, reviews = _probe(
        [_rec("REC-000001", "carverov"), _rec("REC-000002", "carverov")],
        do_not_merge=[{"left": "REC-000001", "right": "REC-000002"}])
    assert summary["link_count"] == 0
    assert summary["do_not_merge_block_count"] == 1
    assert [g["member_count"] for g in golden] == [1, 1]
    assert [(r["left"], r["right"], r["reason"]) for r in reviews] == [
        ("REC-000001", "REC-000002", "do_not_merge")]


def test_a_cluster_reached_only_by_a_chain_is_cut_at_its_weakest_link():
    """#MDM-3230: three records joined by a chain are not a cluster.

    The first and last agree on family and given name alone -- 52, under the
    threshold -- so the group is only reached by walking through the middle
    record. Cohesion is judged on that pair too, though it never linked, and the
    weaker of the two accepted links is the one that goes.
    """
    _, summary, golden, reviews = _probe([
        _rec("REC-000001", "smithxx", born_on="1980-01-01", postal_code="A11",
             street="1 a street", city="arden"),
        _rec("REC-000002", "smithxx", born_on="1980-01-01", postal_code="B22",
             street="2 b street", city="brent"),
        _rec("REC-000003", "smithxx", born_on="1999-09-09", postal_code="B22",
             street="3 c street", city="crown"),
    ])
    assert summary["link_count"] == 2, "the chain did not form in the first place"
    assert summary["chain_broken_link_count"] == 1
    cuts = [r for r in reviews if r["reason"] == "chain_broken"]
    assert cuts == [{"left": "REC-000002", "right": "REC-000003", "score": 70,
                     "reason": "chain_broken"}], cuts
    assert [(g["cluster_id"], g["member_ids"]) for g in golden] == [
        ("REC-000001", ["REC-000001", "REC-000002"]),
        ("REC-000003", ["REC-000003"])]


def test_a_cluster_every_pair_agrees_on_is_left_whole():
    """The cut falls on chains, not on clusters that are cohesive already.

    All three pairs score 72 here, so nothing is cut and the three stay one
    cluster -- an engine that split every group of three would fail this.
    """
    _, summary, golden, reviews = _probe([
        _rec("REC-000001", "smithxx", born_on="1980-01-01", postal_code="A11",
             street="1 a street", city="arden"),
        _rec("REC-000002", "smithxx", born_on="1980-01-01", postal_code="B22",
             street="2 b street", city="brent"),
        _rec("REC-000003", "smithxx", born_on="1980-01-01", postal_code="C33",
             street="3 c street", city="crown"),
    ])
    assert summary["chain_broken_link_count"] == 0
    assert [r for r in reviews if r["reason"] == "chain_broken"] == []
    assert [g["member_count"] for g in golden] == [3]


def test_a_registered_pair_is_never_cohesive_however_well_it_scores():
    """A do-not-merge pair may not be reached through a third record either.

    Every pair here scores 72, so the group is cohesive on the numbers alone; the
    register still holds the first and last apart, and #MDM-3190 only stops them
    linking DIRECTLY. Cohesion is what keeps them out of one cluster, and the tie
    on score sends the cut to the pair that sorts first.
    """
    _, summary, golden, reviews = _probe([
        _rec("REC-000001", "smithxx", born_on="1980-01-01", postal_code="A11",
             street="1 a street", city="arden"),
        _rec("REC-000002", "smithxx", born_on="1980-01-01", postal_code="B22",
             street="2 b street", city="brent"),
        _rec("REC-000003", "smithxx", born_on="1980-01-01", postal_code="C33",
             street="3 c street", city="crown"),
    ], do_not_merge=[{"left": "REC-000001", "right": "REC-000003"}])
    assert summary["do_not_merge_block_count"] == 1
    assert summary["chain_broken_link_count"] == 1
    cuts = [r for r in reviews if r["reason"] == "chain_broken"]
    assert cuts == [{"left": "REC-000001", "right": "REC-000002", "score": 72,
                     "reason": "chain_broken"}], cuts
    assert [(g["cluster_id"], g["member_ids"]) for g in golden] == [
        ("REC-000001", ["REC-000001"]),
        ("REC-000002", ["REC-000002", "REC-000003"])]
    together = [g for g in golden
                if {"REC-000001", "REC-000003"} <= set(g["member_ids"])]
    assert not together, "the register's pair still shares a cluster"


def test_oversized_cluster_is_dissolved_into_singletons():
    """A cluster over the cap is not trusted: it becomes singletons, all queued."""
    records = [_rec(f"REC-{i:06d}", "delacroixo") for i in range(1, 15)]
    _, summary, golden, reviews = _probe(records, policy={"default": {
        "match_threshold": 62, "review_floor": 48,
        "block_prefix_len": 4, "max_cluster_size": 12}})
    assert summary["oversized_cluster_count"] == 1
    assert summary["cluster_count"] == 14
    assert all(g["member_count"] == 1 for g in golden)
    assert sum(1 for r in reviews if r["reason"] == "cluster_too_large") == 14


def test_survivor_of_a_tie_is_the_earliest_loaded_record():
    """Equally complete records tie to the EARLIEST load, not the freshest."""
    _, _, golden, _ = _probe([
        _rec("REC-000001", "eriksson", day=900),
        _rec("REC-000002", "eriksson", day=10),
    ])
    assert len(golden) == 1
    assert golden[0]["survivor_id"] == "REC-000002"


def test_completeness_outranks_the_load_order():
    """A more complete record survives even when it loaded later."""
    _, _, golden, _ = _probe([
        _rec("REC-000001", "fontaine", day=5, city="", born_on=""),
        _rec("REC-000002", "fontaine", day=800),
    ])
    assert len(golden) == 1
    assert golden[0]["survivor_id"] == "REC-000002"
    assert golden[0]["completeness"] == 6


def test_golden_record_is_assembled_field_by_field_not_copied_from_the_survivor():
    """#MDM-3220: a gap in the survivor's row is filled by a sibling that has it.

    The obvious reading -- the survivor's record IS the golden record -- is what
    the shipped engine does, and it loses a field the cluster demonstrably knows.
    Here the survivor is the more complete record but has no postal code, while a
    less complete sibling carries one; the assembled record must take it, and its
    completeness must be the assembled record's rather than the survivor's.
    """
    _, _, golden, _ = _probe([
        _rec("REC-000001", "halvorsen", day=5, postal_code=""),
        _rec("REC-000002", "halvorsen", day=9, born_on=""),
    ])
    assert len(golden) == 1, golden
    row = golden[0]
    # Both carry five of six fields, so the tie goes to the earlier load and
    # REC-000001 survives -- and it is the one missing the postal code.
    assert row["survivor_id"] == "REC-000001", row["survivor_id"]
    assert row["postal_code"] == "A11", "the postal code its sibling carried was dropped"
    assert row["born_on"] == "1980-01-01"
    assert row["completeness"] == 6, (
        "completeness must describe the assembled record, not the survivor's five")


def test_a_field_no_member_fills_stays_empty():
    """Assembly invents nothing: a field absent from every member stays empty."""
    _, _, golden, _ = _probe([
        _rec("REC-000001", "ingemarsson", day=5, born_on=""),
        _rec("REC-000002", "ingemarsson", day=9, born_on=""),
    ])
    assert len(golden) == 1, golden
    assert golden[0]["born_on"] == "", "assembly invented a value no member held"
    assert golden[0]["completeness"] == 5


def test_empty_field_is_no_evidence_rather_than_disagreement():
    """A field missing on one side neither adds nor removes score.

    Both records keep enough agreeing weight to clear the threshold, so the
    missing town does not hold them apart.
    """
    _, summary, _, _ = _probe([
        _rec("REC-000001", "gruberez", city=""),
        _rec("REC-000002", "gruberez"),
    ])
    assert summary["link_count"] == 1


# --------------------------------------------------------------------------
# Contract, budget, determinism and isolation
# --------------------------------------------------------------------------
def test_policy_path_actually_influences_the_output():
    """The policy is resolved from its fixed path, not inlined as constants."""
    saved = (DATA / "linkage_policy.json").read_text(encoding="utf-8")
    try:
        _write_json(DATA / "linkage_policy.json", {"default": {
            "match_threshold": 95, "review_floor": 30,
            "block_prefix_len": 3, "max_cluster_size": 5}})
        _, summary, _, _ = _run_pipeline()
        assert summary["effective_match_threshold"] == 95
        assert summary["effective_review_floor"] == 30
        assert summary["effective_block_prefix"] == 3
        assert summary["effective_max_cluster"] == 5
        assert summary != FIXTURE["primary"]["summary"]
    finally:
        (DATA / "linkage_policy.json").write_text(saved, encoding="utf-8")


def test_do_not_merge_path_actually_influences_the_output():
    """The register is resolved from its fixed path too."""
    saved = (DATA / "do_not_merge.json").read_text(encoding="utf-8")
    try:
        _write_json(DATA / "do_not_merge.json", [])
        _, summary, _, _ = _run_pipeline()
        assert summary["do_not_merge_block_count"] == 0
        assert summary != FIXTURE["primary"]["summary"]
    finally:
        (DATA / "do_not_merge.json").write_text(saved, encoding="utf-8")


def test_run_is_idempotent(primary_outputs):
    """Re-running over the same master reproduces the same artifacts."""
    _, summary, golden, reviews = primary_outputs
    _, s2, g2, r2 = _run_pipeline()
    assert s2 == summary and _digest(g2) == _digest(golden) and _digest(r2) == _digest(reviews)


def test_no_argument_run_writes_to_the_documented_default_output_dir(primary_outputs):
    """With no flags at all the engine reads and writes its documented defaults.

    The previous form passed --output-dir, so it only ever exercised the --input
    default; changing the default output directory went unnoticed.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    default_out = Path(SPEC["cli"]["output_dir"].split("default ")[-1].strip())
    assert str(default_out) == "/app/output"
    # shared state: emptied rather than replaced, and the mode restored below
    default_out.mkdir(parents=True, exist_ok=True)
    before_mode = default_out.stat().st_mode & 0o777
    for stale in sorted(default_out.iterdir()):
        stale.unlink() if stale.is_file() or stale.is_symlink() else shutil.rmtree(stale)
    default_out.mkdir(parents=True, exist_ok=True)
    os.chmod(default_out, 0o777)
    result = _run_agent([binary], cwd=_candidate_dir())
    # the exit code is a precondition; the verdict is the default directory below
    assert result.returncode == 0, (
        f"the run exited {result.returncode}\n"
        f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
    assert sorted(q.name for q in default_out.iterdir()) == [
        "golden_records.json", "review_queue.jsonl", "summary.json"]
    _, summary, golden, reviews = primary_outputs
    assert _load_json(default_out / "summary.json") == summary
    assert _digest(_load_json(default_out / "golden_records.json")) == _digest(golden)
    assert _digest(_load_jsonl(default_out / "review_queue.jsonl")) == _digest(reviews)
    os.chmod(default_out, before_mode)



def test_output_artifacts_use_the_contracted_serialisation(primary_outputs):
    """The three files are written exactly as the contract spells them out.

    Byte-for-byte: two-space indent and a trailing newline for the two JSON
    documents, one compact object per line for the queue.
    """
    out_dir, summary, golden, reviews = primary_outputs
    assert _as_contract_layout(
        (out_dir / "summary.json").read_text(encoding="utf-8")) == \
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    assert _as_contract_layout(
        (out_dir / "golden_records.json").read_text(encoding="utf-8")) == \
        json.dumps(golden, indent=2, ensure_ascii=False) + "\n"
    raw = (out_dir / "review_queue.jsonl").read_text(encoding="utf-8")
    assert raw.endswith("\n") and "\n\n" not in raw
    lines = raw.splitlines()
    assert len(lines) == len(reviews)
    for line, row in zip(lines, reviews):
        assert _as_contract_layout(line) == json.dumps(
            row, separators=(",", ":"), ensure_ascii=False)


def test_staging_the_run_input_does_not_follow_a_planted_link():
    """The master sits on the one /app/data path the agent replaces, and staging runs as root.

    Every graded run copies /app/data/party_records.json into the candidate's own
    work area. That copy followed the source link, so a submission that left a
    symlink there instead of a rebuilt master pointed root at whatever it named --
    the sealed fixtures under /tests included -- and had the contents laid down at
    0644 where the graded program reads them. Staging now refuses anything that is
    not a regular file, and this plants the link to prove it.
    """
    sentinel = Path("/tests/fixtures/expected_report.json")
    if not sentinel.exists():
        sentinel = SPEC_PATH
    original = MASTER_PATH.read_bytes()
    mode = MASTER_PATH.stat().st_mode & 0o7777
    try:
        MASTER_PATH.unlink()
        MASTER_PATH.symlink_to(sentinel)
        staged = _candidate_dir() / "master.json"
        with pytest.raises(AssertionError):
            _stage_input(MASTER_PATH, staged)
        assert not staged.exists(), (
            "the planted link was staged anyway, so its target is now readable "
            "at the path the graded program is handed")
    finally:
        if MASTER_PATH.is_symlink() or MASTER_PATH.exists():
            MASTER_PATH.unlink()
        MASTER_PATH.write_bytes(original)
        os.chmod(MASTER_PATH, mode)
    assert MASTER_PATH.read_bytes() == original


def test_an_engine_run_rewrites_nothing_under_app_data():
    """instruction.md says an engine run rewrites nothing under /app/data at all.

    The intactness check at the top of this file runs before any engine run in
    file order, so an engine that rebuilt the master, the policy or the register
    while it ran still satisfied it. This hashes the whole tree either side of a
    run of its own, so the ordering carries no weight.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)

    def tree() -> dict:
        return {str(q.relative_to(DATA)): hashlib.sha256(q.read_bytes()).hexdigest()
                for q in sorted(DATA.rglob("*")) if q.is_file()}

    before = tree()
    result = _run_agent([binary, "--output-dir", str(out_dir)], cwd=work)
    assert result.returncode == 0, (
        f"the run exited {result.returncode}\n"
        f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
    after = tree()
    assert after == before, (
        "the engine wrote under /app/data: "
        f"changed {sorted(set(before) & set(after) - {k for k in before if before[k] == after.get(k)})}, "
        f"added {sorted(set(after) - set(before))}, removed {sorted(set(before) - set(after))}")


def test_the_engine_is_one_go_source_with_no_sibling_beside_it():
    """instruction.md makes the deliverable that one Go source compiled from that file alone.

    _build copies /app/workflow/link_parties.go to a temp directory as main.go and
    compiles it there, so a submission split across siblings fails with an
    undefined-symbol error that does not say why. This states the rule and names
    the siblings when it fails. It deliberately does NOT ban them: the instruction
    says the master-rebuild tooling is the agent's to put where it likes, so a
    stray file in this directory is not by itself a breach.
    """
    engine = WORKFLOW_PATH.resolve()
    # The rule instruction.md states is that the engine COMPILES FROM THAT FILE
    # ALONE -- not that the directory is empty. It also says whatever rebuilt the
    # master is the agent's to put where it likes, so banning every sibling here
    # failed a submission that had done nothing wrong. The build is the check: a
    # submission whose engine leans on a sibling does not compile from the one
    # file, and the siblings are named only to say why.
    siblings = sorted(q.name for q in WORKFLOW_PATH.parent.glob("*.go")
                      if q.resolve() != engine and not q.name.startswith((".", "_")))
    try:
        _build(WORKFLOW_PATH)
    except AssertionError as exc:
        raise AssertionError(
            f"{WORKFLOW_PATH.name} does not compile on its own, as instruction.md "
            f"requires. Sibling sources beside it, which never join this build: "
            f"{siblings}\n\n{exc}") from exc


def test_a_binary_left_beside_the_engine_is_not_what_gets_graded():
    """instruction.md names the case outright: "no binary you leave behind is read".

    The test above checks the source side of that rule, and nothing checked this
    side. A submission that got its answer from a pre-built executable rather than
    from the delivered source would be graded on the executable if anything ever
    picked it up. This plants one that fails on sight and requires the run to be
    unaffected, so the grading path is proved to go through the compiler.
    """
    # An agent that ran `go build link_parties.go` here and left the artefact has
    # done nothing the instruction forbids -- it says such a binary is not read,
    # not that it may not exist -- so anything already sitting there is put back
    # afterwards rather than treated as a failure.
    planted = WORKFLOW_PATH.parent / WORKFLOW_PATH.stem
    existing = planted.read_bytes() if planted.is_file() else None
    existing_mode = planted.stat().st_mode & 0o7777 if planted.is_file() else None
    planted.write_text("#!/bin/sh\nexit 3\n", encoding="utf-8")
    os.chmod(planted, 0o755)
    try:
        _, summary, golden, reviews = _run_pipeline()
        assert summary == FIXTURE["primary"]["summary"], (
            "the graded run changed once an executable was planted beside the "
            "source, so something other than the compiled source was read")
        assert _digest(golden) == FIXTURE["primary"]["golden_digest"]
        assert _digest(reviews) == FIXTURE["primary"]["review_digest"]
    finally:
        planted.unlink()
        if existing is not None:
            planted.write_bytes(existing)
            os.chmod(planted, existing_mode)


def test_stale_files_are_cleared_from_the_output_directory():
    """A run presents its own artifacts, not whatever an earlier run left behind."""
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    stale = out_dir / "golden_records.json"
    stale.write_text("[]\n", encoding="utf-8")
    os.chmod(stale, 0o666)
    junk = out_dir / "leftover_from_last_run.json"
    junk.write_text('{"stale": true}\n', encoding="utf-8")
    os.chmod(junk, 0o666)
    # A directory counts as a leftover too: the contract says the output directory
    # holds exactly the three artifacts, not three artifacts and a stray folder.
    stale_dir = out_dir / "leftover_dir"
    stale_dir.mkdir()
    (stale_dir / "inner.json").write_text("{}\n", encoding="utf-8")
    os.chmod(stale_dir / "inner.json", 0o666)
    os.chmod(stale_dir, 0o777)
    # instruction.md and the contract both say the directory itself stays where
    # it is; checking only the resulting names let a RemoveAll+MkdirAll pass, so
    # the inode and the mode are taken before the run and compared after.
    before = out_dir.stat()
    result = _run_agent([binary, "--output-dir", str(out_dir)], cwd=work)
    assert result.returncode == 0, (
        f"the run exited {result.returncode}\n"
        f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
    assert sorted(q.name for q in out_dir.iterdir()) == [
        "golden_records.json", "review_queue.jsonl", "summary.json"]
    assert _load_json(out_dir / "golden_records.json") != []
    after = out_dir.stat()
    assert (after.st_ino, after.st_dev) == (before.st_ino, before.st_dev), (
        "the output directory was replaced rather than cleared; the contract says "
        "the run clears the contents and leaves the directory itself in place")
    # the mode is deliberately NOT asserted: the contract says the contents are
    # cleared and the directory itself stays, and the inode check above is what
    # proves that. Neither it nor instruction.md says anything about the mode.


def test_recovery_sources_are_still_intact_after_a_graded_run(primary_outputs):
    """The same digest, taken after the engine has actually run.

    The check at the top of this file runs before any engine does, so an engine
    that rewrote something under /app/data while it worked was caught only by
    filesystem permissions rather than by an assertion. This repeats the
    comparison once a graded run has completed.
    """
    live = {n: hashlib.sha256(Path(p).read_bytes()).hexdigest() for n, p in (
        ("extract", EXTRACT_PATH), ("journal", JOURNAL_PATH),
        ("policy", DATA / "linkage_policy.json"), ("dnm", DATA / "do_not_merge.json"),
        ("contract", SPEC_PATH), ("log", LOG_PATH))}
    assert _digest(live) == FIXTURE["rule_sources_digest"], (
        "an input was rewritten while the graded run was in flight")


def test_a_cluster_cap_of_zero_dissolves_every_cluster():
    """#MDM-3194 compares directly, so a cap of zero leaves nothing clustered.

    "A cluster holding more than max_cluster_size records is not trusted" is true
    of every cluster when the cap is zero. The engine guarded the rule on a
    positive cap, which turned zero into no cap at all -- the opposite reading,
    and one no document supports.
    """
    records = [
        _rec("REC-000001", "Marsh", given="alpha"),
        _rec("REC-000002", "Marsh", given="alpha"),
    ]
    _, summary, golden, reviews = _probe(records, policy={"default": {
        "match_threshold": 62, "review_floor": 48,
        "block_prefix_len": 4, "max_cluster_size": 0}})
    assert summary["effective_max_cluster"] == 0
    assert [g["member_count"] for g in golden] == [1, 1], (
        "a cap of zero left a cluster standing, so the rule was skipped entirely")
    assert {r["reason"] for r in reviews} == {"cluster_too_large"}
    assert summary["oversized_cluster_count"] >= 1


def test_missing_policy_fields_fall_back_to_the_governed_baseline():
    """A field the policy file omits keeps its baseline; it is not read as zero.

    An empty policy object must still resolve match_threshold 62, review_floor 48,
    block_prefix_len 4 and max_cluster_size 12.
    """
    _, summary, _, _ = _probe([_rec("REC-000001", "carverov"),
                               _rec("REC-000002", "carverov")],
                              policy={"default": {}})
    assert summary["effective_match_threshold"] == 62
    assert summary["effective_review_floor"] == 48
    assert summary["effective_block_prefix"] == 4
    assert summary["effective_max_cluster"] == 12
    # a zero threshold would have linked everything in sight
    assert summary["link_count"] == 1


def test_graded_run_is_killed_if_it_exceeds_the_documented_budget(primary_outputs):
    """The budget is enforced, and not by comparing a measured elapsed time.

    Every candidate run is executed with the published budget as its hard
    timeout, so a run that overruns is killed and the suite fails outright; there
    is no wall-clock threshold here to go flaky on a loaded machine.
    """
    assert HARD_TIMEOUT_SEC == int(RUNTIME_BUDGET_SEC)
    assert primary_outputs[1]["cluster_count"] > 0, "the graded run did not complete"


def test_runtime_budget_is_stated_in_the_contract():
    """The budget enforced above is the one the contract publishes."""
    assert int(SPEC["runtime_budget_seconds"]) == int(RUNTIME_BUDGET_SEC)


def test_submitted_program_runs_unprivileged_and_cannot_write_reward(tmp_path):
    """The graded program runs as nobody and cannot touch the reward path."""
    probe = tmp_path / "main.go"
    probe.write_text(
        'package main\n\nimport ("fmt"; "os")\n\n'
        'func main() {\n\tfmt.Println(os.Getuid())\n'
        '\terr := os.WriteFile("/logs/verifier/reward.txt", []byte("1"), 0o644)\n'
        '\tfmt.Println(err != nil)\n}\n', encoding="utf-8")
    binary = _build(probe)
    result = _run_agent([binary], cwd=_candidate_dir())
    # the exit code is a precondition; the verdict is the probe's own two lines
    assert result.returncode == 0, (
        f"the run exited {result.returncode}\n"
        f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
    parts = result.stdout.split()
    assert parts[0] == str(CANDIDATE_UID) and parts[1] == "true"


def test_frozen_snapshot_preserved():
    """The migration's engine must still be on disk, unmodified."""
    assert ORIGINAL_WORKFLOW_PATH.exists()
    assert hashlib.sha256(ORIGINAL_WORKFLOW_PATH.read_bytes()).hexdigest() == \
        FIXTURE["broken_engine_sha256"]


def test_frozen_snapshot_is_wrong(primary_outputs):
    """The shipped engine does not already produce the governed match."""
    _, summary, _, _ = primary_outputs
    _, broken, _, _ = _run_pipeline(script_path=ORIGINAL_WORKFLOW_PATH)
    assert broken != summary


def test_governance_log_present():
    """The minute book the rules are reconstructed from is in the environment."""
    assert LOG_PATH.exists() and LOG_PATH.stat().st_size > 0


def test_engine_does_not_reference_test_artifacts():
    """The engine derives its answer rather than reading anything verifier-side."""
    literals = _source_string_literals(WORKFLOW_PATH.read_text(encoding="utf-8"))
    for token in ("/tests", "expected_report.json", "alt_master.json"):
        assert not any(token in literal for literal in literals), token


def test_shipped_contract_matches_the_golden_copy():
    """The output contract in the environment is unmodified.

    Field lists, container shapes and sort orders are golden metadata and are read
    from the verifier's own image; this proves the agent's copy still agrees with
    it, so the contract cannot be trimmed to weaken a schema check.
    """
    shipped = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    assert shipped == json.loads(GOLDEN_CONTRACT_PATH.read_text(encoding="utf-8"))


def test_a_registered_pair_below_the_threshold_is_not_queued_as_do_not_merge():
    """The register bites only where a pair would otherwise have linked.

    The same registered pair is run under three floors. Scoring below the match
    threshold it is never a link, so it is queued as below_threshold where it
    reaches the review floor and not queued at all beneath it -- never as
    do_not_merge, which the literal reading of the rule would have produced.
    """
    pair = [_rec("REC-000001", "carverov", given="alpha", city="arden",
                 street="12 oak street", postal_code="A11", born_on="1980-01-01"),
            _rec("REC-000002", "carverov", given="albert", city="belmont",
                 street="99 willow street", postal_code="H42", born_on="1991-07-04")]
    register = [{"left": "REC-000001", "right": "REC-000002"}]

    # measure the score this pair actually reaches rather than assuming one
    _, _, _, measured = _probe(pair, do_not_merge=register, policy={"default": {
        "match_threshold": 999, "review_floor": 0,
        "block_prefix_len": 4, "max_cluster_size": 12}})
    assert len(measured) == 1, measured
    score = measured[0]["score"]
    assert 0 < score < 999, score

    # below the threshold but at or above the floor: an ordinary sub-threshold pair
    _, summary, _, reviews = _probe(pair, do_not_merge=register, policy={"default": {
        "match_threshold": score + 1, "review_floor": score,
        "block_prefix_len": 4, "max_cluster_size": 12}})
    assert summary["link_count"] == 0
    assert summary["do_not_merge_block_count"] == 0
    assert [r["reason"] for r in reviews] == ["below_threshold"]

    # below the review floor as well: not queued at all
    _, summary, _, reviews = _probe(pair, do_not_merge=register, policy={"default": {
        "match_threshold": score + 2, "review_floor": score + 1,
        "block_prefix_len": 4, "max_cluster_size": 12}})
    assert summary["do_not_merge_block_count"] == 0
    assert reviews == []
