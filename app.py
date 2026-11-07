"""交渉準備シート（BATNA・留保点・目標点・相手の利害）を整理する Streamlit アプリ

実行方法:  streamlit run app.py
"""

from datetime import date

import streamlit as st

st.set_page_config(page_title="交渉準備シート", page_icon="🤝", layout="wide")

st.title("🤝 交渉準備シート")
st.caption("左側のフォームに入力して「サマリーを作成」を押すと、右側に整理された結果が表示されます。")


def lines(text: str) -> list[str]:
    """改行区切りのテキストを、空行を除いたリストにする"""
    return [t.strip(" ・-*") for t in text.splitlines() if t.strip()]


def bullet(items: list[str], empty: str = "（未入力）") -> str:
    return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"


def fmt(v: float, unit: str) -> str:
    return f"{v:,.0f} {unit}".strip() if float(v).is_integer() else f"{v:,.2f} {unit}".strip()


left, right = st.columns([1, 1], gap="large")

# ------------------------------------------------------------------ 入力
with left:
    with st.form("sheet"):
        st.subheader("① 基本情報")
        title = st.text_input("交渉のテーマ", placeholder="例：中古車の売却価格")
        counterpart = st.text_input("相手", placeholder="例：買取業者A社")
        neg_date = st.date_input("交渉日", value=date.today())

        st.subheader("② 自分の立場")
        role = st.radio(
            "数値は高い方と低い方、どちらが自分に有利？",
            ["高いほど有利（売る側・給与交渉など）", "低いほど有利（買う側・コスト交渉など）"],
        )
        unit = st.text_input("単位", value="万円")

        st.subheader("③ 自分の BATNA（交渉が決裂した場合の最善の代替案）")
        batna = st.text_area("BATNA の内容", placeholder="例：B社に80万円で売る（見積済み）")
        batna_value = st.number_input("BATNA を数値にすると？", value=80.0, step=1.0)

        st.subheader("④ 留保点と目標点")
        reservation = st.number_input(
            "留保点（これ以上譲れない限界ライン）", value=85.0, step=1.0,
            help="これより悪い条件なら、合意せず BATNA を選ぶライン",
        )
        target = st.number_input(
            "目標点（狙いたい理想的な条件）", value=110.0, step=1.0,
            help="野心的だが根拠を説明できるライン",
        )
        my_interests = st.text_area(
            "自分の利害（本当に大事なこと・1行に1つ）",
            placeholder="例：\n今月中に現金化したい\n手続きを楽に済ませたい",
        )

        st.subheader("⑤ 相手の利害（推測）")
        their_interests = st.text_area(
            "相手が大事にしていそうなこと（1行に1つ）",
            placeholder="例：\n在庫を早く確保したい\n整備費用を抑えたい",
        )
        their_batna = st.text_area("相手の BATNA（推測）", placeholder="例：オークションで同型車を仕入れる")
        know_their_res = st.checkbox("相手の留保点を数値で推測できる")
        their_reservation = st.number_input("相手の留保点（推測）", value=100.0, step=1.0)

        st.subheader("⑥ その他")
        options = st.text_area(
            "双方の利害を満たす選択肢のアイデア（1行に1つ）",
            placeholder="例：\n即日引き渡しの代わりに価格を上乗せ\n付属品をセットにする",
        )
        notes = st.text_area("メモ・懸念点")

        submitted = st.form_submit_button("サマリーを作成", type="primary", width="stretch")

