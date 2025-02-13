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

# Matplotlib のデフォルトフォントを変更
mpl.rcParams['font.family'] = font_prop.get_name()


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

        # 初心者向け説明の表示切り替え
        if "show_explanation" not in st.session_state:
           st.session_state.show_explanation = False
        # ボタンを押すたびにセッションステートを切り替える
        if st.button("初心者向け説明を表示/非表示"):
           st.session_state.show_explanation = not st.session_state.show_explanation

         # セッションステートに基づいて説明を表示
        if st.session_state.show_explanation:
           st.markdown("""
           ##この検定は、2つのグループのデータ（例えば「A群」と「B群」）に違いがあるかを調べる方法です。**
    
           - **p値とは？**
            -  p値は「偶然このような結果が出る確率」を表します。
              一般的に p値が0.05未満（5%未満） の場合、「2つのグループの間に違いがある」と考えます。
            -  p値が0.05以上 なら、「データに明確な差があるとは言えない」ということになります。
           - **結果の解釈**
            - p値が0.05未満（有意差あり）
              → 「2つのグループの値は統計的に異なる」と言えます。例えば、「新しい治療を受けたグループの方が回復が早かった」といった結果が示される可能性があります。
            - p値が0.05以上（有意差なし）
              → 「2つのグループに明確な差は見られない」と言えます。例えば、「薬を飲んだグループと飲まなかったグループで症状の改善度合いに違いはない」といった結論になります。""")
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
             st.success("✅ 2群間には統計的に有意な差があります。「2つのグループの間に違いがある」")
             st.write("p値が0.05未満のため、2つのグループの値に違いがあると考えられます。つまり、AとBの間に統計的に有意な差がある可能性が高いです。")
            else:
             st.info("❌ 2群間に統計的な有意差は見られません。「2つのグループの値は統計的に異なる」")
             st.write("p値が0.05以上のため、2つのグループの値に明確な違いがあるとは言えません。サンプル数が少ない場合や、データのばらつきが大きい場合はこのような結果になることがあります。")
            
            # データの分布を可視化（例：マン・ホイットニーU検定）
            fig, ax = plt.subplots()
            sns.histplot(df, x=value_col, hue=group_col, kde=True, ax=ax)
            ax.set_title("データの分布", fontproperties=font_prop)
            ax.set_xlabel(value_col, fontproperties=font_prop)
            ax.set_ylabel("頻度", fontproperties=font_prop)
            st.pyplot(fig)


    
    elif test_type == "3群以上の比較（クラスカル・ウォリス検定）":
        group_col = st.sidebar.selectbox("グループ列を選択", columns)
        value_col = st.sidebar.selectbox("値の列を選択", [col for col in columns if col != group_col])
        
        groups = [df[df[group_col] == g][value_col] for g in df[group_col].unique()]
        stat, p = stats.kruskal(*groups)

        # 初心者向け説明の表示切り替え
        if "show_explanation" not in st.session_state:
           st.session_state.show_explanation = False
        # ボタンを押すたびにセッションステートを切り替える
        if st.button("初心者向け説明を表示/非表示"):
           st.session_state.show_explanation = not st.session_state.show_explanation

         # セッションステートに基づいて説明を表示
        if st.session_state.show_explanation:
           st.markdown("""
           ##この検定は、「3つ以上のグループ」に違いがあるかを調べる方法です。（例えば「A群」「B群」「C群」の3グループを比較する場合）**
    
           - **p値の意味**
            -  こちらもp値が0.05未満なら「少なくとも1つのグループが他と異なる」と言えます。
               逆にp値が0.05以上なら、「グループ間に明確な違いは見られない」ということになります。
           - **結果の解釈**
            - p値が0.05未満（有意差あり）
              → 「3つ以上のグループのうち、少なくとも1つは他と異なる」という結果になります。例えば、「A群は成績が良かったが、B群とC群はほぼ同じだった」などの可能性があります。
            - p値が0.05以上（有意差なし）
              → 「すべてのグループにおいて、統計的に大きな違いはない」と言えます。例えば、「異なる教育法を試した3つのクラスで、成績の平均に大きな違いはなかった」といった結論になります。""")
        st.write(f"### クラスカル・ウォリス検定の結果")
        st.write(f"H統計量: {stat:.4f}")
        st.write(f"p値: {p:.4f}")
        
        if p < 0.05:
            st.success("✅ 3群以上の間で統計的に有意な差があります。")
        else:
            st.info("❌ 3群以上の間で統計的な有意差は見られません。")
        
        # データの分布を可視化（クラスカル・ウォリス検定）
            fig, ax = plt.subplots()
            sns.boxplot(x=group_col, y=value_col, data=df, ax=ax)
            ax.set_title("データの分布", fontproperties=font_prop)
            ax.set_xlabel(group_col, fontproperties=font_prop)
            ax.set_ylabel(value_col, fontproperties=font_prop)
            st.pyplot(fig)



    
    elif test_type == "同じ生徒の前後比較（ウィルコクソン符号付順位検定）":
        before_col = st.sidebar.selectbox("前の値の列を選択", columns)
        after_col = st.sidebar.selectbox("後の値の列を選択", [col for col in columns if col != before_col])
        
        stat, p = stats.wilcoxon(df[before_col], df[after_col])

        # 初心者向け説明の表示切り替え
        if "show_explanation" not in st.session_state:
           st.session_state.show_explanation = False

        # ボタンを押すたびにセッションステートを切り替える
        if st.button("初心者向け説明を表示/非表示"):
           st.session_state.show_explanation = not st.session_state.show_explanation
            # セッションステートに基づいて説明を表示
        st.markdown("""
           ##この検定は、「同じ人が前後でどう変化したか」を調べる方法です。（例えば、「治療前の血圧」と「治療後の血圧」の比較）**
    
           - **p値の意味**
            -  他の検定と同じく、p値が0.05未満なら「前後で変化があった」と言えます。
               p値が0.05以上なら、「前後での変化は偶然の範囲内かもしれない」ということになります。
           - **結果の解釈**
            - p値が0.05未満（有意差あり）
              → 「治療やトレーニングなどの介入の影響で、値が変化した可能性が高い」と言えます。例えば、「運動プログラムの前後で体重が明らかに減った」という結果になるかもしれません。
            - p値が0.05以上（有意差なし）
              → 「前後での変化が統計的に明確ではない」と言えます。例えば、「新しい薬を試したが、血圧に有意な変化は見られなかった」といった結論になります。""")
        st.write(f"### ウィルコクソン符号付順位検定の結果")
        st.write(f"W統計量: {stat:.4f}")
        st.write(f"p値: {p:.4f}")
        
        if p < 0.05:
            st.success("✅ 前後のデータ間に統計的に有意な差があります。")
        else:
            st.info("❌ 前後のデータ間に統計的な有意差は見られません。")
