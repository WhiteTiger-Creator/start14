"""Verifier tests for this task.

Every test below corresponds to something instruction.md states is graded.
Shared machinery lives in harness.py.
"""

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


def test_all_three_review_reasons_occur(primary_outputs):
    """The graded master exercises every documented review reason."""
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
    shutil.rmtree(default_out, ignore_errors=True)
    default_out.mkdir(parents=True, exist_ok=True)
    os.chmod(default_out, 0o777)
    result = _run_agent([binary], cwd=_candidate_dir())
    assert result.returncode == 0, result.stderr
    assert sorted(q.name for q in default_out.iterdir()) == [
        "golden_records.json", "review_queue.jsonl", "summary.json"]
    _, summary, golden, reviews = primary_outputs
    assert _load_json(default_out / "summary.json") == summary
    assert _digest(_load_json(default_out / "golden_records.json")) == _digest(golden)
    assert _digest(_load_jsonl(default_out / "review_queue.jsonl")) == _digest(reviews)


def test_output_artifacts_use_the_contracted_serialisation(primary_outputs):
    """The three files are written exactly as the contract spells them out.

    Byte-for-byte: two-space indent and a trailing newline for the two JSON
    documents, one compact object per line for the queue.
    """
    out_dir, summary, golden, reviews = primary_outputs
    assert (out_dir / "summary.json").read_text(encoding="utf-8") == \
        json.dumps(summary, indent=2) + "\n"
    assert (out_dir / "golden_records.json").read_text(encoding="utf-8") == \
        json.dumps(golden, indent=2) + "\n"
    raw = (out_dir / "review_queue.jsonl").read_text(encoding="utf-8")
    assert raw.endswith("\n") and "\n\n" not in raw
    lines = raw.splitlines()
    assert len(lines) == len(reviews)
    for line, row in zip(lines, reviews):
        assert line == json.dumps(row, separators=(",", ":"))


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
    result = _run_agent([binary, "--output-dir", str(out_dir)], cwd=work)
    assert result.returncode == 0, result.stderr
    assert sorted(q.name for q in out_dir.iterdir()) == [
        "golden_records.json", "review_queue.jsonl", "summary.json"]
    assert _load_json(out_dir / "golden_records.json") != []


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
    assert result.returncode == 0, result.stderr
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
    source = WORKFLOW_PATH.read_text(encoding="utf-8")
    for token in ("/tests", "expected_report.json", "alt_master.json"):
        assert token not in source


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