# ------------------------------------------------------------------ サマリー
with right:
    if not submitted:
        st.info("👈 入力が終わったら「サマリーを作成」を押してください。")
        st.stop()

    higher_better = role.startswith("高い")

    def better(a: float, b: float) -> bool:
        """a が b より自分にとって有利か"""
        return a > b if higher_better else a < b

    st.subheader(f"📋 {title or '（テーマ未入力）'}")
    st.write(f"**相手:** {counterpart or '（未入力）'}　／　**交渉日:** {neg_date:%Y年%m月%d日}")

    # 主要数値
    c1, c2, c3 = st.columns(3)
    c1.metric("BATNA", fmt(batna_value, unit))
    c2.metric("留保点", fmt(reservation, unit))
    c3.metric("目標点", fmt(target, unit))

    # 整合性チェック
    st.markdown("#### ✅ チェック")
    warnings = []
    if not better(target, reservation):
        warnings.append("目標点が留保点より有利になっていません。目標点をもっと野心的に設定しましょう。")
    if better(batna_value, reservation):
        warnings.append("BATNA の方が留保点より有利です。留保点は少なくとも BATNA と同等以上に設定するのが基本です。")
    if not batna.strip():
        warnings.append("BATNA の内容が未入力です。決裂時の選択肢がないと、交渉で弱い立場になります。")
    if not lines(their_interests):
        warnings.append("相手の利害が未入力です。相手が「なぜ」それを求めるのかを考えてみましょう。")

    if warnings:
        for w in warnings:
            st.warning(w)
    else:
        st.success("基本的な整合性は取れています。")

    # ZOPA
    zopa_text = "相手の留保点が未入力のため、ZOPA（合意可能領域）は判定していません。"
    if know_their_res:
        st.markdown("#### 📏 ZOPA（合意可能領域）")
        if better(their_reservation, reservation) or their_reservation == reservation:
            lo, hi = sorted([reservation, their_reservation])
            zopa_text = f"ZOPA あり：{fmt(lo, unit)} 〜 {fmt(hi, unit)}（幅 {fmt(hi - lo, unit)}）"
            st.success(zopa_text)
            if better(target, their_reservation):
                st.caption("※ 目標点は相手の推定留保点を超えています。強気な提示の根拠を準備しておきましょう。")
        else:
            zopa_text = "ZOPA なし：相手の推定留保点が自分の留保点に届いていません。"
            st.error(zopa_text + " 価格以外の条件（選択肢）を工夫するか、BATNA の行使を検討しましょう。")

    # 利害
    st.markdown("#### 🎯 利害の整理")
    i1, i2 = st.columns(2)
    with i1:
        st.markdown("**自分の利害**")
        st.markdown(bullet(lines(my_interests)))
    with i2:
        st.markdown("**相手の利害（推測）**")
        st.markdown(bullet(lines(their_interests)))
    st.markdown("**相手の BATNA（推測）**")
    st.markdown(bullet(lines(their_batna)))
    st.markdown("**選択肢のアイデア**")
    st.markdown(bullet(lines(options)))
    if notes.strip():
        st.markdown("**メモ・懸念点**")
        st.markdown(notes)

    # ダウンロード用 Markdown
    md = f"""# 交渉準備シート：{title or '（テーマ未入力）'}

- 相手：{counterpart or '（未入力）'}
- 交渉日：{neg_date:%Y年%m月%d日}
- 有利な方向：{role}

## 数値
| 項目 | 値 |
|---|---|
| BATNA | {fmt(batna_value, unit)} |
| 留保点 | {fmt(reservation, unit)} |
| 目標点 | {fmt(target, unit)} |
| 相手の留保点（推測） | {fmt(their_reservation, unit) if know_their_res else '未入力'} |

{zopa_text}

## 自分の BATNA
{bullet(lines(batna))}

## 自分の利害
{bullet(lines(my_interests))}

## 相手の利害（推測）
{bullet(lines(their_interests))}

## 相手の BATNA（推測）
{bullet(lines(their_batna))}

## 選択肢のアイデア
{bullet(lines(options))}

## チェック結果
{bullet(warnings, empty='問題なし')}

## メモ
{notes or '（なし）'}
"""
    st.download_button(
        "📥 サマリーを Markdown で保存", md,
        file_name=f"交渉準備_{neg_date:%Y%m%d}.md", mime="text/markdown",
        width="stretch",
    )
