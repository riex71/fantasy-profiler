import json
import random
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="판타지 세계 속 나의 캐릭터",
    page_icon="🗺️",
    layout="wide",
)

DATA_DIR = Path("data")

WORLD_KEYS = [
    "apocalypse",
    "dark_fantasy",
    "fantasy",
    "comedy_fantasy",
    "cyberpunk",
    "murim",
]

ROLE_KEYS = [
    "frontliner",
    "shooter",
    "caster",
    "supporter",
    "scout",
    "technician",
    "negotiator",
    "commander",
]

TAG_KEYS = [
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
]

BIG5_KEYS = [
    "extraversion",
    "agreeableness",
    "conscientiousness",
    "neuroticism",
    "openness",
]

BIG5_LABELS = {
    "extraversion": "외향성",
    "agreeableness": "친화성",
    "conscientiousness": "성실성",
    "neuroticism": "신경성",
    "openness": "개방성",
}

DEFAULT_USERS = [
    {"username": "admin", "password": "1234", "name": "윤동현"},
    {"username": "guest", "password": "1234", "name": "테스트유저"},
]


@st.cache_data
def load_questions() -> dict[str, Any]:
    with open(DATA_DIR / "questions.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_worlds() -> dict[str, Any]:
    with open(DATA_DIR / "worlds.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_role_titles() -> dict[str, Any]:
    with open(DATA_DIR / "role_titles.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_result_texts() -> dict[str, Any]:
    with open(DATA_DIR / "result_texts.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_users() -> list[dict[str, str]]:
    path = DATA_DIR / "users.json"
    if not path.exists():
        return DEFAULT_USERS
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def init_session() -> None:
    defaults = {
        "logged_in": False,
        "current_user": None,
        "page": "home",
        "answers": {},
        "current_index": 0,
        "submitted": False,
        "is_random_result": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def authenticate(username: str, password: str, users: list[dict[str, str]]) -> dict[str, str] | None:
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None


def reset_test() -> None:
    st.session_state.answers = {}
    st.session_state.current_index = 0
    st.session_state.submitted = False
    st.session_state.page = "test"
    st.session_state.is_random_result = False


def go_menu() -> None:
    st.session_state.page = "menu"
    st.session_state.current_index = 0
    st.session_state.submitted = False
    st.session_state.is_random_result = False


def logout() -> None:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = "home"
    st.session_state.answers = {}
    st.session_state.current_index = 0
    st.session_state.submitted = False
    st.session_state.is_random_result = False


def random_fill_answers(questions: list[dict[str, Any]]) -> None:
    random_answers: dict[str, str] = {}
    for question in questions:
        selected = random.choice(question["options"])
        random_answers[str(question["id"])] = selected["id"]

    st.session_state.answers = random_answers
    st.session_state.current_index = 0
    st.session_state.submitted = True
    st.session_state.page = "result"
    st.session_state.is_random_result = True


def init_scores() -> dict[str, dict[str, int]]:
    return {
        "world": {key: 0 for key in WORLD_KEYS},
        "role": {key: 0 for key in ROLE_KEYS},
        "tag": {key: 0 for key in TAG_KEYS},
        "big5": {key: 0 for key in BIG5_KEYS},
    }


def apply_option_scores(total_scores: dict[str, dict[str, int]], option_scores: dict[str, dict[str, int]]) -> None:
    for category, score_map in option_scores.items():
        if category not in total_scores:
            continue
        for key, value in score_map.items():
            if key in total_scores[category]:
                total_scores[category][key] += value


def calculate_scores(questions: list[dict[str, Any]], answers: dict[str, str]) -> dict[str, dict[str, int]]:
    total_scores = init_scores()

    for question in questions:
        qid = str(question["id"])
        selected_option_id = answers.get(qid)
        if not selected_option_id:
            continue

        matched = next(
            (option for option in question["options"] if option["id"] == selected_option_id),
            None,
        )
        if matched:
            apply_option_scores(total_scores, matched["scores"])

    return total_scores


def get_top_key(score_map: dict[str, int]) -> str:
    return max(score_map.items(), key=lambda item: item[1])[0]


def get_top_n_keys(score_map: dict[str, int], n: int = 2) -> list[str]:
    sorted_items = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
    return [key for key, _ in sorted_items[:n]]


def build_immersive_prologue(
    world_key: str,
    role_key: str,
    tag_keys: list[str],
    result_texts: dict[str, Any],
) -> str:
    sorted_tags = sorted(tag_keys)
    override_key = f"{world_key}|{role_key}|{sorted_tags[0]}|{sorted_tags[1]}"

    if override_key in result_texts.get("overrides", {}):
        return result_texts["overrides"][override_key]

    world_line = random.choice(result_texts["world_intro"][world_key])
    role_line = random.choice(result_texts["role_core"][role_key])
    tag_line_1 = random.choice(result_texts["tag_flavor"][tag_keys[0]])
    tag_line_2 = random.choice(result_texts["tag_flavor"][tag_keys[1]])
    ending_line = random.choice(result_texts["ending"])

    return " ".join([world_line, role_line, tag_line_1, tag_line_2, ending_line])


def build_immersive_advice(
    role_key: str,
    tag_keys: list[str],
    result_texts: dict[str, Any],
) -> str:
    advice_block = result_texts["advice"][role_key]
    base_line = random.choice(advice_block["base"])

    extra_candidates: list[str] = []
    for tag in tag_keys:
        if tag in advice_block:
            extra_candidates.extend(advice_block[tag])

    if extra_candidates:
        extra_line = random.choice(extra_candidates)
        return f"{base_line} {extra_line}"

    return base_line


def build_result_text(
    user_name: str,
    world_key: str,
    role_key: str,
    world_title: str,
    base_role_label: str,
    tag_keys: list[str],
    worlds: dict[str, Any],
    role_data: dict[str, Any],
    total_scores: dict[str, dict[str, int]],
    prologue: str,
    advice: str,
) -> str:
    tag_labels = [role_data["tag_labels"][tag] for tag in tag_keys]

    lines = [
        f"{user_name}님의 캐릭터 리포트",
        "",
        "[결과 요약]",
        f"- 세계관: {worlds[world_key]['label']}",
        f"- 역할군: {base_role_label}",
        f"- 이 세계에서의 이름: {world_title}",
        f"- 태그: {tag_labels[0]} / {tag_labels[1]}",
        "",
        "[프롤로그]",
        prologue,
        "",
        "[진행 조언]",
        advice,
        "",
        "[내부 점수 참고]",
        f"- 세계관 점수: {total_scores['world']}",
        f"- 역할군 점수: {total_scores['role']}",
        f"- 태그 점수: {total_scores['tag']}",
        f"- 빅파이브 보정 점수: {total_scores['big5']}",
    ]
    return "\n".join(lines)


def make_plotly_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str):
    fig = px.bar(df, x=x_col, y=y_col, title=title, text=y_col)
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
    )
    return fig


def render_home() -> None:
    st.title("판타지 세계 속 나의 캐릭터")
    st.caption("성향 기반 이세계 캐릭터 프로파일러")

    st.markdown("### 제출자 정보")
    st.write("학번: 2022204055")
    st.write("이름: 윤동현")

    st.markdown("---")
    st.markdown(
        """
        이 앱은 다양한 상황형 질문을 통해,  
        당신이 판타지 세계에서 어떤 역할과 결을 가진 인물인지 리포트 형식으로 보여줍니다.

        정답은 없습니다. 가장 끌리는 선택지를 따라가며,  
        당신만의 캐릭터 프로필을 확인해 보세요.
        """
    )

    st.info("로그인 후 직접 검사를 진행하거나, 랜덤 선택으로 빠르게 결과를 확인할 수 있습니다.")

    st.markdown("### 로그인")
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

    if submitted:
        users = load_users()
        user = authenticate(username, password, users)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.session_state.page = "menu"
            st.success("로그인에 성공했습니다.")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")


def render_sidebar() -> None:
    user = st.session_state.current_user
    with st.sidebar:
        st.markdown("## 사용자 정보")
        st.write(f"이름: {user['name']}")
        st.write(f"아이디: {user['username']}")
        st.markdown("---")

        if st.button("메뉴로 돌아가기"):
            go_menu()
            st.rerun()

        if st.button("검사 다시 시작"):
            reset_test()
            st.rerun()

        if st.button("로그아웃"):
            logout()
            st.rerun()


def render_menu() -> None:
    question_data = load_questions()
    questions = question_data["questions"]

    st.title("판타지 세계 속 나의 캐릭터")
    st.caption("원하는 방식으로 캐릭터 리포트를 확인해 보세요.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 직접 검사하기")
        st.write("60문항을 직접 선택하며 당신의 캐릭터를 찾아갑니다.")
        if st.button("검사 시작하기", use_container_width=True):
            reset_test()
            st.rerun()

    with col2:
        st.markdown("### 빠르게 결과 보기")
        st.write("선택지를 랜덤으로 자동 응답해 샘플 결과를 즉시 확인합니다.")
        if st.button("랜덤 선택으로 결과 보기", use_container_width=True):
            random_fill_answers(questions)
            st.rerun()

    st.markdown("---")
    st.markdown("### 추가 보기")
    if st.button("캐릭터 아카이브", use_container_width=True):
        st.session_state.page = "archive"
        st.rerun()


def render_test() -> None:
    question_data = load_questions()
    questions = question_data["questions"]
    sections = {section["id"]: section for section in question_data["meta"]["sections"]}

    total = len(questions)
    idx = st.session_state.current_index
    question = questions[idx]
    section_id = question["section"]

    current_section_questions = [q for q in questions if q["section"] == section_id]
    section_question_ids = [str(q["id"]) for q in current_section_questions]
    section_answered = sum(1 for qid in section_question_ids if qid in st.session_state.answers)

    st.title("캐릭터 판별 퀴즈")
    st.caption("가장 끌리는 선택지를 하나 골라 주세요.")

    progress = (idx + 1) / total
    st.progress(progress)

    st.markdown(f"**섹션 {section_id} / 6**")
    st.markdown(f"**현재 문항 {idx + 1} / {total}**")

    st.info(
        f"**{sections[section_id]['title']}**\n\n"
        f"{sections[section_id]['description']}\n\n"
        f"현재 섹션 응답 수: {section_answered} / {len(current_section_questions)}"
    )

    st.markdown("---")
    st.markdown(f"### {question['question']}")

    option_labels = {option["id"]: option["text"] for option in question["options"]}
    current_value = st.session_state.answers.get(str(question["id"]))
    option_ids = list(option_labels.keys())
    default_index = option_ids.index(current_value) if current_value in option_ids else 0

    selected_option = st.radio(
        "선택지",
        options=option_ids,
        index=default_index,
        format_func=lambda x: f"{x}. {option_labels[x]}",
        key=f"question_{question['id']}",
    )

    st.session_state.answers[str(question["id"])] = selected_option

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("이전", disabled=(idx == 0)):
            st.session_state.current_index -= 1
            st.rerun()

    with col2:
        if idx < total - 1:
            if st.button("다음"):
                st.session_state.current_index += 1
                st.rerun()
        else:
            if st.button("결과 보기"):
                if len(st.session_state.answers) == total:
                    st.session_state.submitted = True
                    st.session_state.page = "result"
                    st.rerun()
                else:
                    st.warning("모든 문항에 응답해야 결과를 볼 수 있습니다.")

    with col3:
        st.write(f"전체 응답 수: {len(st.session_state.answers)}/{total}")


def render_result() -> None:
    question_data = load_questions()
    questions = question_data["questions"]
    worlds = load_worlds()
    role_data = load_role_titles()
    result_texts = load_result_texts()
    user = st.session_state.current_user

    total_scores = calculate_scores(questions, st.session_state.answers)

    world_key = get_top_key(total_scores["world"])
    role_key = get_top_key(total_scores["role"])
    tag_keys = get_top_n_keys(total_scores["tag"], 2)

    world_label = worlds[world_key]["label"]
    base_role_label = role_data["role_labels"][role_key]
    world_role_title = role_data["world_role_titles"][world_key][role_key]
    tag_labels = [role_data["tag_labels"][tag] for tag in tag_keys]

    prologue = build_immersive_prologue(
        world_key=world_key,
        role_key=role_key,
        tag_keys=tag_keys,
        result_texts=result_texts,
    )
    advice = build_immersive_advice(
        role_key=role_key,
        tag_keys=tag_keys,
        result_texts=result_texts,
    )

    result_text = build_result_text(
        user_name=user["name"],
        world_key=world_key,
        role_key=role_key,
        world_title=world_role_title,
        base_role_label=base_role_label,
        tag_keys=tag_keys,
        worlds=worlds,
        role_data=role_data,
        total_scores=total_scores,
        prologue=prologue,
        advice=advice,
    )

    st.title(f"{user['name']}님의 캐릭터 리포트")
    st.caption("당신의 선택은 하나의 세계관과 역할, 그리고 두 개의 태그로 정리됩니다.")

    if st.session_state.get("is_random_result", False):
        st.info("이 결과는 랜덤 선택지를 자동 응답해 생성한 샘플 결과입니다.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("당신의 세계관", world_label)
        st.metric("당신의 역할군", base_role_label)
    with col2:
        st.metric("이 세계에서의 이름", world_role_title)
        st.metric("당신을 이루는 태그", f"{tag_labels[0]} / {tag_labels[1]}")

    st.markdown("## 세계관")
    st.write(worlds[world_key]["summary"])
    st.write(worlds[world_key]["description"])

    st.markdown("## 프롤로그")
    st.info(prologue)

    st.markdown("## 진행 조언")
    st.write(advice)

    st.markdown("---")
    st.markdown("## 결과 시각화")

    world_df = pd.DataFrame({
        "세계관": [worlds[key]["label"] for key in WORLD_KEYS],
        "점수": [total_scores["world"][key] for key in WORLD_KEYS],
    }).sort_values("점수", ascending=False)

    role_df = pd.DataFrame({
        "역할군": [role_data["role_labels"][key] for key in ROLE_KEYS],
        "점수": [total_scores["role"][key] for key in ROLE_KEYS],
    }).sort_values("점수", ascending=False)

    tag_df = pd.DataFrame({
        "태그": [role_data["tag_labels"][key] for key in TAG_KEYS],
        "점수": [total_scores["tag"][key] for key in TAG_KEYS],
    }).sort_values("점수", ascending=False).head(6)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(make_plotly_bar(world_df, "세계관", "점수", "세계관 점수"), use_container_width=True)
    with col2:
        st.plotly_chart(make_plotly_bar(role_df, "역할군", "점수", "역할군 점수"), use_container_width=True)

    st.plotly_chart(make_plotly_bar(tag_df, "태그", "점수", "상위 태그 점수"), use_container_width=True)

    with st.expander("내부 점수 자세히 보기"):
        st.markdown("### 태그 점수 전체")
        full_tag_df = pd.DataFrame({
            "태그": [role_data["tag_labels"][key] for key in TAG_KEYS],
            "점수": [total_scores["tag"][key] for key in TAG_KEYS],
        }).sort_values("점수", ascending=False)
        st.dataframe(full_tag_df, use_container_width=True, hide_index=True)

        st.markdown("### 빅파이브 보정 점수")
        big5_df = pd.DataFrame({
            "성향": [BIG5_LABELS[key] for key in BIG5_KEYS],
            "점수": [total_scores["big5"][key] for key in BIG5_KEYS],
        }).sort_values("점수", ascending=False)
        st.dataframe(big5_df, use_container_width=True, hide_index=True)

    st.markdown("## 결과 저장")
    st.download_button(
        label="결과 텍스트 다운로드",
        data=result_text,
        file_name="fantasy_character_report.txt",
        mime="text/plain",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("다시 선택하기"):
            reset_test()
            st.rerun()
    with col2:
        if st.button("메뉴로 돌아가기"):
            go_menu()
            st.rerun()
    with col3:
        if st.button("캐릭터 아카이브"):
            st.session_state.page = "archive"
            st.rerun()


def render_archive() -> None:
    worlds = load_worlds()
    role_data = load_role_titles()
    result_texts = load_result_texts()

    st.title("캐릭터 아카이브")
    st.caption("세계관, 역할군, 태그를 직접 고르고 결과를 미리 확인할 수 있습니다.")
    st.markdown("---")

    world_options = {worlds[key]["label"]: key for key in WORLD_KEYS}
    role_options = {role_data["role_labels"][key]: key for key in ROLE_KEYS}
    tag_options = {role_data["tag_labels"][key]: key for key in TAG_KEYS}

    col1, col2 = st.columns(2)
    with col1:
        selected_world_label = st.selectbox("세계관 선택", list(world_options.keys()))
        selected_role_label = st.selectbox("역할군 선택", list(role_options.keys()))
    with col2:
        selected_tag_1_label = st.selectbox("태그 1 선택", list(tag_options.keys()))
        remaining_tag_labels = [label for label in tag_options.keys() if label != selected_tag_1_label]
        selected_tag_2_label = st.selectbox("태그 2 선택", remaining_tag_labels)

    world_key = world_options[selected_world_label]
    role_key = role_options[selected_role_label]
    tag_keys = sorted([
        tag_options[selected_tag_1_label],
        tag_options[selected_tag_2_label],
    ])

    world_role_title = role_data["world_role_titles"][world_key][role_key]

    prologue = build_immersive_prologue(
        world_key=world_key,
        role_key=role_key,
        tag_keys=tag_keys,
        result_texts=result_texts,
    )
    advice = build_immersive_advice(
        role_key=role_key,
        tag_keys=tag_keys,
        result_texts=result_texts,
    )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("당신의 세계관", worlds[world_key]["label"])
        st.metric("당신의 역할군", role_data["role_labels"][role_key])
    with col2:
        st.metric("이 세계에서의 이름", world_role_title)
        st.metric("당신을 이루는 태그", f"{selected_tag_1_label} / {selected_tag_2_label}")

    st.markdown("## 세계관")
    st.write(worlds[world_key]["summary"])
    st.write(worlds[world_key]["description"])

    st.markdown("## 프롤로그")
    st.info(prologue)

    st.markdown("## 진행 조언")
    st.write(advice)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("메뉴로 돌아가기", key="archive_menu"):
            st.session_state.page = "menu"
            st.rerun()
    with col2:
        if st.button("로그아웃", key="archive_logout"):
            logout()
            st.rerun()


def main() -> None:
    init_session()

    try:
        load_questions()
        load_worlds()
        load_role_titles()
        load_result_texts()
        load_users()
    except FileNotFoundError as e:
        st.error(f"필수 데이터 파일을 찾을 수 없습니다: {e}")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"JSON 파일 형식이 올바르지 않습니다: {e}")
        st.stop()

    if not st.session_state.logged_in:
        render_home()
    else:
        render_sidebar()
        if st.session_state.page == "menu":
            render_menu()
        elif st.session_state.page == "test":
            render_test()
        elif st.session_state.page == "result":
            render_result()
        elif st.session_state.page == "archive":
            render_archive()
        else:
            render_menu()


if __name__ == "__main__":
    main()