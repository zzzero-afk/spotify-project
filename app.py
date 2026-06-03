import streamlit as st
import pandas as pd
import random

# ── 頁面設定 ──────────────────────────────────────────────
st.set_page_config(page_title="更隨機的隨機播放 🎲", layout="centered")
st.title("🎵 更隨機的隨機播放")
st.caption("打破聚類偏誤，聆聽真正的驚喜")

# ── 欄位名稱設定（若 CSV 欄位名稱不同，只需修改這裡）──────
COL_TRACK  = "track_name"    # 歌名欄位
COL_ARTIST = "artist_name"   # 歌手欄位
COL_GENRE  = "artist_genres"         # 曲風欄位

# ── 讀取資料 ──────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    # 1. 自動獲取當前 app.py 所在的資料夾絕對路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. 把資料夾路徑與檔名完美結合，確保程式永遠不會迷路
    file_path = os.path.join(current_dir, "spotify_data.csv")
    
    # 3. 讀取絕對路徑，並加上編碼防護盾，徹底解決 Excel 污染問題
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    return df

df = load_data()

# ── Hashtag → 關鍵字映射表────────────
HASHTAG_MAP = {
    "#Pop":         ["pop"],
    "#Rock":        ["rock", "metal", "punk", "alternative"],
    "#Dance":       ["dance", "edm", "electronic", "house", "techno"],
    "#HipHop":      ["hip hop", "hip-hop", "rap", "trap"],
    "#R&B":         ["r&b", "soul", "rnb"],
    "#Latin":       ["latin", "reggaeton", "salsa", "cumbia"],
    "#Jazz":        ["jazz", "blues"],
    "#Classical":   ["classical", "orchestra", "instrumental"],
    "#Country":     ["country", "folk", "bluegrass"],
    "#Indie":       ["indie", "lo-fi", "bedroom pop"],
    "#Afro":        ["afro", "Amapiano"]
}

# ── 操作面板（已移至主畫面中央） ────────────────────────────
st.markdown("### 🎛️ 開始訂製")
chosen_tag = st.selectbox("請選擇曲風", list(HASHTAG_MAP.keys()))

# 讓拉桿和按鈕並排，畫面比較好看
col_slider, col_btn = st.columns([3, 1])
with col_slider:
    playlist_size = st.slider("請選擇數量", min_value=5, max_value=30, value=10)
with col_btn:
    st.write("") # 稍微推開一點空間對齊
    st.write("") 
    generate_btn = st.button("✨ GO!", use_container_width=True)

# ── 核心函式 ──────────────────────────────────────────────
def get_unique_artist_pool(dataframe, keywords):
    """用關鍵字過濾 genre，並對歌手去重，每位歌手只保留一首歌"""
    pattern = "|".join(keywords)
    mask = dataframe[COL_GENRE].str.contains(pattern, case=False, na=False)
    filtered = dataframe[mask]
    
    # ⚡ 破解 Excel 固定順序的關鍵：在去重前，先將撈出來的歌曲大洗牌！
    filtered_shuffled = filtered.sample(frac=1, random_state=random.randint(0, 9999)).reset_index(drop=True)
    
    # 洗牌後再留第一首，這樣每次留下來的代表作就絕對不一樣了！
    return filtered_shuffled.drop_duplicates(subset=[COL_ARTIST])

def build_surprise_playlist(df, tag, total):
    """80/20 法則：80% 主題曲 + 20% 跨領域驚喜曲"""
    keywords = HASHTAG_MAP[tag]

    main_pool = get_unique_artist_pool(df, keywords)

    other_keywords = []
    for t, kws in HASHTAG_MAP.items():
        if t != tag:
            other_keywords.extend(kws)
    surprise_pool = get_unique_artist_pool(df, other_keywords)

    n_main     = max(1, round(total * 0.8))
    n_surprise = max(1, total - n_main)

    n_main     = min(n_main, len(main_pool))
    n_surprise = min(n_surprise, len(surprise_pool))

    sampled_main     = main_pool.sample(n=n_main, random_state=random.randint(0, 9999))
    sampled_surprise = surprise_pool.sample(n=n_surprise, random_state=random.randint(0, 9999))

    playlist = pd.concat([sampled_main, sampled_surprise]).sample(frac=1).reset_index(drop=True)
    playlist.index += 1
    return playlist, n_main, n_surprise

# ── 主介面輸出 ─────────────────────────────────────────────
if generate_btn:
    with st.spinner("系統正在計算特徵距離並過濾重複歌手..."):
        try:
            playlist, n_main, n_surprise = build_surprise_playlist(df, chosen_tag, playlist_size)

            st.success(f"🎉 專屬探索歌單已成功生成！共挑選 {len(playlist)} 首歌曲")

            # 統計資訊
            col1, col2, col3 = st.columns(3)
            col1.metric("🎯 主題曲", f"{n_main} 首", chosen_tag)
            col2.metric("🎲 驚喜曲", f"{n_surprise} 首", "跨領域隨機")
            col3.metric("👤 歌手", f"{len(playlist)} 位", "每人僅一首")

            st.divider()
            st.subheader("🎼 專屬驚喜歌單")

            # ── 這裡改用精美的條列式呈現：歌名加粗、留下歌手、不顯示曲風 ──
            for index, row in playlist.iterrows():
                # **文字** 在網頁裡代表加粗
                st.markdown(f"{index}. **{row[COL_TRACK]}** — *{row[COL_ARTIST]}*")

        except ValueError as e:
            st.error(f"資料量不足，請嘗試減少歌單數量或換一個 Hashtag。\n\n錯誤：{e}")

else:
    # 預設說明畫面
    st.info("選擇偏好 Hashtag，再點擊按鈕生成！")

    with st.sidebar.expander("💡 有什麼特別之處？", expanded=True):
        st.markdown("""
        | 隨機播放 | 更隨機的隨機播放 |
        |---|---|
        | 同歌手可能連續出現 | 每位歌手僅出現一次 |
        | 只播你選的類型 | 80%主題+20%驚喜 |
        | 有聚類偏誤 | 去重後真隨機取樣 |
        """)
        
    with st.sidebar.expander("### 📊 數據來源與素材", expanded=True):
        st.markdown("""
        - **平台**：Kaggle 
        - **資料集名稱**：*Spotify Global Music Dataset (2009-2025)*
        - **資料貢獻者**：Warda Bilal
        - **數據評分 (Usability)**：10.0 🔥 Gold
        """)