import streamlit as st
import pandas as pd

st.set_page_config(page_title="個人事業主 節税・キャッシュアウト試算シミュレータ", layout="wide")

st.title("🧮 個人事業主 節税・キャッシュアウト試算アプリ")
st.markdown("所得や専従者給与、共済、健康保険、家族構成を変更して、年間のトータル負担（キャッシュアウト）をリアルタイムに比較できます。")

# --- サイドバー：入力パラメータ ---
st.sidebar.header("⚙️ 条件設定パラメータ")

# 1. 事業所得 (経費を引く前のベース所得)
gross_income = st.sidebar.number_input("個人事業所得 (万円, 専従者給与控除前)", min_value=200, max_value=2000, value=600, step=50)

# 2. 家族構成（子供の人数・年齢）
st.sidebar.subheader("👨‍👩‍👧‍👦 家族構成")
st.sidebar.markdown("- 夫婦2人\n- お子様2人（**13歳・中学生** / **8歳・小学生**）")
# 16歳未満のため所得税・住民税の扶養控除対象外ですが、世帯人数として国保計算等に連動します
family_members = 4 

# 3. 青色事業専従者給与（妻への給与を経費にする）
use_zenshuja = st.sidebar.checkbox("妻を「青色事業専従者」にして給与を経費にする", value=True)
if use_zenshuja:
    spouse_monthly = st.sidebar.slider("妻への専従者給与月額 (万円/月)", min_value=5.0, max_value=15.0, value=10.8, step=0.5)
    spouse_annual_salary = spouse_monthly * 12
else:
    spouse_annual_salary = 0

# 4. 小規模企業共済
use_kyosai = st.sidebar.checkbox("小規模企業共済に加入する", value=True)
if use_kyosai:
    kyosai_monthly = st.sidebar.slider("共済の月額掛け金 (万円/月)", min_value=1.0, max_value=7.0, value=2.0, step=0.5)
    kyosai_annual = kyosai_monthly * 12
else:
    kyosai_annual = 0

# 5. 健康保険の選択
insurance_type = st.sidebar.radio("健康保険の選択", ["市区町村の国民健康保険", "建設国民健康保険組合（定額）"])

# 6. その他の固定費（返済など）
other_debt_monthly = st.sidebar.number_input("その他の返済等 (万円/月, 例: 10万×15ヶ月)", min_value=0, max_value=50, value=0, step=5)
other_debt_annual = other_debt_monthly * 12


# --- A. 今回の設定プランの計算ロジック ---
def calculate_plan_taxes(income, spouse_salary, kyosai_val, ins_sel, members):
    # 1. 売上から妻への給与（必要経費）を引いた実質所得
    effective_income = max(0, income - spouse_salary)
    
    # 2. 課税所得 (実質所得 - 基礎控除43万 - 共済掛け金)
    # ※13歳と8歳のお子様は16歳未満のため、所得税・住民税の扶養控除対象外
    taxable_income = max(0, effective_income - 43.0 - kyosai_val)
    
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
    
    # 住民税
    resident_tax = max(15.0, taxable_income * 0.10 + 2.0)
    
    # 個人事業税（実質所得ベース）
    biz_tax = max(0, (effective_income - 290.0) * 0.05) if effective_income > 290 else 0
    
    # 健康保険税
    if ins_sel == "建設国民健康保険組合（定額）":
        health_tax = 53.5  # 組合の定額ベース
    else:
        # 市区町村国保（所得割 ＋ 4人分の均等割を考慮して算出・上限104万）
        base_calc = (effective_income - 43.0) * 0.095 + (members * 3.5)
        health_tax = min(104.0, max(30.0, base_calc))
        
    pension = 41.0  # 夫婦2人分の国民年金
    total_out = income_tax + resident_tax + biz_tax + health_tax + pension
    return income_tax, resident_tax, biz_tax, health_tax, pension, total_out


# --- B. 現状のまま（対策なし：専従者なし・控除なし・市区町村国保） ---
def calculate_base_taxes(income, members):
    taxable_income = max(0, income - 43.0)
    
    if taxable_income <= 195:
        income_tax = taxable_income * 0.05
    elif taxable_income <= 330:
        income_tax = taxable_income * 0.10 - 9.75
    elif taxable_income <= 695:
        income_tax = taxable_income * 0.20 - 42.75
    else:
        income_tax = taxable_income * 0.23 - 63.6
    income_tax = max(1.0, income_tax)
    
    resident_tax = taxable_income * 0.10 + 4.0
    biz_tax = max(0, (income - 290.0) * 0.05) if income > 290 else 0
    
    base_calc = (income - 43.0) * 0.095 + (members * 3.5)
    health_tax = min(104.0, max(30.0, base_calc))
    
    pension = 41.0
    total_out = income_tax + resident_tax + biz_tax + health_tax + pension
    return income_tax, resident_tax, biz_tax, health_tax, pension, total_out


# 計算実行
inc_tax, res_tax, biz_tax, health_tax, pension, total_tax_soc = calculate_plan_taxes(
    gross_income, spouse_annual_salary, kyosai_annual, insurance_type, family_members
)

base_inc_tax, base_res_tax, base_biz_tax, base_health_tax, base_pension, base_base_total = calculate_base_taxes(
    gross_income, family_members
)

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
        f"- 世帯構成（ご夫婦＋お子様2人：13歳・8歳）を反映したシミュレータになっています。\n"
        f"- 奥様への青色事業専従者給与（月給 {spouse_monthly}万円）と小規模企業共済、建設国保の組み合わせにより、年間トータル負担を最適化しています[span_0](start_span)[span_0](end_span)[span_1](start_span)[span_1](end_span)。")
