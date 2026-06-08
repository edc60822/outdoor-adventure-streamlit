# Streamlit 戶外冒險教育研究問題一、二分析模板
# 用途：使用動態圓餅圖、雷達圖、熱力圖、折線圖呈現 ANOVA 與 t 檢定結果
# 執行方式：streamlit run st_practice_7_1.py

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 1. 頁面基本設定
# ==========================================
st.set_page_config(
    page_title="NTTUES戶外冒險教育",
    page_icon="🏕️",
    layout="wide"
)

st.title("參與冒險教育孩子真的成長了嗎？")
st.subheader("🏕️ NTTUES戶外冒險教育課程成效分析")
st.markdown("### 114-2 運動大數據與視覺化分析專題研究 / 唐翊瑄")
st.markdown("---")

# ==========================================
# 2. 自動尋找並載入資料
# ==========================================
all_files = os.listdir()

excel_files = [f for f in all_files if f.endswith(".xlsx")]
csv_files = [f for f in all_files if f.endswith(".csv")]

if len(csv_files) == 0:
    st.error("找不到 CSV 檔案，請確認 t_test_all_results 檔案已上傳。")
    st.stop()

if len(excel_files) == 0:
    st.error("找不到 Excel 檔案，請確認單因子重複量數分析檔案已上傳。")
    st.stop()

ttest_candidates = [
    f for f in csv_files
    if "t_test" in f or "ttest" in f or "t檢定" in f
]

if len(ttest_candidates) > 0:
    ttest_file = ttest_candidates[0]
else:
    ttest_file = csv_files[0]

anova_candidates = [
    f for f in excel_files
    if "單因子" in f or "重複量數" in f or "ANOVA" in f or "anova" in f
]

if len(anova_candidates) > 0:
    anova_file = anova_candidates[0]
else:
    anova_file = excel_files[0]

try:
    ttest_df = pd.read_csv(ttest_file, encoding="utf-8-sig")
except Exception:
    try:
        ttest_df = pd.read_csv(ttest_file, encoding="utf-8")
    except Exception:
        ttest_df = pd.read_csv(ttest_file, encoding="big5")

try:
    life_anova = pd.read_excel(anova_file, sheet_name="表4-10生活效能_ANOVA")
    problem_anova = pd.read_excel(anova_file, sheet_name="表4-11問題解決_ANOVA")

    life_desc = pd.read_excel(anova_file, sheet_name="生活效能_描述統計")
    problem_desc = pd.read_excel(anova_file, sheet_name="問題解決_描述統計")

except Exception as e:
    st.error("Excel 工作表名稱可能不一致，請確認工作表名稱是否正確。")
    st.write("錯誤訊息：", e)

    try:
        xls = pd.ExcelFile(anova_file)
        st.write("目前 Excel 中的工作表名稱：")
        st.write(xls.sheet_names)
    except Exception:
        pass

    st.stop()

# 清理欄位名稱
ttest_df.columns = ttest_df.columns.astype(str).str.strip()
life_anova.columns = life_anova.columns.astype(str).str.strip()
problem_anova.columns = problem_anova.columns.astype(str).str.strip()
life_desc.columns = life_desc.columns.astype(str).str.strip()
problem_desc.columns = problem_desc.columns.astype(str).str.strip()

# 檢查 t 檢定必要欄位
required_cols = ["自變數", "依變數", "t值", "p值"]

missing_cols = [
    col for col in required_cols
    if col not in ttest_df.columns
]

if len(missing_cols) > 0:
    st.error("CSV 缺少必要欄位，請確認是否為 t 檢定結果檔。")
    st.write("缺少欄位：", missing_cols)
    st.write("目前 CSV 欄位：")
    st.write(ttest_df.columns.tolist())
    st.dataframe(ttest_df.head())
    st.stop()

# ==========================================
# 3. 整理 t 檢定資料
# ==========================================
ttest_df["p_num"] = (
    ttest_df["p值"]
    .astype(str)
    .str.replace("*", "", regex=False)
    .str.strip()
)

