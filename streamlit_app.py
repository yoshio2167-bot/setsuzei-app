# --- サイドバー：入力パラメータ ---
st.sidebar.header("⚙️ 条件設定パラメータ")

# 1. 事業所得（例：最大値を2000万から3000万にしたい場合など）
gross_income = st.sidebar.number_input("個人事業所得 (万円)", min_value=200, max_value=3000, value=600, step=50)

# 2. 専従者給与（例：初期値を11万から12万に変えたい場合）
use_deputy = st.sidebar.checkbox("青色事業専従者（妻）を導入する", value=True)
if use_deputy:
    deputy_monthly = st.sidebar.slider("妻への月額給与 (万円/月)", min_value=5, max_value=20, value=12, step=1)
    deputy_annual = deputy_monthly * 12
else:
    deputy_annual = 0

# 3. 小規模企業共済（例：もっと細かい刻みにしたい場合など）
use_kyosai = st.sidebar.checkbox("小規模企業共済に加入する", value=True)
if use_kyosai:
    kyosai_monthly = st.sidebar.slider("共済の月額掛け金 (万円/月)", min_value=1.0, max_value=7.0, value=2.0, step=0.5)
    kyosai_annual = kyosai_monthly * 12
else:
    kyosai_annual = 0
