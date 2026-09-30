import streamlit as st
import pandas as pd

st.set_page_config(page_title="個人事業主 節税・キャッシュアウト試算シミュレータ", layout="wide")

st.title("🧮 個人事業主 節税・キャッシュアウト試算アプリ")
st.markdown("所得や専従者給与、共済の掛け金、保険の選択肢を変更して、年間のトータル負担（キャッシュアウト）をリアルタイムに比較できます。")

# --- サイドバー：入力パラメータ ---
st.sidebar.header("⚙️ 条件設定パラメータ")

# 1. 事業所得
gross_income = st.sidebar.number_input("個人事業所得 (万円)", min_value=200, max_value=2000, value=600, step=50)

# 2. 専従者給与
use_deputy = st.sidebar.checkbox("青色事業専従者（妻）を導入する", value=True)
if use_deputy:
    deputy_monthly = st.sidebar.slider("妻への月額給与 (万円/月)", min_value=5, max_value=15, value=11, step=1)
    deputy_annual = deputy_monthly * 12
else:
    deputy_annual = 0

# 3. 小規模企業共済
use_kyosai = st.sidebar.checkbox("小規模企業共済に加入する", value=True)
if use_kyosai:
    kyosai_monthly = st.sidebar.slider("共済の月額掛け金 (万円/月)", min_value=1.0, max_value=7.0, value=2.0, step=0.5)
    kyosai_annual = kyosai_monthly * 12
else:
    kyosai_annual = 0

# 4. 健康保険の選択
insurance_type = st.sidebar.radio("健康保険の選択", ["市区町村の国民健康保険", "建設国民健康保険組合（定額）"])

# 5. その他の固定費（返済など）
other_debt_monthly = st.sidebar.number_input("その他の返済等 (万円/月, 例: 10万×15ヶ月)", min_value=0, max_value=50, value=10, step=5)
other_debt_annual = other_debt_monthly * 12


# --- 計算ロジック ---
def calculate_taxes(income, dep_val, kyosai_val, ins_sel):
    taxable_income = max(0, income - 43 - dep_val - kyosai_val)
    
    if taxable_income <= 195:
        income_tax = taxable_income * 0.05
    elif taxable_income <= 330:
        income_tax = taxable_income * 0.10 - 9.75
    elif taxable_income <= 695:
        income_tax = taxable_income * 0.20 - 42.75
    elif taxable_income <= 900:
        income_tax = taxable_income * 0.23 - 63.6
    else:
        income_tax = taxable_income * 0.33 - 153.6
    income_tax = max(10, income_tax)
    
    resident_tax = taxable_income * 0.10 + 5.0
    biz_tax = max(0, (income - 210) * 0.05) if income > 210 else 0
    
    if ins_sel == "市区町村の国民健康保険":
        health_tax = min(104, max(30, (income - 43) * 0.095))
    else:
        health_tax = 53.0
        
    pension = 41.0
    total_out = income_tax + resident_tax + biz_tax + health_tax + pension
    return income_tax, resident_tax, biz_tax, health_tax, pension, total_out

inc_tax, res_tax, biz_tax, health_tax, pension, total_tax_soc = calculate_taxes(gross_income, deputy_annual, kyosai_annual, insurance_type)
base_inc_tax, base_res_tax, base_biz_tax, base_health_tax, base_pension, base_base_total = calculate_taxes(gross_income, 0, 0, "市区町村の国民健康保険")

# --- 画面表示 ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 年間トータル負担（税金＋社保＋年金）",
        value=f"{total_tax_soc:.1f} 万円",
        delta=f"{total_tax_soc - base_base_total:.1f} 万円 (対現状)",
        delta_inverse=True
    )

with col2:
    st.metric(
        label="📅 月換算のキャッシュアウト",
        value=f"{(total_tax_soc + other_debt_annual)/12:.1f} 万円/月"
    )

with col3:
    st.metric(
        label="🛡️ 現状からの節税・軽減効果",
        value=f"{base_base_total - total_tax_soc:.1f} 万円 お得！",
        delta="手残りアップ"
    )

st.divider()

st.subheader("📊 負担内訳の比較 (万円 / 年)")

comparison_df = pd.DataFrame({
    "項目": ["所得税", "住民税", "個人事業税", "健康保険", "国民年金", "【年間合計 (税金+社保)】", "返済などその他の固定費", "【総キャッシュアウト】"],
    "現状のまま (対策なし)": [
        f"{base_inc_tax:.1f}", f"{base_res_tax:.1f}", f"{base_biz_tax:.1f}", f"{base_health_tax:.1f}", f"{base_pension:.1f}",
        f"**{base_base_total:.1f}**", f"{other_debt_annual:.1f}", f"**{base_base_total + other_debt_annual:.1f}**"
    ],
    "今回の設定プラン": [
        f"{inc_tax:.1f}", f"{res_tax:.1f}", f"{biz_tax:.1f}", f"{health_tax:.1f}", f"{pension:.1f}",
        f"**{total_tax_soc:.1f}**", f"{other_debt_annual:.1f}", f"**{total_tax_soc + other_debt_annual:.1f}**"
    ],
    "差額 (節税効果)": [
        f"{inc_tax - base_inc_tax:.1f}", f"{res_tax - base_res_tax:.1f}", f"{biz_tax - base_biz_tax:.1f}", f"{health_tax - base_health_tax:.1f}", f"0.0",
        f"**{total_tax_soc - base_base_total:.1f}**", f"0.0", f"**{total_tax_soc - base_base_total:.1f}**"
    ]
})

st.table(comparison_df)

st.info(f"💡 **現在のシミュレーションのポイント：**\n"
        f"- ご主人の所得 **{gross_income}万円** に対し、専従者給与（年間 **{deputy_annual}万円**）と小規模企業共済（年間 **{kyosai_annual}万円**）の合計 **{deputy_annual + kyosai_annual}万円** が所得から控除されています。\n"
        f"- 健康保険に **{insurance_type}** を選択しているため、所得増による保険料の跳ね上がりが調整されています。\n"
        f"- 返済（月{other_debt_monthly}万円×15ヶ月）を含めても、毎月の資金繰りがどうなるかスライダーを動かして試算できます。")
