import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
import matplotlib.font_manager as fm

# サーバー環境用のフォント設定
server_font_path = "/tmp/ipaexg.ttf"
local_font_path = "ipaexg.ttf"  # フォントファイルをアプリフォルダに同梱
if not os.path.exists(server_font_path):
    shutil.copy(local_font_path, server_font_path)
font_prop = fm.FontProperties(fname=server_font_path)

st.title("ノンパラメトリック統計 Web アプリ")


# CSVテンプレートのダウンロード
templates = {
    "2群比較（マン・ホイットニーU検定）": "グループ,値\nA,23\nA,45\nA,67\nB,34\nB,56\nB,78\n",
    "3群以上の比較（クラスカル・ウォリス検定）": "グループ,値\nA,12\nA,14\nA,16\nB,18\nB,20\nB,22\nC,24\nC,26\nC,28\n",
    "同じ生徒の前後比較（ウィルコクソン符号付順位検定）": "被験者,前,後\n1,100,105\n2,98,97\n3,102,110\n4,95,92\n"
}

for name, data in templates.items():
    st.download_button(f"{name} のCSVテンプレートをダウンロード", data=data.encode('utf-8-sig'), file_name=f"{name}.csv", mime="text/csv")

# CSVファイルのアップロード
st.sidebar.header("データのアップロード")
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロード", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### アップロードされたデータ")
    st.dataframe(df.head())
    
    # データの列選択
    columns = df.columns.tolist()
    test_type = st.sidebar.selectbox("実施する検定の種類を選択", ["2群比較（マン・ホイットニーU検定）", "3群以上の比較（クラスカル・ウォリス検定）", "同じ生徒の前後比較（ウィルコクソン符号付順位検定）"])
    
    if test_type == "2群比較（マン・ホイットニーU検定）":
        group_col = st.sidebar.selectbox("グループ列を選択", columns)
        value_col = st.sidebar.selectbox("値の列を選択", [col for col in columns if col != group_col])
        
        groups = df[group_col].unique()
        if len(groups) != 2:
            st.error("エラー: グループはちょうど2種類必要です。")
        else:
            group1 = df[df[group_col] == groups[0]][value_col]
            group2 = df[df[group_col] == groups[1]][value_col]
            stat, p = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            
            st.write(f"### マン・ホイットニーU検定の結果")
            st.write(f"U統計量: {stat:.4f}")
            st.write(f"p値: {p:.4f}")
            
            if p < 0.05:
                st.success("✅ 2群間には統計的に有意な差があります。")
            else:
                st.info("❌ 2群間に統計的な有意差は見られません。")
            
            # データの分布を可視化
            fig, ax = plt.subplots()
            sns.histplot(df, x=value_col, hue=group_col, kde=True, ax=ax)
            ax.set_title("データの分布")
            st.pyplot(fig)
    
    elif test_type == "3群以上の比較（クラスカル・ウォリス検定）":
        group_col = st.sidebar.selectbox("グループ列を選択", columns)
        value_col = st.sidebar.selectbox("値の列を選択", [col for col in columns if col != group_col])
        
        groups = [df[df[group_col] == g][value_col] for g in df[group_col].unique()]
        stat, p = stats.kruskal(*groups)
        
        st.write(f"### クラスカル・ウォリス検定の結果")
        st.write(f"H統計量: {stat:.4f}")
        st.write(f"p値: {p:.4f}")
        
        if p < 0.05:
            st.success("✅ 3群以上の間で統計的に有意な差があります。")
        else:
            st.info("❌ 3群以上の間で統計的な有意差は見られません。")
        
        # データの分布を可視化（マン・ホイットニーU検定）
        fig, ax = plt.subplots()
        sns.histplot(df, x=value_col, hue=group_col, kde=True, ax=ax)
        ax.set_title("データの分布", fontproperties=font_prop)  # ← フォント適用
        st.pyplot(fig)

    
    elif test_type == "同じ生徒の前後比較（ウィルコクソン符号付順位検定）":
        before_col = st.sidebar.selectbox("前の値の列を選択", columns)
        after_col = st.sidebar.selectbox("後の値の列を選択", [col for col in columns if col != before_col])
        
        stat, p = stats.wilcoxon(df[before_col], df[after_col])
        
        st.write(f"### ウィルコクソン符号付順位検定の結果")
        st.write(f"W統計量: {stat:.4f}")
        st.write(f"p値: {p:.4f}")
        
        if p < 0.05:
            st.success("✅ 前後のデータ間に統計的に有意な差があります。")
        else:
            st.info("❌ 前後のデータ間に統計的な有意差は見られません。")