ttest_df["p_num"] = pd.to_numeric(ttest_df["p_num"], errors="coerce")
ttest_df["t值"] = pd.to_numeric(ttest_df["t值"], errors="coerce")

ttest_df["顯著性"] = np.where(
    ttest_df["p_num"] < 0.05,
    "顯著",
    "未顯著"
)

ttest_df["構面代碼"] = ttest_df["依變數"].apply(
    lambda x: "_".join(str(x).split("_")[:2])
)

ttest_df["測量代碼"] = ttest_df["依變數"].apply(
    lambda x: str(x).split("_")[-1]
)

stage_map = {
    "1": "前測",
    "2": "中測",
    "3": "後測"
}

ttest_df["測量階段"] = ttest_df["測量代碼"].map(stage_map)

code_name_map = {
    "TM_SM": "時間管理",
    "EC_SM": "情緒控制",
    "AM_SM": "成就動機",
    "SL_SM": "社交領導",
    "SC_SM": "自信心",
    "AI_SM": "主動積極",
    "PD_SM": "發現問題",
    "DP_SM": "確定問題",
    "SF_SM": "形成策略",
    "EI_SM": "執行實現",
    "RI_SM": "整合成果",
    "AP_SM": "推廣應用"
}

ttest_df["構面"] = ttest_df["構面代碼"].map(code_name_map)

life_codes = [
    "TM_SM",
    "EC_SM",
    "AM_SM",
    "SL_SM",
    "SC_SM",
    "AI_SM"
]

ttest_df["問卷"] = np.where(
    ttest_df["構面代碼"].isin(life_codes),
    "生活效能",
    "問題解決能力"
)

background_map = {
    "gender": "性別",
    "club": "是否參加運動性社團",
    "time": "參與運動性社團的時間"
}

ttest_df["背景變項"] = ttest_df["自變數"].map(background_map)

# ==========================================
# 4. 整理 ANOVA 與描述統計資料
# ==========================================
anova_df = pd.concat(
    [life_anova, problem_anova],
    ignore_index=True
)

desc_df = pd.concat(
    [life_desc, problem_desc],
    ignore_index=True
)

anova_df["p值"] = pd.to_numeric(anova_df["p值"], errors="coerce")
anova_df["F值"] = pd.to_numeric(anova_df["F值"], errors="coerce")
anova_df["效果量"] = pd.to_numeric(anova_df["效果量"], errors="coerce")

anova_df["顯著性"] = np.where(
    anova_df["p值"] < 0.05,
    "顯著",
    "未顯著"
)

desc_df["平均數"] = pd.to_numeric(desc_df["平均數"], errors="coerce")
desc_df["標準差"] = pd.to_numeric(desc_df["標準差"], errors="coerce")

# ==========================================
# 5. 側邊欄設定
# ==========================================
st.sidebar.header("🏕️ NTTUES戶外冒險教育")

selected_background = st.sidebar.selectbox(
    "基本結構分布",
    ["性別", "是否參加運動性社團", "參與運動性社團的時間"],
    key="sidebar_background"
)

selected_questionnaire = st.sidebar.selectbox(
    "問卷類型",
    ["生活效能", "問題解決能力"],
    key="sidebar_questionnaire"
)

life_dimensions = [
    "時間管理",
    "情緒控制",
    "成就動機",
    "社交領導",
    "自信心",
    "主動積極"
]

problem_dimensions = [
    "發現問題",
    "確定問題",
    "形成策略",
    "執行實現",
    "整合成果",
    "推廣應用"
]

if selected_questionnaire == "生活效能":
    selected_dimension = st.sidebar.selectbox(
        "選擇構面",
        life_dimensions,
        key="sidebar_life_dimension"
    )
else:
    selected_dimension = st.sidebar.selectbox(
        "選擇構面",
        problem_dimensions,
        key="sidebar_problem_dimension"
    )

selected_stage = st.sidebar.selectbox(
    "測量階段",
    ["前測", "中測", "後測"],
    key="sidebar_stage"
)

