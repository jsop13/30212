import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 항생제 클래스
class Antibiotic:
    def __init__(self, name, pKa_list, active_form='neutral', max_activity=1.0, min_MIC=1.0):
        self.name = name
        self.pKa_list = pKa_list
        self.active_form = active_form
        self.max_activity = max_activity
        self.min_MIC = min_MIC

    def ionization_ratio(self, pH):
        pKa = self.pKa_list[0]
        if self.active_form == 'neutral':
            return 1 / (1 + 10**(pH - pKa))
        elif self.active_form == 'ionized':
            return 1 / (1 + 10**(pKa - pH))
        else:
            raise ValueError("Invalid active_form")

    def predict_activity(self, pH):
        ionized_ratio = self.ionization_ratio(pH)

        if self.active_form == 'ionized':
            return self.max_activity * ionized_ratio

        elif self.active_form == 'neutral':
            return self.max_activity * (1 - ionized_ratio)
        else:
            raise ValueError("활성화 상태는 '이온화' 또는 '중성' 이어야 합니다.")

    def predict_MIC(self, pH):
        if self.active_form == 'neutral':
            activity = self.predict_activity(pH)
            return self.min_MIC / (activity + 1e-6)  # 중성형이 많을수록 MIC 작아짐
        elif self.active_form == 'ionized':
            ion_ratio = self.ionization_ratio(pH)
            return self.min_MIC / (ion_ratio + 1e-6)  # 이온화형이 많을수록 MIC 작아짐
        else:
            raise ValueError("활성화 상태는 '이온화' 또는 '중성' 이어야 합니다.")


# 항생제 데이터
antibiotics_data = {
    'Ampicillin': {
        'pKa_list': [7.2],
        'active_form': 'neutral',
        'max_activity': 1.0,
        'min_MIC': 0.5
    },
    'Kanamycin': {
        'pKa_list': [8.2],
        'active_form': 'ionized',
        'max_activity': 1.0,
        'min_MIC': 1.0
    },
    'Tetracycline': {
        'pKa_list': [3.3, 7.7, 9.7],
        'active_form': 'neutral',
        'max_activity': 1.0,
        'min_MIC': 1.0
    },  
    'Erythromycin': {
        'pKa_list': [8.8],
        'active_form': 'neutral',
        'max_activity': 1.0,
        'min_MIC': 0.004
    }
}

# 항생제 객체
antibiotics = {}
for name, props in antibiotics_data.items():
    antibiotics[name] = Antibiotic(
        name, props['pKa_list'], props['active_form'],
        props['max_activity'], props['min_MIC']
    )

# Streamlit UI(그래프프)
st.title("항생제 주변의의 pH에 따른 이온화율, MIC 변화")
st.sidebar.header("항생제 선택")
selected = st.sidebar.multiselect("항생제를 선택하세요:", list(antibiotics.keys()), default=list(antibiotics.keys()))

st.sidebar.header("그래프 선택")
show_activity = st.sidebar.checkbox("활성형 비율", value=True)
show_ionization = st.sidebar.checkbox("이온화율", value=True)
show_MIC = st.sidebar.checkbox("MIC", value=True)

# 그래프 함수 def
def plot_combined_graph(ab: Antibiotic):
    # ax1, ax2
    fig, ax1 = plt.subplots(figsize=(10, 6))

    pH_values = np.linspace(3, 11, 100)

    # 활성형 비율 G
    activity_vals = [ab.predict_activity(pH) for pH in pH_values]
    ax1.plot(pH_values, activity_vals, 'g-', label='활성형 비율🦠', linewidth=2)

    # 이온화율 B
    ion_ratio_vals = [ab.ionization_ratio(pH) for pH in pH_values]
    ax1.plot(pH_values, ion_ratio_vals, 'b--', label='이온화율', linewidth=2)

    ax1.set_xlabel('pH')
    ax1.set_ylabel('활성형 비율 / 이온화율 (0~1)', color='black')
    ax1.set_ylim(0, 1.05)
    ax1.tick_params(axis='y')

    # MIC R
    ax2 = ax1.twinx()
    MIC_vals = [ab.predict_MIC(pH) for pH in pH_values]
    ax2.plot(pH_values, MIC_vals, 'r:', label='MIC (μg/mL)', linewidth=2)
    ax2.set_ylabel('MIC (μg/mL)', color='red')
    ax2.set_yscale('log')
    ax2.tick_params(axis='y', labelcolor='red')

    # y축 합체체
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # 사이트 제목
    plt.title(f"{ab.name}의 pH에 따른 활성형 비율🦠, 이온화율, MIC 변화")
    plt.grid(True)
    plt.tight_layout()

    # 그래프 렌더링!!!
    st.pyplot(fig)


# Streamlit UI 코드
st.header("📊")

# 항생제 선택택
selected_single = st.selectbox("📌 항생제를 선택하세요:", list(antibiotics.keys()))

# 항생제 선택-그래프 생성성
if selected_single:
    ab = antibiotics[selected_single] 
    plot_combined_graph(ab) 
