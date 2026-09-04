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
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    # Data hasil clustering
    data = pd.read_excel(
        "data_dashboard_dbi.xlsx"
    )

    # Data centroid
    centroid = pd.read_excel(
        "centroid_cluster_dbi.xlsx"
    )

    # Hasil perhitungan DBI K=2 sampai K=10
    df_dbi = pd.read_excel(
        "hasil_dbi.xlsx"
    )

    # Data peta
    with open(
        "hasil_cluster_peta_dbi.geojson",
        "r",
        encoding="utf-8"
    ) as file:

        peta = json.load(file)

    return data, centroid, df_dbi, peta


# ============================================================
# MEMANGGIL DATA
# ============================================================

try:

    data, centroid, df_dbi, peta = load_data()

except Exception as e:

    st.error("Data dashboard gagal dibaca.")

    st.write(
        "Pastikan semua file berada dalam repository GitHub "
        "yang sama dengan app.py."
    )

    st.code(str(e))

    st.stop()


# ============================================================
# CEK KOLOM DBI
# ============================================================

if "K" not in df_dbi.columns or "DBI" not in df_dbi.columns:

    st.error(
        "File hasil_dbi.xlsx harus memiliki kolom 'K' dan 'DBI'."
    )

    st.write(
        "Kolom yang ditemukan:"
    )

    st.write(
        list(df_dbi.columns)
    )

    st.stop()


# ============================================================
# MEMBERSIHKAN DATA DBI
# ============================================================

df_dbi["K"] = pd.to_numeric(
    df_dbi["K"],
    errors="coerce"
)

df_dbi["DBI"] = pd.to_numeric(
    df_dbi["DBI"],
    errors="coerce"
)

df_dbi = df_dbi.dropna(
    subset=["K", "DBI"]
)

df_dbi = df_dbi.sort_values(
    "K"
).reset_index(drop=True)


# ============================================================
# MENENTUKAN K OPTIMAL OTOMATIS
# ============================================================

index_terbaik = df_dbi["DBI"].idxmin()

k_optimal = int(
    df_dbi.loc[index_terbaik, "K"]
)

dbi_terbaik = float(
    df_dbi.loc[index_terbaik, "DBI"]
)


# ============================================================
# JUDUL DASHBOARD
# ============================================================

st.title(
    "📊 Dashboard Klasterisasi Sosial Ekonomi"
)

st.subheader(
    "Provinsi Sumatera Barat Menggunakan K-Means "
    "dan Davies-Bouldin Index (DBI)"
)

st.write(
    "Dashboard ini menyajikan hasil klasterisasi "
    "kabupaten/kota di Provinsi Sumatera Barat "
    "berdasarkan indikator sosial ekonomi."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📌 Menu")

menu = st.sidebar.radio(
    "Pilih halaman:",
    [
        "Beranda",
        "Evaluasi DBI",
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
            "DBI Terbaik",
            f"{dbi_terbaik:.4f}"
        )

    with col4:

        st.metric(
            "Indikator",
            "9"
        )

    st.divider()

    st.success(
        f"K optimal berdasarkan DBI adalah "
        f"{k_optimal} dengan nilai DBI "
        f"{dbi_terbaik:.4f}."
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
# EVALUASI DBI
# ============================================================

elif menu == "Evaluasi DBI":

    st.header(
        "📈 Evaluasi Davies-Bouldin Index"
    )

    st.write(
        "Metode Davies-Bouldin Index digunakan untuk "
        "menentukan jumlah cluster optimal. "
        "K optimal dipilih berdasarkan nilai DBI "
        "yang paling rendah."
    )

    # --------------------------------------------------------
    # GRAFIK DBI
    # --------------------------------------------------------

    fig = px.line(
        df_dbi,
        x="K",
        y="DBI",
        markers=True,
        title="Davies-Bouldin Index untuk Menentukan K Optimal"
    )

    fig.update_layout(
        xaxis_title="Jumlah Cluster (K)",
        yaxis_title="Nilai DBI",
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    # --------------------------------------------------------
    # TANDA K OPTIMAL
    # --------------------------------------------------------

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
    # HASIL OTOMATIS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "K Optimal",
            str(k_optimal)
        )

    with col2:

        st.metric(
            "DBI Terbaik",
            f"{dbi_terbaik:.4f}"
        )

    st.success(
        f"Berdasarkan nilai DBI terkecil, "
        f"K optimal adalah **{k_optimal}** "
        f"dengan nilai DBI **{dbi_terbaik:.4f}**."
    )

    # --------------------------------------------------------
    # TABEL DBI
    # --------------------------------------------------------

    st.subheader(
        "Tabel Nilai DBI"
    )

    st.dataframe(
        df_dbi,
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
        f"Hasil pengelompokan kabupaten/kota "
        f"menggunakan K-Means dengan "
        f"K optimal = {k_optimal}."
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
        f"Jumlah anggota: "
        f"**{len(data_cluster)} kabupaten/kota**"
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
        "Peta menunjukkan distribusi cluster "
        "kabupaten/kota di Provinsi Sumatera Barat."
    )

    # --------------------------------------------------------
    # SALIN GEOJSON
    # --------------------------------------------------------

    peta_tampil = json.loads(
        json.dumps(peta)
    )

    # --------------------------------------------------------
    # DATA CLUSTER
    # --------------------------------------------------------

    data_peta = data[
        ["Kabupaten/Kota", "Cluster"]
    ].copy()

    data_peta["Cluster"] = pd.to_numeric(
        data_peta["Cluster"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # SESUAIKAN NAMA SAWAHLUNTO
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

    for feature in peta_tampil.get(
        "features",
        []
    ):

        properties = feature.get(
            "properties",
            {}
        )

        nama_wilayah = properties.get(
            "nama"
        )

        hasil = data_peta[
            data_peta["Kabupaten/Kota"]
            == nama_wilayah
        ]

        if not hasil.empty:

            properties["Cluster"] = int(
                hasil.iloc[0]["Cluster"]
            )

        else:

            properties["Cluster"] = 0

        feature["properties"] = properties

    # --------------------------------------------------------
    # PETA
    # --------------------------------------------------------

    try:

        fig = px.choropleth_map(
            data_peta,
            geojson=peta_tampil,
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

        fig.update_layout(
            margin=dict(
                r=0,
                t=0,
                l=0,
                b=0
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            "Peta belum dapat ditampilkan."
        )

        st.write(
            "Terjadi masalah pada GeoJSON "
            "atau nama wilayah."
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
        "Nilai centroid menunjukkan rata-rata "
        "nilai indikator pada masing-masing cluster."
    )

    st.dataframe(
        centroid,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Centroid digunakan untuk melihat "
        "karakteristik masing-masing cluster."
    )
