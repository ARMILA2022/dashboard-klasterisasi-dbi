import streamlit as st
import pandas as pd
import plotly.express as px
import json


# ============================================================
# KONFIGURASI
# ============================================================

st.set_page_config(
    page_title="Dashboard Klasterisasi Sosial Ekonomi",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# MEMBACA DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_excel(
        "data_dashboard_dbi.xlsx"
    )

    centroid = pd.read_excel(
        "centroid_cluster_dbi.xlsx"
    )

    hasil_dbi = pd.read_excel(
        "hasil_dbi.xlsx"
    )

    with open(
        "hasil_cluster_peta_dbi.geojson",
        "r",
        encoding="utf-8"
    ) as file:
        peta = json.load(file)

    return data, centroid, hasil_dbi, peta


# ============================================================
# LOAD DATA
# ============================================================

try:

    data, centroid, hasil_dbi, peta = load_data()

except Exception as e:

    st.error("Data dashboard gagal dibaca.")

    st.write(
        "Pastikan semua file berada dalam repository "
        "GitHub yang sama dengan app.py."
    )

    st.code(str(e))

    st.stop()


# ============================================================
# VALIDASI DATA DBI
# ============================================================

if "K" not in hasil_dbi.columns:

    st.error(
        "Kolom 'K' tidak ditemukan dalam hasil_dbi.xlsx."
    )

    st.write(
        "Kolom yang tersedia:"
    )

    st.write(
        list(hasil_dbi.columns)
    )

    st.stop()


if "DBI" not in hasil_dbi.columns:

    st.error(
        "Kolom 'DBI' tidak ditemukan dalam hasil_dbi.xlsx."
    )

    st.write(
        "Kolom yang tersedia:"
    )

    st.write(
        list(hasil_dbi.columns)
    )

    st.stop()


# ============================================================
# MEMBERSIHKAN DATA DBI
# ============================================================

hasil_dbi["K"] = pd.to_numeric(
    hasil_dbi["K"],
    errors="coerce"
)

hasil_dbi["DBI"] = pd.to_numeric(
    hasil_dbi["DBI"],
    errors="coerce"
)

hasil_dbi = hasil_dbi.dropna(
    subset=["K", "DBI"]
)

hasil_dbi = hasil_dbi.sort_values(
    "K"
).reset_index(drop=True)


# ============================================================
# MENENTUKAN K OPTIMAL
# ============================================================

index_terbaik = hasil_dbi["DBI"].idxmin()

k_optimal = int(
    hasil_dbi.loc[index_terbaik, "K"]
)

dbi_terbaik = float(
    hasil_dbi.loc[index_terbaik, "DBI"]
)


# ============================================================
# JUDUL DASHBOARD
# ============================================================

st.title(
    "📊 Dashboard Klasterisasi Sosial Ekonomi"
)

st.subheader(
    "Provinsi Sumatera Barat Menggunakan K-Means"
)

