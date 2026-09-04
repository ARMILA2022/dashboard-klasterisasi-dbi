
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="Dashboard Klasterisasi DBI Sumatera Barat",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# JUDUL
# ============================================================

st.title("📊 Dashboard Klasterisasi Sosial Ekonomi")
st.subheader(
    "Provinsi Sumatera Barat Menggunakan K-Means "
    "dan Davies-Bouldin Index (DBI)"
)

st.markdown(
    """
    Dashboard ini menyajikan hasil klasterisasi 19 kabupaten/kota
    di Provinsi Sumatera Barat berdasarkan 9 indikator sosial ekonomi
    menggunakan algoritma K-Means.
    """
)

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_excel("data_dashboard_dbi.xlsx")

    centroid = pd.read_excel(
        "centroid_cluster_dbi.xlsx"
    )

    with open(
        "hasil_cluster_peta_dbi.geojson",
        "r",
        encoding="utf-8"
    ) as f:
        peta = json.load(f)

    return data, centroid, peta


data, centroid, peta = load_data()

# ============================================================
# INFORMASI HASIL DBI
# ============================================================

k_optimal = 3
dbi_terbaik = 0.6041

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📌 Menu")

menu = st.sidebar.radio(
    "Pilih halaman:",
    [
        "Beranda",
        "Hasil Clustering",
        "Peta Clustering",
        "Centroid"
    ]
)

# ============================================================
# BERANDA
# ============================================================

if menu == "Beranda":

    st.header("Ringkasan Hasil Clustering")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Kabupaten/Kota",
            "19"
        )

    with col2:
        st.metric(
            "K Optimal",
            "3"
        )

    with col3:
        st.metric(
            "Nilai DBI",
            "0.6041"
        )

    with col4:
        st.metric(
            "Indikator",
            "9"
        )

    st.divider()

    st.write("### Distribusi Anggota Cluster")

    jumlah_cluster = (
        data["Cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    jumlah_cluster.columns = [
        "Cluster",
        "Jumlah Anggota"
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.dataframe(
            jumlah_cluster,
            use_container_width=True,
            hide_index=True
        )

    with col2:

        fig = px.bar(
            jumlah_cluster,
            x="Cluster",
            y="Jumlah Anggota",
            text="Jumlah Anggota",
            title="Jumlah Kabupaten/Kota per Cluster"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ============================================================
# HASIL CLUSTERING
# ============================================================

elif menu == "Hasil Clustering":

    st.header("📋 Hasil Clustering")

    st.write(
        "Hasil pengelompokan kabupaten/kota berdasarkan "
        "K-Means dengan K optimal = 3."
    )

    cluster_pilih = st.selectbox(
        "Pilih Cluster:",
        sorted(data["Cluster"].unique())
    )

    data_cluster = data[
        data["Cluster"] == cluster_pilih
    ]

    st.write(
        f"### Anggota Cluster {cluster_pilih}"
    )

    st.dataframe(
        data_cluster,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# ============================================================
# PETA CLUSTERING
# ============================================================

elif menu == "Peta Clustering":

    st.header("🗺️ Peta Hasil Clustering")

    st.write(
        "Peta menunjukkan distribusi cluster kabupaten/kota "
        "di Provinsi Sumatera Barat."
    )

    # Membuat DataFrame dari data clustering
    data_peta = data[
        ["Kabupaten/Kota", "Cluster"]
    ].copy()

    data_peta["Cluster"] = data_peta["Cluster"].astype(int)

    # Gabungkan informasi cluster ke setiap wilayah GeoJSON
    for feature in peta["features"]:

        nama_wilayah = feature["properties"].get("nama")

        # Menyesuaikan nama Kota Sawahlunto
        if nama_wilayah == "Kota Sawahlunto":
            nama_cari = "Kota Sawah Lunto"
        else:
            nama_cari = nama_wilayah

        hasil = data_peta[
            data_peta["Kabupaten/Kota"] == nama_cari
        ]

        if not hasil.empty:
            feature["properties"]["Cluster"] = int(
                hasil.iloc[0]["Cluster"]
            )
        else:
            feature["properties"]["Cluster"] = 0

    # Membuat peta
   fig = px.choropleth_map(
    data_peta,
    geojson=peta,
    locations="Kabupaten/Kota",
    featureidkey="properties.nama",
    color="Cluster",
    hover_name="Kabupaten/Kota",
    map_style="carto-positron",
    center={
        "lat": -0.7399,
        "lon": 100.8000
    },
    zoom=6,
    opacity=0.7
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )
# ============================================================
# CENTROID
# ============================================================

elif menu == "Centroid":

    st.header("🎯 Centroid Setiap Cluster")

    st.write(
        "Nilai centroid menunjukkan rata-rata nilai "
        "9 indikator pada masing-masing cluster."
    )

    st.dataframe(
        centroid,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Centroid digunakan untuk melihat karakteristik "
        "masing-masing cluster."
    )
