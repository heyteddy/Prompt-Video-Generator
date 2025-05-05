import streamlit as st
import difflib # 문자열 간 차이를 계산
import json
import os
import time
from dotenv import load_dotenv
from datetime import datetime
from difflib import SequenceMatcher
from runwayml import RunwayML, BadRequestError
load_dotenv()

RUNWAY_KEY = os.getenv("RUNWAYML_API_SECRET")
if not RUNWAY_KEY:
    st.error("RUNWAYML_API_SECRET 환경 변수가 설정되지 않았습니다.")
    st.stop()

client = RunwayML(api_key=RUNWAY_KEY)

# 이력 로드
def load_history(path="prompt_history.jsonl"):
    """JSONL 형식의 프롬프트 이력 파일을 불러와 리스트로 반환"""
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                records.append(json.loads(line))
    except FileNotFoundError:
        pass
    return records

# 유사도 계산
def get_best_match(concept: str, history: list, threshold=0.6):
    """
    history 내 각 레코드['concept']와 비교하여
    가장 높은 유사도를 가진 레코드를 반환.
    유사도가 threshold 미만이면 None 리턴.`
    """
    best = None
    best_ratio = threshold
    for rec in history:
        ratio = SequenceMatcher(None, concept, rec["concept"]).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best = rec
    return best, best_ratio

# 자동 프롬프트 생성
def generate_prompt(concept: str) -> str:
    """간단한 템플릿 기반 초기 프롬프트 생성 함수"""
    return (
        f"Create a 10-second video of '{concept}', "
        "1080p resolution, 30fps, cinematic style, "
        "with vibrant colors and smooth motion." 
    )


# Diff 계산 및 JSON 직렬화 함수
def compute_diff_json(orig: str, edited: str) -> str:
    """원본(orig)과 수정본(edited)의 차이(opcode)를 JSON 포맷의 문자열로 만들어 돌려줌"""

    sm = difflib.SequenceMatcher(None, orig, edited)
    diff_records = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        diff_records.append({
            "op": tag,
            "orig_range": [i1, i2],
            "edited_range": [j1, j2],
            "orig_text": orig[i1:i2],
            "edited_text": edited[j1:j2],
        })

    return json.dumps(diff_records, ensure_ascii=False, indent=2)


# 영상 생성 호출
# 로컬 경로에 위치한 placeholder 비디오 파일 경로 반환
def generate_video(prompt: str) -> str:
    return "C:\Prompt Video Generator\SampleVideo_1280x720_2mb.mp4"

# Streamlit UI
def main():
    st.title("프롬프트 최적화 기반 영상 생성 에이전트 시스템")

    # 1. 사용자 콘셉트 입력
    user_concept = st.text_input(
        "원하는 영상 콘셉트/느낌을 입력하세요.",
        value=st.session_state.get("last_concept", "")
    ).strip()

    # 이력 기반 추천 프롬프트
    if user_concept:
        history = load_history()
        best_rec, best_ratio = get_best_match(user_concept, history)
        if best_rec:
            st.info(f"유사 이전 요청 감지 (유사도: {best_ratio:.2f})")
            st.write("> 이전에 최적화된 프롬프트:")
            st.code(best_rec["edited_prompt"], language="text")
            if st.button("이 프롬프트 사용", key="use_reco"):
                # 추천된 프롬프트를 세션에 바로 세팅
                st.session_state["orig_prompt"]   = best_rec["original_prompt"]
                st.session_state["edited_prompt"] = best_rec["edited_prompt"]
                st.session_state["last_concept"]  = user_concept

    # 신규 프롬프트 생성
    if st.button("프롬프트 생성"):
        # 자동 생성
        orig_prompt = generate_prompt(user_concept.strip())
        # 세션에 저장
        st.session_state["orig_prompt"] = orig_prompt
        st.session_state["last_concept"] = user_concept
        st.session_state["edited_prompt"] = orig_prompt

    # 2. 편집 가능한 텍스트 에어리어
    if "orig_prompt" in st.session_state:
        edited = st.text_area(
            "프롬프트를 편집하세요.",
            value=st.session_state["edited_prompt"],
            height=150
        )
        st.session_state["edited_prompt"] = edited

        # 3. 저장 및 Diff 생성
        if st.button("Diff 저장", key="save_gen"):
            orig = st.session_state["orig_prompt"]
            edited = st.session_state["edited_prompt"]

            # Diff 계산
            diff_json = compute_diff_json(orig, edited)
            diff_data = json.loads(diff_json)

            # 로그 레코드 준비
            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "concept": user_concept,
                "original_prompt": orig,
                "edited_prompt": edited,
                "diff": diff_data
            }

            with open("prompt_history.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            # 결과 표시
            st.success("프롬프트와 Diff가 저장되었습니다.")
            with st.expander("결과 확인", expanded=True):
                st.subheader("최종 프롬프트")
                st.code(edited)
                st.subheader("Diff 기록")
                st.json(diff_data)
                st.subheader("생성된 영상")
                with st.spinner("영상 생성 중… 잠시만 기다려주세요."):
                    video_url = generate_video(edited)
                st.video(video_url)
                st.caption("결과입니다.")


if __name__ == "__main__":
    main()