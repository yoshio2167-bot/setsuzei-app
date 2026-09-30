import streamlit as st
import pandas as pd

st.set_page_config(page_title="個人事業主 節税・キャッシュアウト試算シミュレータ", layout="wide")

st.title("🧮 個人事業主 節税・キャッシュアウト試算アプリ")
st.markdown("所得や配偶者控除、共済の掛け金、保険の選択肢を変更して、年間のトータル負担（キャッシュアウト）をリアルタイムに比較できます。")

# --- サイドバー：入力パラメータ ---
st.sidebar.header("⚙️ 条件設定パラメータ")

# 1. 事業所得
gross_income = st.sidebar.number_input("個人事業所得 (万円)", min_value=200, max_value=2000, value=600, step=50)

# 2. 配偶者（妻）の扶養・給与設定
use_spouse_deduction = st.sidebar.checkbox("妻を配偶者の扶養（控除）にする", value=True)
if use_spouse_deduction:
    spouse_monthly = st.sidebar.slider("妻のパート・給与月額 (万円/月)", min_value=5.0, max_value=15.0, value=10.8, step=0.5)
    spouse_annual_income = spouse_monthly * 12
else:
    spouse_annual_income = 0

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
other_debt_monthly = st.sidebar.number_input("その他の返済等 (万円/月, 例: 10万×15ヶ月)", min_value=0, max_value=50, value=0, step=5)
other_debt_annual = other_debt_monthly * 12


# --- 計算ロジック ---
def calculate_taxes(income, spouse_inc, kyosai_val, ins_sel):
    # 配偶者特別控除の目安（妻の年収に応じた控除額）
    spouse_deduction = 0
    if spouse_inc > 0:
        if spouse_inc <= 150:
            spouse_deduction = 38.0
        elif spouse_inc <= 201:
            spouse_deduction = max(10.0, 38.0 - (spouse_inc - 150) * 0.6)
            
    # 控除後の課税所得 (基礎控除43万 + 配偶者特別控除 + 共済)
    taxable_income = max(0, income - 43 - spouse_deduction - kyosai_val)
    
    # 所得税
    if taxable_income <= 195:
        income_tax = taxable_income * 0.05
    elif taxable_income <= 330:
        income_tax = taxable_income * 0.10 - 9.75
    elif taxable_income <= 695:
        income_tax = taxable_income * 0.20 - 42.75
    else:
        income_tax = taxable_income * 0.23 - 63.6
    income_tax = max(1.0, income_tax)
    
    # 住民税（改正後の負担軽減を反映した標準算出）
    resident_tax = taxable_income * 0.10 + 2.0
    
    # 個人事業税（事業主控除290万円を適用）
    biz_tax = max(0, (income - 290) * 0.05) if income > 290 else 0
    
    # 健康保険税の判定
    if ins_sel == "建設国民健康保険組合（定額）":
        health_tax = 53.0
    else:
        health_tax = min(104, max(30, (income - 43) * 0.095))
        
    # 国民年金 (夫婦2人分固定)
    pension = 41.0
    
    total_out = income_tax + resident_tax + biz_tax + health_tax + pension
    return income_tax, resident_tax, biz_tax, health_tax, pension, total_out

# 選択された条件での計算
inc_tax, res_tax, biz_tax, health_tax, pension, total_tax_soc = calculate_taxes(gross_income, spouse_annual_income, kyosai_annual, insurance_type)

# 比較用の「現状ベース（対策なし・配偶者控除なし・市区町村国保・共済なし）」の計算
base_inc_tax, base_res_tax, base_biz_tax, base_health_tax, base_pension, base_base_total = calculate_taxes(gross_income, 0, 0, "市区町村の国民健康保険")

# --- 画面表示 ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 年間トータル負担（税金＋社保＋年金）",
        value=f"{total_tax_soc:.1f} 万円",
        delta=f"{total_tax_soc - base_base_total:.1f} 万円 (対現状)"
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

# 詳細内訳比較テーブル
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
        f"- 奥様を扶養（配偶者特別控除の対象）にしつつ、パート収入を **月額 {spouse_monthly}万円**（年間 {spouse_annual_income:.1f}万円）に設定しています。\n"
        f"- 小規模企業共済（年間 **{kyosai_annual}万円**）と組み合わせることで、無理のない節税と控除を両立しています。\n"
        f"- 健康保険に **{insurance_type}** を選択した状態でのトータル負担をリアルタイムで確認できます。")
