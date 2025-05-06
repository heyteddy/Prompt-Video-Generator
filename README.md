### 워크플로우
1. 사용자 입력 인터페이스
    * 사용자가 자연어 콘셉트(예: “귀여운 강아지가 뛰노는 밝은 영상”)를 Streamlit st.text_input 위젯에 입력
    * “프롬프트 생성” 버튼을 클릭

2. 프롬프트 자동 생성
    * generate_prompt(concept) 함수 호출
    * 내부에 정의된 템플릿(길이·해상도·스타일 등 옵션 포함)을 적용하여 “Create a 10-second video of '…'…” 형태의 초기 프롬프트 문자열 생성
    * 생성된 프롬프트를 Session State 에 저장하고 st.text_area 에 띄워 줌

3. 프롬프트 편집 및 Diff 계산
    * 사용자가 st.text_area 에서 프롬프트를 직접 수정
    * “Diff 저장 & 영상 생성” 버튼 클릭 시
      * compute_diff_json(orig, edited) 호출
      * difflib.SequenceMatcher 로 원본·수정본 간 변경 블록(opcodes)을 계산
      * JSON 직렬화하여 prompt_history.jsonl 에 한 줄씩 append

4. 프롬프트 이력 저장 및 추천(옵션)
    * 로그인 후 과거 prompt_history.jsonl 에 기록된 콘셉트와 수정 이력을 불러와(load_history)
    * 현재 입력된 콘셉트와의 유사도를 SequenceMatcher.ratio() 로 비교
    * 일정 기준(0.6 이상) 넘는 과거 레코드가 있으면 “이 프롬프트 사용” 버튼으로 추천

5. 영상 생성 호출 (Placeholder)
    * 실제 API 호출 대신, generate_video(prompt) 에서 로컬에 미리 준비된 짧은 MP4 파일 경로를 반환
<pre>
return "C:\Prompt Video Generator\SampleVideo_1280x720_1mb.mp4"
</pre>

6. 결과 확인 인터페이스
    * st.expander("결과 확인") 컨테이너 안에
      * 최종 프롬프트 (st.code)
      * Diff 기록 (st.json)
      * 생성된(placeholder) 영상 (st.video)를 한눈에 보여 줌

### 주요 기술 스택
* Frontend: Streamlit
* Diff 로직: Python, difflib
* 영상 생성: Placeholder(st.video + 로컬 MP4) 또는 향후 RunwayML/Pika API 연동 가능
* 이력 관리: JSONL 파일(prompt_history.jsonl)
* 환경 변수 관리: python-dotenv (.env 사용)

### 실행 예시
![실행 예시 1](https://github.com/user-attachments/assets/cb065bfe-a53e-4a1d-8278-3cfaf517733d)
![실행 예시 2](https://github.com/user-attachments/assets/74636804-8afc-4f64-8a3e-691082d92031)
![실행 예시 3](https://github.com/user-attachments/assets/4c76fdb0-d059-41dc-91c9-4806b5fbbe10)
![실행 예시 4](https://github.com/user-attachments/assets/cff0bdb3-ea58-47a8-895e-0cbd68169340)
![실행 예시 5](https://github.com/user-attachments/assets/34356b02-1928-4852-a7db-4de91c833a00)
![실행 예시 6](https://github.com/user-attachments/assets/8501d4ea-83a1-4545-89a8-d584267f2776)
