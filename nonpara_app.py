import streamlit as st
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shutil
import matplotlib.font_manager as fm
from io import BytesIO

# サーバー環境用のフォント設定
server_font_path = "/tmp/ipaexg.ttf"
local_font_path = "ipaexg.ttf"  # フォントファイルをアプリフォルダに同梱
if not os.path.exists(server_font_path):
    shutil.copy(local_font_path, server_font_path)
font_prop = fm.FontProperties(fname=server_font_path)

st.title("ノンパラメトリック統計 Web アプリ")

# 検定の種類
TEST_OPTIONS = {
    "2群（マン・ホイットニーU検定）": "mannwhitneyu",
    "3群以上（クラスカル・ウォリス検定）": "kruskal",
    "同じ対象の前後比較（ウィルコクソン符号付順位検定）": "wilcoxon"
}

def perform_test(test_type, df, group_col, value_col):
    result_text = ""
    
    if test_type == "mannwhitneyu":
        groups = df[group_col].unique()
        if len(groups) != 2:
            st.error("エラー: 2群のデータが必要です。")
            return None
        group1 = df[df[group_col] == groups[0]][value_col]
        group2 = df[df[group_col] == groups[1]][value_col]
        stat, p = stats.mannwhitneyu(group1, group2)
        result_text = f"マン・ホイットニーU検定: 統計量={stat:.4f}, p値={p:.4f}"
    
    elif test_type == "kruskal":
        groups = [df[df[group_col] == g][value_col] for g in df[group_col].unique()]
        stat, p = stats.kruskal(*groups)
        result_text = f"クラスカル・ウォリス検定: 統計量={stat:.4f}, p値={p:.4f}"
    
    elif test_type == "wilcoxon":
        before = df[df[group_col] == "Before"][value_col]
        after = df[df[group_col] == "After"][value_col]
        if len(before) != len(after):
            st.error("エラー: 'Before' と 'After' のデータ数が一致しません。")
            return None
        stat, p = stats.wilcoxon(before, after)
        result_text = f"ウィルコクソン検定: 統計量={stat:.4f}, p値={p:.4f}"
    
    return result_text, p

# CSVテンプレートのダウンロード機能
def get_csv_template(test_type):
    if test_type == "mannwhitneyu":
        df = pd.DataFrame({"Group": ["A", "A", "B", "B"], "Value": [10, 20, 15, 25]})
    elif test_type == "kruskal":
        df = pd.DataFrame({"Group": ["A", "A", "B", "B", "C", "C"], "Value": [10, 20, 15, 25, 30, 35]})
    elif test_type == "wilcoxon":
        df = pd.DataFrame({"Time": ["Before", "Before", "After", "After"], "Value": [10, 20, 15, 25]})
    else:
        return None
    
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    return BytesIO(csv.encode('utf-8-sig'))

st.sidebar.header("データのアップロード")
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロード", type=["csv"])
test_type_label = st.sidebar.selectbox("適用する検定を選択", list(TEST_OPTIONS.keys()))
test_type = TEST_OPTIONS[test_type_label]

# CSVテンプレートのダウンロード
csv_template = get_csv_template(test_type)
if csv_template:
    st.sidebar.download_button(
        label="CSVテンプレートをダウンロード",
        data=csv_template,
        file_name="template.csv",
        mime="text/csv"
    )

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    st.write("### アップロードされたデータ")
    st.dataframe(df.head())
    
    group_col = st.sidebar.selectbox("グループを示す列を選択", df.columns)
    value_col = st.sidebar.selectbox("数値データの列を選択", df.columns)
    
    if st.sidebar.button("検定を実行"):
        result = perform_test(test_type, df, group_col, value_col)
        if result:
            result_text, p_value = result
            st.write("### 検定結果")
            st.write(result_text)
            
            if p_value < 0.05:
                st.write("**統計的に有意な差がある可能性があります（p < 0.05）**")
            else:
                st.write("**統計的に有意な差は見られませんでした（p >= 0.05）**")
            
            # データの分布を可視化
            st.write("### データの分布")
            fig, ax = plt.subplots()
            sns.histplot(df, x=value_col, hue=group_col, kde=True, ax=ax)
            ax.set_title("データの分布", fontproperties=font_prop)
            st.pyplot(fig)
