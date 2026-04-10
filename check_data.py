import json
from pathlib import Path

DATA_DIR = Path("data")

WORLD_KEYS = {
    "apocalypse",
    "dark_fantasy",
    "fantasy",
    "comedy_fantasy",
    "cyberpunk",
    "murim",
}

ROLE_KEYS = {
    "frontliner",
    "shooter",
    "caster",
    "supporter",
    "scout",
    "technician",
    "negotiator",
    "commander",
}

TAG_KEYS = {
    "growth",
    "survival",
    "inquiry",
    "strategy",
    "support",
    "operation",
    "wanderer",
    "comeback",
    "contract",
    "record",
}

BIG5_KEYS = {
    "extraversion",
    "agreeableness",
    "conscientiousness",
    "neuroticism",
    "openness",
}


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_questions():
    data = load_json(DATA_DIR / "questions.json")

    assert "meta" in data, "questions.json: meta 키가 없음"
    assert "questions" in data, "questions.json: questions 키가 없음"

    questions = data["questions"]
    assert isinstance(questions, list), "questions.json: questions는 리스트여야 함"
    assert len(questions) == 60, f"questions.json: 문항 수가 60이 아님 ({len(questions)})"

    ids = set()

    for q in questions:
        assert "id" in q, "문항에 id 없음"
        assert "section" in q, f"문항 {q.get('id')}: section 없음"
        assert "question" in q, f"문항 {q.get('id')}: question 없음"
        assert "options" in q, f"문항 {q.get('id')}: options 없음"

        qid = q["id"]
        assert qid not in ids, f"문항 id 중복: {qid}"
        ids.add(qid)

        assert 1 <= q["section"] <= 6, f"문항 {qid}: section 범위 이상"
        assert isinstance(q["options"], list), f"문항 {qid}: options는 리스트여야 함"
        assert len(q["options"]) == 4, f"문항 {qid}: 선택지가 4개가 아님"

        option_ids = set()
        for opt in q["options"]:
            assert "id" in opt, f"문항 {qid}: 선택지 id 없음"
            assert "text" in opt, f"문항 {qid}: 선택지 text 없음"
            assert "scores" in opt, f"문항 {qid}: 선택지 scores 없음"

            oid = opt["id"]
            assert oid not in option_ids, f"문항 {qid}: 선택지 id 중복 {oid}"
            option_ids.add(oid)

            scores = opt["scores"]
            for category in ["world", "role", "tag", "big5"]:
                assert category in scores, f"문항 {qid} 선택지 {oid}: scores[{category}] 없음"
                assert isinstance(scores[category], dict), f"문항 {qid} 선택지 {oid}: {category}는 dict여야 함"

            for key in scores["world"].keys():
                assert key in WORLD_KEYS, f"문항 {qid} 선택지 {oid}: 잘못된 world 키 {key}"

            for key in scores["role"].keys():
                assert key in ROLE_KEYS, f"문항 {qid} 선택지 {oid}: 잘못된 role 키 {key}"

            for key in scores["tag"].keys():
                assert key in TAG_KEYS, f"문항 {qid} 선택지 {oid}: 잘못된 tag 키 {key}"

            for key in scores["big5"].keys():
                assert key in BIG5_KEYS, f"문항 {qid} 선택지 {oid}: 잘못된 big5 키 {key}"


def check_worlds():
    data = load_json(DATA_DIR / "worlds.json")
    assert set(data.keys()) == WORLD_KEYS, "worlds.json: 세계관 키 불일치"

    for key, value in data.items():
        assert "label" in value, f"worlds.json {key}: label 없음"
        assert "summary" in value, f"worlds.json {key}: summary 없음"
        assert "description" in value, f"worlds.json {key}: description 없음"


def check_role_titles():
    data = load_json(DATA_DIR / "role_titles.json")

    assert "role_labels" in data, "role_titles.json: role_labels 없음"
    assert "world_role_titles" in data, "role_titles.json: world_role_titles 없음"
    assert "tag_labels" in data, "role_titles.json: tag_labels 없음"

    assert set(data["role_labels"].keys()) == ROLE_KEYS, "role_titles.json: role_labels 키 불일치"
    assert set(data["tag_labels"].keys()) == TAG_KEYS, "role_titles.json: tag_labels 키 불일치"
    assert set(data["world_role_titles"].keys()) == WORLD_KEYS, "role_titles.json: world_role_titles 세계관 키 불일치"

    for world_key, mapping in data["world_role_titles"].items():
        assert set(mapping.keys()) == ROLE_KEYS, f"role_titles.json: {world_key} 역할군 키 불일치"


def check_result_texts():
    data = load_json(DATA_DIR / "result_texts.json")

    required_keys = {"world_intro", "role_core", "tag_flavor", "ending", "advice", "overrides"}
    assert required_keys.issubset(data.keys()), "result_texts.json: 필수 키 누락"

    assert set(data["world_intro"].keys()) == WORLD_KEYS, "result_texts.json: world_intro 키 불일치"
    assert set(data["role_core"].keys()) == ROLE_KEYS, "result_texts.json: role_core 키 불일치"
    assert set(data["tag_flavor"].keys()) == TAG_KEYS, "result_texts.json: tag_flavor 키 불일치"
    assert isinstance(data["ending"], list) and len(data["ending"]) > 0, "result_texts.json: ending이 비었음"
    assert set(data["advice"].keys()) == ROLE_KEYS, "result_texts.json: advice 역할군 키 불일치"

    for role_key, advice_block in data["advice"].items():
        assert "base" in advice_block, f"result_texts.json advice[{role_key}]: base 없음"
        assert isinstance(advice_block["base"], list), f"result_texts.json advice[{role_key}]: base는 list여야 함"

    for override_key in data["overrides"].keys():
        parts = override_key.split("|")
        assert len(parts) == 4, f"override 키 형식 오류: {override_key}"
        world, role, tag1, tag2 = parts
        assert world in WORLD_KEYS, f"override world 오류: {override_key}"
        assert role in ROLE_KEYS, f"override role 오류: {override_key}"
        assert tag1 in TAG_KEYS, f"override tag1 오류: {override_key}"
        assert tag2 in TAG_KEYS, f"override tag2 오류: {override_key}"


def check_users():
    data = load_json(DATA_DIR / "users.json")
    assert isinstance(data, list), "users.json: 리스트여야 함"
    for i, user in enumerate(data, start=1):
        assert "username" in user, f"users.json {i}: username 없음"
        assert "password" in user, f"users.json {i}: password 없음"
        assert "name" in user, f"users.json {i}: name 없음"


def main():
    check_questions()
    check_worlds()
    check_role_titles()
    check_result_texts()
    check_users()
    print("모든 JSON 파일 검사를 통과했습니다.")


if __name__ == "__main__":
    main()