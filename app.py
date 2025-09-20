import re
import google.generativeai as genai
import streamlit as st

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="Win Ugly 전략 분석기",
    page_icon="🥊",
    layout="centered",
)

# --- UI 스타일링 함수 ---
def apply_ui_styles():
    """앱 전체에 적용될 CSS 스타일을 정의합니다."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
            
            :root {
                --primary-color: #2BA7D1;
                --black-color: #0D1628;
                --secondary-color: #86929A;
                --divider-color: #E5E7EB;
                --background-color: #F1F2F5;
            }

            /* --- 라이트 모드 강제 --- */
            body[data-theme="dark"] {
                --background-color: #ffffff; 
                --secondary-background-color: #F1F2F5; 
                --text-color: var(--black-color);
                --primary: var(--primary-color);
            }
            body[data-theme="dark"] div[data-baseweb="select"] > div,
            body[data-theme="dark"] .stTextArea textarea {
                color: var(--black-color);
            }
            /* --- 라이트 모드 강제 끝 --- */

            .stApp {
                background-color: var(--background-color);
            }
            
            div.block-container {
                padding: 2rem 1.5rem 2.5rem 1.5rem !important;
                max-width: 720px;
                margin: 0 auto !important; 
            }
            
            header[data-testid="stHeader"] { display: none !important; }

            body, .stTextArea, .stButton>button {
                font-family: 'Noto Sans KR', sans-serif;
            }

            .icon-container {
                width: 68px; height: 68px;
                background-color: rgba(43, 167, 209, 0.1);
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                margin-bottom: 12px;
                font-size: 40px;
            }

            .title {
                font-size: 24px; font-weight: 700; color: var(--black-color);
                line-height: 36px; margin-bottom: 8px;
            }
            .subtitle {
                font-size: 14px; color: var(--secondary-color);
                line-height: 22px; margin-bottom: 32px;
            }
            
            .input-title {
                font-size: 18px; font-weight: 700; color: var(--black-color);
                margin-bottom: 12px;
            }

            .stTextArea textarea {
                background-color: #ffffff !important;
                border: 1px solid var(--divider-color) !important;
                border-radius: 12px !important;
            }
            
            div[data-testid="stFormSubmitButton"] button {
                background-color: var(--primary-color) !important;
                color: white !important;
                font-size: 16px; font-weight: 700;
                border-radius: 12px; padding: 14px 0;
                border: none !important;
                box-shadow: 0px 5px 10px rgba(43, 167, 209, 0.2);
            }

            hr {
                margin: 1.5rem 0 !important;
                background-color: var(--divider-color);
                height: 1px;
                border: none;
            }
        </style>
    """, unsafe_allow_html=True)


# --- Gemini API 키 설정 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except (FileNotFoundError, KeyError):
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다.")
    st.stop()