# 圖表顏色主題設定
color_theme = st.sidebar.selectbox(
    "圖表顏色主題",
    ["暖色系", "藍綠系", "粉紫系", "灰階系"],
    key="sidebar_color_theme"
)

if color_theme == "暖色系":
    pie_colors = px.colors.qualitative.Set2
    line_colors = px.colors.qualitative.Set2
    heatmap_colors = "YlOrRd"

elif color_theme == "藍綠系":
    pie_colors = px.colors.qualitative.Pastel
    line_colors = px.colors.qualitative.Pastel
    heatmap_colors = "GnBu"

elif color_theme == "粉紫系":
    pie_colors = px.colors.qualitative.Pastel1
    line_colors = px.colors.qualitative.Pastel1
    heatmap_colors = "PuRd"

else:
    pie_colors = px.colors.qualitative.G10
    line_colors = px.colors.qualitative.G10
    heatmap_colors = "Greys"

st.sidebar.markdown("---")
st.sidebar.write("🎨 **目前圖表顏色主題**")
st.sidebar.write(color_theme)

st.sidebar.write("📁 **t 檢定檔案**")
st.sidebar.write(ttest_file)
st.sidebar.write("📁 **ANOVA 檔案**")
st.sidebar.write(anova_file)

# ==========================================
# 6. 依照側邊欄條件篩選資料
# ==========================================
filtered_df = ttest_df[
    (ttest_df["背景變項"] == selected_background) &
    (ttest_df["問卷"] == selected_questionnaire) &
    (ttest_df["構面"] == selected_dimension) &
    (ttest_df["測量階段"] == selected_stage)
].copy()

# ==========================================
# 7. 基本結構分布連動分析
# ==========================================
st.subheader("📊 基本結構分布連動分析")

col_a, col_b, col_c, col_d, col_e = st.columns(5)

with col_a:
    st.metric("基本結構分布", selected_background)

with col_b:
    st.metric("問卷類型", selected_questionnaire)

with col_c:
    st.metric("構面", selected_dimension)

with col_d:
    st.metric("測量階段", selected_stage)

with col_e:
    st.metric("顏色主題", color_theme)

st.markdown("---")