st.write(
    "Dashboard ini menyajikan hasil klasterisasi "
    "kabupaten/kota di Provinsi Sumatera Barat "
    "berdasarkan indikator sosial ekonomi "
    "menggunakan algoritma K-Means."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📌 Menu")

menu = st.sidebar.radio(
    "Pilih halaman:",
    [
        "Beranda",
        "Penentuan K Optimal",
        "Hasil Clustering",
        "Peta Clustering",
        "Centroid"
    ]
)


# ============================================================
# BERANDA
# ============================================================

if menu == "Beranda":

    st.header(
        "Ringkasan Hasil Clustering"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Kabupaten/Kota",
            "19"
        )

    with col2:

        st.metric(
            "K Optimal",
            str(k_optimal)
        )

    with col3:

        st.metric(
            "Nilai DBI",
            f"{dbi_terbaik:.4f}"
        )

    with col4:

        st.metric(
            "Indikator",
            "9"
        )

    st.divider()

    st.success(
        f"Jumlah cluster optimal berdasarkan "
        f"Davies-Bouldin Index adalah {k_optimal} "
        f"dengan nilai DBI sebesar {dbi_terbaik:.4f}."
    )

    st.subheader(
        "Distribusi Anggota Cluster"
    )

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

        fig.update_layout(
            xaxis_title="Cluster",
            yaxis_title="Jumlah Kabupaten/Kota"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PENENTUAN K OPTIMAL
# ============================================================

elif menu == "Penentuan K Optimal":

    st.header(
        "📊 Penentuan K Optimal Menggunakan DBI"
    )

    st.write(
        "Davies-Bouldin Index (DBI) digunakan untuk "
        "menentukan jumlah cluster (K) optimal. "
        "Nilai DBI yang lebih kecil menunjukkan "
        "hasil clustering yang lebih baik."
    )

    st.divider()

    # --------------------------------------------------------
    # GRAFIK DBI
    # --------------------------------------------------------

    st.subheader(
        "Grafik Davies-Bouldin Index"
    )

    fig = px.line(
        hasil_dbi,
        x="K",
        y="DBI",
        markers=True,
        title="Nilai DBI untuk K = 2 sampai K = 10"
    )

    fig.update_layout(
        xaxis_title="Jumlah Cluster (K)",
        yaxis_title="Nilai Davies-Bouldin Index (DBI)",
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    # Menandai K optimal
    fig.add_scatter(
        x=[k_optimal],
        y=[dbi_terbaik],
        mode="markers+text",
        text=[
            f"K Optimal = {k_optimal}<br>"
            f"DBI = {dbi_terbaik:.4f}"
        ],
        textposition="top center",
        marker=dict(
            size=14
        ),
        name="K Optimal"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # HASIL K OPTIMAL
    # --------------------------------------------------------

    st.subheader(
        "Hasil Penentuan K Optimal"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "K Optimal",
            str(k_optimal)
        )

    with col2:

        st.metric(
            "DBI Terkecil",
            f"{dbi_terbaik:.4f}"
        )

    st.success(
        f"Berdasarkan grafik dan tabel DBI, "
        f"nilai DBI terkecil adalah {dbi_terbaik:.4f} "
        f"pada K = {k_optimal}. "
        f"Oleh karena itu, K = {k_optimal} dipilih "
        f"sebagai jumlah cluster optimal."
    )

    # --------------------------------------------------------
    # TABEL DBI
    # --------------------------------------------------------

    st.subheader(
        "Tabel Hasil Perhitungan DBI"
    )

    st.dataframe(
        hasil_dbi,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# HASIL CLUSTERING
# ============================================================

elif menu == "Hasil Clustering":

    st.header(
        "📋 Hasil Clustering"
    )

    st.write(
        f"Hasil clustering menggunakan algoritma "
        f"K-Means dengan K optimal = {k_optimal}."
    )

    cluster_pilih = st.selectbox(
        "Pilih Cluster:",
        sorted(
            data["Cluster"].unique()
        )
    )

    data_cluster = data[
        data["Cluster"] == cluster_pilih
    ].copy()

    st.subheader(
        f"Anggota Cluster {cluster_pilih}"
    )

    st.write(
        f"Jumlah anggota: **{len(data_cluster)} "
        f"kabupaten/kota**"
    )

    st.dataframe(
        data_cluster,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PETA CLUSTERING
# ============================================================

elif menu == "Peta Clustering":

    st.header(
        "🗺️ Peta Hasil Clustering"
    )

    st.write(
        f"Peta distribusi hasil clustering "
        f"K-Means dengan K optimal = {k_optimal}."
    )

    # --------------------------------------------------------
    # SALIN GEOJSON
    # --------------------------------------------------------

    peta_tampil = json.loads(
        json.dumps(peta)
    )

    # --------------------------------------------------------
    # DATA WILAYAH DAN CLUSTER
    # --------------------------------------------------------

    data_peta = data[
        ["Kabupaten/Kota", "Cluster"]
    ].copy()

    # Pastikan Cluster berupa angka
    data_peta["Cluster"] = pd.to_numeric(
        data_peta["Cluster"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # SAMAKAN NAMA WILAYAH
    # --------------------------------------------------------

    data_peta["Kabupaten/Kota"] = (
        data_peta["Kabupaten/Kota"]
        .replace(
            "Kota Sawah Lunto",
            "Kota Sawahlunto"
        )
    )

    # --------------------------------------------------------
    # MASUKKAN CLUSTER KE GEOJSON
    # --------------------------------------------------------

    for feature in peta_tampil["features"]:

        properties = feature.get(
            "properties",
            {}
        )

        nama_wilayah = properties.get(
            "nama"
        )

        hasil = data_peta[
            data_peta["Kabupaten/Kota"] == nama_wilayah
        ]

        if not hasil.empty:

            properties["Cluster"] = str(
                int(
                    hasil.iloc[0]["Cluster"]
                )
            )

        else:

            properties["Cluster"] = "Tidak Ada"

        feature["properties"] = properties

    # --------------------------------------------------------
    # BUAT DATA UNTUK PETA
    # --------------------------------------------------------

    # Ambil nama wilayah dari GeoJSON
    nama_geojson = []

    for feature in peta_tampil["features"]:

        nama_geojson.append(
            feature.get(
                "properties",
                {}
            ).get("nama")
        )

    # Buat tabel khusus peta
    data_peta_map = pd.DataFrame(
        {
            "Kabupaten/Kota": nama_geojson
        }
    )

    # Gabungkan dengan data cluster
    data_peta_map = data_peta_map.merge(
        data_peta,
        on="Kabupaten/Kota",
        how="left"
    )

    # Jadikan Cluster sebagai kategori
    data_peta_map["Cluster"] = (
        data_peta_map["Cluster"]
        .fillna(0)
        .astype(int)
        .astype(str)
    )

    # --------------------------------------------------------
    # TAMPILKAN PETA
    # --------------------------------------------------------

    try:

        fig = px.choropleth_map(
            data_peta_map,
            geojson=peta_tampil,
            locations="Kabupaten/Kota",
            featureidkey="properties.nama",
            color="Cluster",
            color_discrete_map={
                "1": "green",
                "2": "yellow",
                "3": "red"
            },
            hover_name="Kabupaten/Kota",
            map_style="carto-positron",
            fitbounds="locations",
            opacity=0.7,
            category_orders={
                "Cluster": [
                    "1",
                    "2",
                    "3"
                ]
            }
        )

        fig.update_layout(
            margin=dict(
                r=0,
                t=0,
                l=0,
                b=0
            ),
            legend_title_text="Cluster"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            "Peta belum dapat ditampilkan."
        )

        st.code(
            str(e)
        )


# ============================================================
# CENTROID
# ============================================================

elif menu == "Centroid":

    st.header(
        "🎯 Centroid Setiap Cluster"
    )

    st.write(
        f"Centroid hasil clustering dengan "
        f"K optimal = {k_optimal}."
    )

    st.dataframe(
        centroid,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Nilai centroid menunjukkan karakteristik "
        "masing-masing cluster berdasarkan "
        "sembilan indikator sosial ekonomi."
    )