def get_gemini_feedback(user_strategy_input):
    """Gemini API를 호출하여 사용자의 전략에 대한 피드백을 생성합니다."""
    prompt = f"""
        당신은 'Win Ugly' 전략에 특화된 코치입니다. 'Win Ugly'는 승리를 위해 때로는 비합리적이거나 비정상적인 방법까지도 불사하는 '독한 선수'의 정신을 의미합니다.

        아래 4단계 코칭 틀과 출력 형식에 맞춰 사용자의 입력에 대해 상세하게 분석하고 피드백을 제공해 주세요.

        **4단계 'Win Ugly' 코칭 틀:**
        1.  **종합 진단:** 사용자의 전략을 전반적으로 평가하여 '독한 선수'와 '착한 선수' 중 어디에 가까운지 진단합니다.
        2.  **칭찬할 점:** 사용자의 입력 내용 중 가장 'Win Ugly' 정신에 부합하는 **핵심 문장 하나를 그대로 인용**하고, 왜 그것이 '독한(Ugly)' 생각인지 근거를 제시하여 칭찬합니다.
        3.  **보완할 점:** 사용자의 입력 내용 중 가장 개선이 필요한 '착한' 생각 **하나를 그대로 인용**하고, 그것을 어떻게 '독한(Ugly)' 전략으로 바꿀 수 있는지 구체적인 행동 지침을 제공합니다.
        4.  **'Win Ugly' 미션:** 위 분석을 바탕으로 사용자가 실행할 수 있는 가장 중요한 핵심 행동 2~3가지를 짧고 명료한 미션으로 요약합니다.

        ---
        **사용자 입력:**
        "{user_strategy_input}"
        ---

        **출력 형식 (이 형식을 반드시 지켜주세요):**
        ### 1. 종합 진단
        {{여기에 종합 진단 내용 작성}}

        ### 2. 칭찬할 점 (Ugly Points 🥊)
        > {{사용자 입력에서 인용한 칭찬할 문장}}
        {{인용한 문장에 대한 칭찬 및 분석 내용을 작성해주세요.}}

        ### 3. 보완할 점 (Nice Points 😇)
        > {{사용자 입력에서 인용한 보완할 문장}}
        {{인용한 문장에 대한 보완점 및 대안 제시 내용을 작성해주세요. 독려, 행동 지침, 승리 최면 등 여러 내용이 있다면, 읽기 쉽도록 문단 사이에 한 줄씩 띄어쓰기(줄 바꿈)를 반드시 포함해주세요.}}

        ### 4. 당신의 Win Ugly 미션
        - {{미션 1 내용}}
        - {{미션 2 내용}}
        - {{미션 3 내용}}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"피드백 생성 중 오류가 발생했습니다: {e}")
        return None

def build_report_component(feedback_text):
    """피드백 텍스트를 기반으로, 이미지 저장 기능이 포함된 완전한 HTML 컴포넌트를 생성합니다."""
    # 1. 피드백 텍스트를 HTML 콘텐츠로 파싱
    try:
        sections = re.split(r"###\s*\d\.", feedback_text)
        
        diag_html = f"<div class='card-section'><p class='section-title'>종합 진단</p><p class='section-body'>{sections[1].strip()}</p></div>"

        praise_content = sections[2].split(")", 1)[-1].strip()
        praise_quote = re.search(r">\s*(.*)", praise_content).group(1)
        praise_feedback = praise_content.split(re.search(r">\s*(.*)", praise_content).group(0))[-1].strip().replace("\n", "<br>")
        praise_html = f"<div class='card-section'><p class='section-title'>칭찬할 점 (Ugly Points)</p><p class='quoted-text good'>“{praise_quote}”</p><p class='section-body'>{praise_feedback}</p></div>"

        improve_content = sections[3].split(")", 1)[-1].strip()
        improve_quote = re.search(r">\s*(.*)", improve_content).group(1)
        improve_feedback = improve_content.split(re.search(r">\s*(.*)", improve_content).group(0))[-1].strip().replace("\n", "<br>")
        improve_html = f"<div class='card-section'><p class='section-title'>보완할 점 (Nice Points)</p><p class='quoted-text bad'>“{improve_quote}”</p><p class='section-body'>{improve_feedback}</p></div>"

        missions = sections[4].strip().split("\n- ")
        missions_html = "".join([f"<li class='mission-item'>{m.strip()}</li>" for m in missions if m.strip()])
        missions_section_html = f"<div class='card-section last'><p class='section-title'>Win Ugly 미션</p><ul class='mission-list'>{missions_html}</ul></div>"

    except (IndexError, AttributeError) as e:
        st.error(f"AI 응답을 처리하는 데 실패했습니다. 다시 시도해주세요. (오류: {e})")
        return ""

    # 2. 최종 HTML 컴포넌트 조합
    final_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
            :root {{
                --primary-color: #2BA7D1; --black-color: #0D1628;
                --secondary-color: #86929A; --divider-color: #F1F1F1;
            }}
            body {{ font-family: 'Noto Sans KR', sans-serif; }}

            #capture-card {{
                background: linear-gradient(315deg, rgba(77, 0, 200, 0.03) 0%, rgba(29, 48, 78, 0.03) 100%), #ffffff;
                border-radius: 32px; padding: 2rem;
                outline: 8px solid rgba(33, 64, 131, 0.08);
            }}
            .card-section {{
                padding-bottom: 20px; margin-bottom: 20px;
                border-bottom: 1px solid var(--divider-color);
            }}
            .card-section.last {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
            .section-title {{
                font-size: 18px; font-weight: 700; color: var(--black-color);
                margin-bottom: 16px;
            }}
            .section-body {{
                color: var(--secondary-color); font-size: 14px;
                line-height: 1.7;
            }}
            .quoted-text {{
                font-size: 15px; font-weight: 700; padding: 12px 16px;
                border-radius: 8px; margin: 12px 0 16px 0;
            }}
            .quoted-text.good {{ background-color: rgba(43, 167, 209, 0.1); color: #1e6b85; }}
            .quoted-text.bad {{ background-color: rgba(239, 68, 68, 0.1); color: #9c2a2a; }}

            .mission-list {{ list-style: none; padding: 0; }}
            .mission-item {{
                font-size: 15px; color: var(--secondary-color);
                margin-bottom: 10px; display: flex; align-items: flex-start;
            }}
            .mission-item::before {{
                content: '🎯'; margin-right: 10px; font-size: 1.2em;
            }}

            #save-btn {{
                width: 100%; padding: 14px; margin-top: 1.5rem;
                font-size: 16px; font-weight: 700; color: white;
                background-color: var(--primary-color); border: none; border-radius: 12px;
                cursor: pointer; text-align: center;
                box-shadow: 0px 5px 10px rgba(43, 167, 209, 0.2);
            }}
        </style>
    </head>
    <body>
        <div id="capture-card">
            {diag_html}
            {praise_html}
            {improve_html}
            {missions_section_html}
        </div>
        <button id="save-btn">이미지로 저장 📸</button>

        <script>
        document.getElementById("save-btn").onclick = function() {{
            const cardElement = document.getElementById("capture-card");
            const btn = this;
            btn.innerHTML = "저장 중..."; btn.disabled = true;

            html2canvas(cardElement, {{
                useCORS: true, scale: 2, backgroundColor: null
            }}).then(canvas => {{
                const image = canvas.toDataURL("image/png");
                const link = document.createElement("a");
                link.href = image;
                link.download = "win-ugly-report.png";
                link.click();
                btn.innerHTML = "이미지로 저장 📸"; btn.disabled = false;
            }});
        }}
        </script>
    </body>
    </html>
    """
    return final_html


