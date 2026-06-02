"""Unit tests for scripts/resolve_auditors.py — auditor name -> markdown link."""
import json

import pytest

from scripts import resolve_auditors


MAPPING = {
    "Dacian": {"link": "https://x.com/DevDacian"},
    "Alexzoid": {"link": "https://x.com/alexzoid", "suffix": "Formal Verification"},
    "PeterSR": {"link": "https://x.com/peter"},
    "0x539": {"link": "https://x.com/1337web3"},
    "ChainDefenders": {
        "link": "https://x.com/DefendersAudits",
        "members": ["0x539", "PeterSR"],
    },
}


class TestResolveName:
    def test_simple_link(self):
        assert resolve_auditors._resolve_name("Dacian", MAPPING) == "[Dacian](https://x.com/DevDacian)"

    def test_suffix_appended(self):
        assert (
            resolve_auditors._resolve_name("Alexzoid", MAPPING)
            == "[Alexzoid](https://x.com/alexzoid) (Formal Verification)"
        )

    def test_members_expanded(self):
        assert resolve_auditors._resolve_name("ChainDefenders", MAPPING) == (
            "[ChainDefenders](https://x.com/DefendersAudits) "
            "([0x539](https://x.com/1337web3), [PeterSR](https://x.com/peter))"
        )

    def test_unknown_name_exits(self):
        with pytest.raises(SystemExit):
            resolve_auditors._resolve_name("Nobody", MAPPING)

    def test_unknown_member_exits(self):
        bad = {"Team": {"link": "https://x.com/team", "members": ["Ghost"]}}
        with pytest.raises(SystemExit):
            resolve_auditors._resolve_name("Team", bad)


class TestReadNames:
    def test_reads_and_strips_blank_lines(self, tmp_path):
        f = tmp_path / "leads.md"
        f.write_text("Dacian\n\n  Alexzoid  \n\n")
        assert resolve_auditors._read_names(str(f)) == ["Dacian", "Alexzoid"]

    def test_missing_file_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            resolve_auditors._read_names(str(tmp_path / "nope.md"))


class TestLoadAuditorMapping:
    def test_loads_valid_mapping(self, tmp_path, monkeypatch):
        f = tmp_path / "auditors.json"
        f.write_text(json.dumps(MAPPING))
        monkeypatch.setattr(resolve_auditors, "AUDITORS_JSON", str(f))
        assert resolve_auditors._load_auditor_mapping() == MAPPING

    def test_entry_missing_link_exits(self, tmp_path, monkeypatch):
        f = tmp_path / "auditors.json"
        f.write_text(json.dumps({"Bad": {"suffix": "x"}}))
        monkeypatch.setattr(resolve_auditors, "AUDITORS_JSON", str(f))
        with pytest.raises(SystemExit):
            resolve_auditors._load_auditor_mapping()

    def test_invalid_json_exits(self, tmp_path, monkeypatch):
        f = tmp_path / "auditors.json"
        f.write_text("{ not valid json ")
        monkeypatch.setattr(resolve_auditors, "AUDITORS_JSON", str(f))
        with pytest.raises(SystemExit):
            resolve_auditors._load_auditor_mapping()


class TestResolveFile:
    def test_writes_resolved_links(self, tmp_path):
        src = tmp_path / "leads.md"
        src.write_text("Dacian\nAlexzoid\n")
        out = tmp_path / "out.md"
        resolve_auditors._resolve_file(str(src), str(out), MAPPING)
        written = out.read_text()
        assert "[Dacian](https://x.com/DevDacian)" in written
        assert "[Alexzoid](https://x.com/alexzoid) (Formal Verification)" in written