# ==========================================
# 8. 右側資料與圓餅圖連動
# ==========================================
if len(filtered_df) > 0:

    row = filtered_df.iloc[0]

    if selected_background == "性別":
        pie_data = pd.DataFrame({
            "組別": ["男生", "女生"],
            "人數": [row["男生_N"], row["女生_N"]],
            "平均數": [row["男生_M"], row["女生_M"]],
            "標準差": [row["男生_SD"], row["女生_SD"]]
        })

    elif selected_background == "是否參加運動性社團":
        pie_data = pd.DataFrame({
            "組別": ["有參加運動性社團", "無參加運動性社團"],
            "人數": [
                row["有參加社團_N"],
                row["無參加社團_N"]
            ],
            "平均數": [
                row["有參加社團_M"],
                row["無參加社團_M"]
            ],
            "標準差": [
                row["有參加社團_SD"],
                row["無參加社團_SD"]
            ]
        })

    elif selected_background == "參與運動性社團的時間":

        if "一年以下_N" in row.index:
            under_one_prefix = "一年以下"
        elif "未滿一年_N" in row.index:
            under_one_prefix = "未滿一年"
        else:
            st.error("找不到『一年以下』或『未滿一年』相關欄位。")
            st.write("目前資料欄位：")
            st.write(row.index.tolist())
            st.stop()

        pie_data = pd.DataFrame({
            "組別": ["未滿一年", "一年以上"],
            "人數": [
                row[f"{under_one_prefix}_N"],
                row["一年以上_N"]
            ],
            "平均數": [
                row[f"{under_one_prefix}_M"],
                row["一年以上_M"]
            ],
            "標準差": [
                row[f"{under_one_prefix}_SD"],
                row["一年以上_SD"]
            ]
        })

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.markdown("### 🥧 平均數分布圓餅圖")

        fig = px.pie(
            pie_data,
            names="組別",
            values="平均數",
            hole=0.4,
            color_discrete_sequence=pie_colors,
            title=f"{selected_background}在「{selected_questionnaire}－{selected_dimension}－{selected_stage}」的平均數分布"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="label+percent+value"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.markdown("### 📋 連動數據")

        st.metric("t值", round(row["t值"], 3))
        st.metric("p值", round(row["p_num"], 3))
        st.metric("顯著性", row["顯著性"])

        st.dataframe(
            pie_data.round(3),
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("📄 篩選後原始資料")

    display_filtered_df = filtered_df.rename(columns={
        "一年以下_N": "未滿一年_N",
        "一年以下_M": "未滿一年_M",
        "一年以下_SD": "未滿一年_SD"
    })

    st.dataframe(
        display_filtered_df,
        use_container_width=True
    )

else:
    st.warning("目前條件沒有篩選到資料，請確認背景變項、問卷類型、構面與測量階段是否一致。")

    st.write("目前資料中的背景變項：")
    st.write(ttest_df["背景變項"].dropna().unique())

    st.write("目前資料中的問卷類型：")
    st.write(ttest_df["問卷"].dropna().unique())

    st.write("目前資料中的構面：")
    st.write(ttest_df["構面"].dropna().unique())

    st.write("目前資料中的測量階段：")
    st.write(ttest_df["測量階段"].dropna().unique())

# ==========================================
# 9. 已跑好的 ANOVA 數據：可切換生活效能 / 問題解決能力
# ==========================================
st.markdown("---")
st.subheader("📈 已跑好的課程成效分析資料")

selected_anova_questionnaire = st.selectbox(
    "請選擇要查看的 ANOVA 問卷類型",
    ["生活效能", "問題解決能力"],
    key="anova_questionnaire_switch"
)

anova_show = anova_df[
    anova_df["問卷"] == selected_anova_questionnaire
].copy()

st.write("目前呈現：", selected_anova_questionnaire)

if len(anova_show) == 0:
    st.warning("目前沒有篩選到 ANOVA 資料，請確認 anova_df 的「問卷」欄位是否有生活效能或問題解決能力。")
    st.write("目前 anova_df 問卷類型：")
    st.write(anova_df["問卷"].dropna().unique())

else:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ANOVA 綜合雷達圖")

        radar_df = anova_show.copy()

        radar_df["F值"] = pd.to_numeric(radar_df["F值"], errors="coerce")
        radar_df["效果量"] = pd.to_numeric(radar_df["效果量"], errors="coerce")
        radar_df["p值"] = pd.to_numeric(radar_df["p值"], errors="coerce")

        def radar_significance_level(p):
            if pd.isna(p):
                return 0
            elif p < 0.001:
                return 3
            elif p < 0.01:
                return 2
            elif p < 0.05:
                return 1
            else:
                return 0

        def radar_minmax(series):
            if series.max() == series.min():
                return series * 0
            return (series - series.min()) / (series.max() - series.min())

        radar_df["顯著性等級"] = radar_df["p值"].apply(radar_significance_level)

        radar_df["F值_標準化"] = radar_minmax(radar_df["F值"])
        radar_df["效果量_標準化"] = radar_minmax(radar_df["效果量"])
        radar_df["顯著性等級_標準化"] = radar_df["顯著性等級"] / 3

        fig_radar = go.Figure()

        fig_radar.add_trace(
            go.Scatterpolar(
                r=radar_df["F值_標準化"],
                theta=radar_df["構面"],
                fill="toself",
                name="F值"
            )
        )

        fig_radar.add_trace(
            go.Scatterpolar(
                r=radar_df["效果量_標準化"],
                theta=radar_df["構面"],
                fill="toself",
                name="效果量"
            )
        )

        fig_radar.add_trace(
            go.Scatterpolar(
                r=radar_df["顯著性等級_標準化"],
                theta=radar_df["構面"],
                fill="toself",
                name="顯著性等級"
            )
        )

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title=f"{selected_anova_questionnaire}：ANOVA 綜合雷達圖",
            height=520
        )

        st.plotly_chart(fig_radar, use_container_width=True)

        with st.expander("查看雷達圖資料"):
            st.dataframe(
                radar_df[
                    [
                        "問卷",
                        "構面",
                        "F值",
                        "效果量",
                        "p值",
                        "顯著性",
                        "顯著性等級"
                    ]
                ],
                use_container_width=True
            )

    with col2:
        st.markdown("#### ANOVA 結果表")

        st.dataframe(
            anova_show[
                [
                    "問卷",
                    "構面",
                    "有效樣本數",
                    "F值",
                    "p值",
                    "效果量",
                    "顯著性"
                ]
            ],
            use_container_width=True
        )

    # ==========================================
    # 10. ANOVA 結果熱力圖
    # ==========================================
    st.markdown("---")
    st.subheader("🔥 ANOVA 結果熱力圖")

    st.markdown(
        """
        此熱力圖會依照上方選擇的問卷類型切換：
        可查看「生活效能」或「問題解決能力」各構面的 F值、效果量與顯著性等級。
        """
    )

    heatmap_df = anova_show.copy()

    heatmap_df["F值"] = pd.to_numeric(heatmap_df["F值"], errors="coerce")
    heatmap_df["p值"] = pd.to_numeric(heatmap_df["p值"], errors="coerce")
    heatmap_df["效果量"] = pd.to_numeric(heatmap_df["效果量"], errors="coerce")

    def significance_level(p):
        if pd.isna(p):
            return 0
        elif p < 0.001:
            return 3
        elif p < 0.01:
            return 2
        elif p < 0.05:
            return 1
        else:
            return 0

    def significance_label(p):
        if pd.isna(p):
            return "無資料"
        elif p < 0.001:
            return "p < .001"
        elif p < 0.01:
            return "p < .01"
        elif p < 0.05:
            return "p < .05"
        else:
            return "未顯著"

    def minmax(series):
        if series.max() == series.min():
            return series * 0
        return (series - series.min()) / (series.max() - series.min())

    heatmap_df["顯著性等級"] = heatmap_df["p值"].apply(significance_level)
    heatmap_df["顯著性標籤"] = heatmap_df["p值"].apply(significance_label)

    heatmap_df["F值_標準化"] = minmax(heatmap_df["F值"])
    heatmap_df["效果量_標準化"] = minmax(heatmap_df["效果量"])
    heatmap_df["顯著性等級_標準化"] = heatmap_df["顯著性等級"] / 3

    z_data = [
        heatmap_df["F值_標準化"].tolist(),
        heatmap_df["效果量_標準化"].tolist(),
        heatmap_df["顯著性等級_標準化"].tolist()
    ]

    y_labels = ["F值", "效果量", "顯著性等級"]
    x_labels = heatmap_df["構面"].tolist()

    text_data = [
        [f"F={v:.2f}" for v in heatmap_df["F值"]],
        [f"η²={v:.2f}" for v in heatmap_df["效果量"]],
        heatmap_df["顯著性標籤"].tolist()
    ]

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            text=text_data,
            texttemplate="%{text}",
            colorscale=heatmap_colors,
            colorbar=dict(title="相對強度"),
            hovertemplate="構面：%{x}<br>指標：%{y}<br>%{text}<extra></extra>"
        )
    )

    fig_heatmap.update_layout(
        title=f"{selected_anova_questionnaire} ANOVA 結果熱力圖",
        xaxis_title="構面",
        yaxis_title="統計指標",
        height=420
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    with st.expander("查看熱力圖判讀說明"):
        st.write("顯著性等級說明：")
        st.write("0：未顯著")
        st.write("1：p < .05")
        st.write("2：p < .01")
        st.write("3：p < .001")
        st.write("F值越高，代表前、中、後測差異越明顯。")
        st.write("效果量越高，代表課程影響程度越大。")
        st.write("雷達圖中的 F值、效果量、顯著性等級皆已標準化為 0～1，方便放在同一張圖中比較。")

# ==========================================
# 11. 各構面平均數折線圖：前、中、後測
# ==========================================
st.markdown("---")
st.subheader("📈 各構面前、中、後測平均數變化折線圖")

line_questionnaire = st.selectbox(
    "選擇折線圖問卷類型",
    ["生活效能", "問題解決能力"],
    key="line_questionnaire"
)

line_data = desc_df[
    desc_df["問卷"] == line_questionnaire
].copy()

stage_order = ["前測", "中測", "後測"]

line_data["測量階段"] = pd.Categorical(
    line_data["測量階段"],
    categories=stage_order,
    ordered=True
)

line_data = line_data.sort_values(
    ["構面", "測量階段"]
)

fig_line = px.line(
    line_data,
    x="測量階段",
    y="平均數",
    color="構面",
    markers=True,
    color_discrete_sequence=line_colors,
    title=f"{line_questionnaire}各構面前、中、後測平均數變化",
    text="平均數"
)

fig_line.update_traces(
    textposition="top center"
)

fig_line.update_layout(
    xaxis_title="測量階段",
    yaxis_title="平均數",
    legend_title="構面",
    yaxis=dict(range=[0, 5])
)

st.plotly_chart(fig_line, use_container_width=True)

with st.expander("查看折線圖資料表"):
    st.dataframe(
        line_data[
            [
                "問卷",
                "構面",
                "測量階段",
                "N",
                "平均數",
                "標準差"
            ]
        ].round(2),
        use_container_width=True
    )

# ==========================================
# 12. 單一構面折線圖：跟側邊欄連動
# ==========================================
st.markdown("---")
st.subheader("📉 側邊欄所選構面之前、中、後測平均數變化")

single_line_data = desc_df[
    (desc_df["問卷"] == selected_questionnaire) &
    (desc_df["構面"] == selected_dimension)
].copy()

single_line_data["測量階段"] = pd.Categorical(
    single_line_data["測量階段"],
    categories=stage_order,
    ordered=True
)

single_line_data = single_line_data.sort_values("測量階段")

fig_single_line = px.line(
    single_line_data,
    x="測量階段",
    y="平均數",
    markers=True,
    color_discrete_sequence=line_colors,
    title=f"{selected_questionnaire}－{selected_dimension}：前、中、後測平均數變化",
    text="平均數"
)

fig_single_line.update_traces(
    textposition="top center"
)

fig_single_line.update_layout(
    xaxis_title="測量階段",
    yaxis_title="平均數",
    yaxis=dict(range=[0, 5])
)

st.plotly_chart(fig_single_line, use_container_width=True)

st.dataframe(
    single_line_data[
        [
            "問卷",
            "構面",
            "測量階段",
            "N",
            "平均數",
            "標準差"
        ]
    ].round(2),
    use_container_width=True
)

# ==========================================
# 13. 頁尾說明
# ==========================================
st.markdown("---")
st.subheader("📝 圖表閱讀說明")

st.write("1. 側邊欄選擇「基本結構分布、問卷類型、構面、測量階段」後，右側圖表與表格會同步更新。")
st.write("2. 側邊欄可選擇圖表顏色主題，圓餅圖、雷達圖、熱力圖與折線圖會同步變更顏色。")
st.write("3. t 檢定資料用於呈現不同背景變項學生在各構面上的差異。")
st.write("4. ANOVA 資料用於呈現戶外冒險課程前、中、後測是否達顯著差異。")
st.write("5. ANOVA 綜合雷達圖將 F值、效果量、顯著性等級標準化為 0～1，方便同圖比較。")
st.write("6. ANOVA 熱力圖可透過下拉選單切換生活效能與問題解決能力。")
st.write("7. 折線圖用於呈現生活效能與問題解決能力各構面之前、中、後測平均數變化。")
st.write("8. 畫面顯示已將「一年以下」改為「未滿一年」，但程式仍可自動判斷原始欄位名稱。")

st.success("🎉 戶外冒險教育動態資料視覺化 Dashboard 已完成！")