# --- 메인 애플리케이션 ---
def main():
    apply_ui_styles()
    
    st.markdown('<div class="icon-container">🥊</div>', unsafe_allow_html=True)
    st.markdown('<p class="title">Win Ugly 전략 분석기</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">승리를 위한 \'독한\' 마음가짐, 지금 바로 진단받으세요.<br>AI 코치가 냉철하게 분석해 드립니다.</p>', unsafe_allow_html=True)
    
    with st.form("input_form"):
        st.markdown('<p class="input-title">당신의 Win Ugly 전략은 무엇인가요?</p>', unsafe_allow_html=True)
        user_strategy = st.text_area(
            "user_strategy",
            placeholder="예: 저는 이번 경기에서 절대 실수하지 않도록 최선을 다하고, 동료들을 격려하며, 관중들에게 좋은 모습을 보여주고 싶습니다. 어떤 상황에서도 긍정적인 마음을 잃지 않겠습니다.",
            height=150,
            label_visibility="collapsed",
            max_chars=2000
        )
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("AI 코칭 리포트 받기", use_container_width=True)

    if submitted:
        if not user_strategy:
            st.warning("분석할 전략을 입력해주세요.")
        else:
            with st.spinner('AI 코치가 당신의 전략을 심층 분석하고 있습니다...'):
                feedback_text = get_gemini_feedback(user_strategy)
                if feedback_text:
                    st.session_state.report = feedback_text
    
    if 'report' in st.session_state and st.session_state.report:
        st.divider()
        st.markdown('<p class="title" style="text-align:center; margin-top: 2rem; margin-bottom: 1.5rem;">당신을 위한 Win Ugly 코칭 리포트 🏆</p>', unsafe_allow_html=True)
        report_component = build_report_component(st.session_state.report)
        st.components.v1.html(report_component, height=1000, scrolling=True)

if __name__ == "__main__":
    main()

