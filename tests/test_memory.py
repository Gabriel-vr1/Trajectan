from trajectan.memory import relate, recap_memory


def test_hypothesis_revision_preserves_evidence_and_history():
    old = {
        "key": "recent_shot_balance",
        "assessment": "home",
        "source_sequence": 100,
        "evidence_ids": ["demo:99"],
        "qualifier": "Observed event window",
    }
    prior = {
        "investigation_id": "a",
        "status": "published",
        "source_sequence": 100,
        "hypotheses": [old],
        "relations": [],
    }
    new = old | {
        "assessment": "away",
        "source_sequence": 150,
        "evidence_ids": ["demo:149"],
    }
    links = relate([new], [prior])
    assert links[0]["type"] == "contradicts"
    assert links[0]["previous_sequence"] == 100 and links[0]["evidence"] == ["demo:149"]
    current = {
        "investigation_id": "b",
        "status": "published",
        "source_sequence": 150,
        "hypotheses": [new],
        "relations": links,
    }
    assert recap_memory([prior, current], 120) == {
        "investigation_refs": ["a"],
        "revisions": [],
    }
    recap = recap_memory([prior, current], 150)
    assert recap["revisions"][0]["previous_assessment"] == "home"
    assert old["assessment"] == "home"
    assert not recap_memory([current | {"status": "rejected"}], 150)["revisions"]
    assert relate([old], [prior])[0]["type"] == "supports"
