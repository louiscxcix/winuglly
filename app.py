import os
import re

import google.generativeai as genai
import streamlit as st

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="Win Ugly 전략 분석기", page_icon="🥊", layout="centered")

# --- Gemini API 키 설정 ---
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    st.error(
        "Gemini API 키를 설정하는 데 문제가 발생했습니다. Streamlit Cloud의 'Settings > Secrets'에 API 키를 올바르게 설정했는지 확인해주세요."
    )
    st.stop()


def get_gemini_feedback(user_strategy_input):
    """
    Gemini API를 호출하여 사용자의 전략에 대한 피드백을 생성합니다.
    """
    # 가독성 향상을 위해 출력 형식에 줄 바꿈을 명시적으로 요청하도록 프롬프트를 수정했습니다.
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
    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    response = model.generate_content(prompt)
    return response.text


def build_report_component(feedback_text):
    """
    피드백 텍스트를 기반으로, 이미지 저장 기능이 포함된 완전한 HTML 컴포넌트를 생성합니다.
    """
    # 1. 피드백 텍스트를 HTML 콘텐츠로 파싱
    sections = re.split(r"###\s*\d\.", feedback_text)
    report_content_html = ""

    # 리포트 헤더 추가
    report_content_html += """
        <div class="report-header">
            <div class="header-icon">🥊</div>
            <div class="header-text">
                <h2>Win Ugly</h2>
                <p>승리를 위한 '독한' 마음가짐, 지금 바로 진단받으세요.</p>
            </div>
        </div>
    """

    # 종합 진단
    if len(sections) > 1:
        report_content_html += f"""
        <div class="report-section">
            <h3>종합 진단</h3>
            <p class="section-body">{sections[1].strip()}</p>
        </div>
        """

    # 칭찬할 점
    if len(sections) > 2:
        content = sections[2].split(")", 1)[-1].strip()
        quote_match = re.search(r">\s*(.*)", content)
        if quote_match:
            quote = quote_match.group(1)
            raw_feedback = content.split(quote_match.group(0))[-1].strip()
            feedback_paragraphs = "".join([f"<p class='section-body'>{p.strip()}</p>" for p in raw_feedback.split("\n") if p.strip()])
            report_content_html += f"""
            <div class="report-section">
                <h3>칭찬할 점 (Ugly Points)</h3>
                <div class="quote-box quote-box-good">"{quote}"</div>
                {feedback_paragraphs}
            </div>
            """

    # 보완할 점
    if len(sections) > 3:
        content = sections[3].split(")", 1)[-1].strip()
        quote_match = re.search(r">\s*(.*)", content)
        if quote_match:
            quote = quote_match.group(1)
            raw_feedback = content.split(quote_match.group(0))[-1].strip()
            feedback_paragraphs = "".join([f"<p class='section-body'>{p.strip()}</p>" for p in raw_feedback.split("\n") if p.strip()])
            report_content_html += f"""
            <div class="report-section">
                <h3>보완할 점 (Nice Points)</h3>
                <div class="quote-box quote-box-bad">"{quote}"</div>
                {feedback_paragraphs}
            </div>
            """

    # Win Ugly 미션
    if len(sections) > 4:
        missions = sections[4].strip().split("\n- ")
        missions_html = "".join([f"<li>{m.strip()}</li>" for m in missions if m.strip()])
        report_content_html += f"""
        <div class="report-section">
            <h3>당신의 Win Ugly 미션</h3>
            <ul class="mission-list">{missions_html}</ul>
        </div>
        """

    # 2. 최종 HTML 컴포넌트 조합
    final_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
            body {{
                font-family: 'Noto Sans KR', sans-serif;
                background-color: #F1F2F5;
                margin: 0;
                padding: 16px;
            }}
            #report-card {{
                background: white;
                border-radius: 32px;
                box-shadow: 0 8px 32px rgba(33, 64, 131, 0.08);
                color: #374151;
                overflow: hidden;
            }}
            .report-header {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 24px;
            }}
            .header-icon {{
                font-size: 40px;
                width: 68px;
                height: 68px;
                display: flex;
                justify-content: center;
                align-items: center;
                background: rgba(12, 124, 162, 0.04);
                border-radius: 50%;
            }}
            .header-text h2 {{
                color: #0D1628;
                font-size: 20px;
                font-weight: 700;
                margin: 0 0 4px 0;
            }}
            .header-text p {{
                color: #86929A;
                font-size: 13px;
                margin: 0;
            }}
            .report-section {{
                padding: 24px;
                border-top: 1px solid #F1F1F1;
            }}
            .report-section h3 {{
                color: #0D1628;
                font-size: 18px;
                font-weight: 700;
                margin: 0 0 16px 0;
            }}
            .section-body {{
                color: #86929A;
                font-size: 14px;
                line-height: 1.7;
            }}
            .quote-box {{
                padding: 12px 16px;
                margin: 16px 0;
                border-radius: 8px;
                font-weight: 700;
                font-size: 14px;
                color: #0D1628;
                border-left-width: 10px;
                border-left-style: solid;
            }}
            .quote-box-good {{
                background-color: rgba(49, 157, 208, 0.15);
                border-color: rgba(49, 157, 208, 0.60);
            }}
            .quote-box-bad {{
                background-color: rgba(238, 125, 141, 0.15);
                border-color: rgba(238, 125, 141, 0.60);
            }}
            .mission-list {{
                list-style-type: none;
                padding-left: 0;
                color: #86929A;
                font-size: 14px;
            }}
            .mission-list li {{
                margin-bottom: 10px;
                display: flex;
                align-items: flex-start;
            }}
            .mission-list li::before {{
                content: "🎯";
                margin-right: 10px;
                font-size: 1.2em;
            }}
            #save-btn {{
                display: block;
                width: calc(100% - 32px);
                padding: 16px;
                margin: 0 16px 16px 16px;
                font-family: 'Noto Sans KR', sans-serif;
                font-size: 16px;
                font-weight: bold;
                color: white;
                background: #2BA7D1;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                text-align: center;
                transition: all 0.2s ease;
                box-shadow: 0 5px 15px rgba(43, 167, 209, 0.2);
            }}
            #save-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(43, 167, 209, 0.3);
            }}
        </style>
    </head>
    <body>
        <div id="capture-area">
            <div id="report-card">
                {report_content_html}
            </div>
        </div>
        <button id="save-btn">리포트 이미지로 저장 🖼️</button>
        <script>
        document.getElementById("save-btn").onclick = function() {{
            const cardElement = document.getElementById("capture-area");
            const originalButtonText = this.innerHTML;
            this.innerHTML = "저장 중...";
            this.disabled = true;

            html2canvas(cardElement, {{
                useCORS: true,
                scale: 2,
                backgroundColor: '#F1F2F5',
                logging: true
            }}).then(canvas => {{
                const image = canvas.toDataURL("image/png");
                const link = document.createElement("a");
                link.href = image;
                link.download = "win-ugly-report.png";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                this.innerHTML = originalButtonText;
                this.disabled = false;
            }});
        }}
        </script>
    </body>
    </html>
    """
    return final_html


# --- Streamlit UI 구성 ---
st.markdown('<style>body { background-color: #F1F2F5; }</style>', unsafe_allow_html=True)
st.title("🥊 Win Ugly 전략 분석기")
st.markdown("##### 승리를 위한 '독한' 마음가짐, 지금 바로 진단받으세요.")

with st.container(border=True):
    user_strategy = st.text_area(
        "**👇 당신의 'Win Ugly' 전략을 여기에 입력하세요**",
        height=150,
        placeholder="예시: 저는 이번 경기에서 절대 실수하지 않도록 최선을 다하고, 동료들을 격려하며, 관중들에게 좋은 모습을 보여주고 싶습니다. 어떤 상황에서도 긍정적인 마음을 잃지 않겠습니다.",
    )

    if st.button("분석 시작하기", type="primary", use_container_width=True):
        if user_strategy:
            with st.spinner("AI 코치가 당신의 전략을 심층 분석하고 있습니다..."):
                try:
                    feedback_text = get_gemini_feedback(user_strategy)
                    report_component = build_report_component(feedback_text)
                    st.session_state.report = report_component
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {e}")
        else:
            st.warning("분석할 전략을 입력해주세요.")

if 'report' in st.session_state:
    st.markdown("---")
    st.subheader("🏆 당신을 위한 Win Ugly 코칭 리포트")
    st.components.v1.html(st.session_state.report, height=1200, scrolling=True)

