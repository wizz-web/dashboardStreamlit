import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# JUDUL
st.title("Analisis Data E-Commerce")

# Membaca data
df = pd.read_csv("https://raw.githubusercontent.com/wizz-web/dashboardStreamlit/refs/heads/main/main_data.csv")

# Menampilkan preview data
st.write("Preview Data:")
st.dataframe(df.head())

# Menambahkan filter di sidebar agar pengguna bisa memilih tahun dan kota
st.sidebar.header("Filter")

# Filter Tahun
year_options = ["All"] + sorted(df['year'].unique().tolist())

selected_year = st.sidebar.selectbox(
    "Pilih Tahun",
    options=year_options
)


# Filter Kota (supaya tidak langsung semua tampil)
selected_city = st.sidebar.multiselect(
    "Pilih Kota",
    options=sorted(df['customer_city'].unique())
)

df_filtered = df.copy()

# Filter Tahun
if selected_year != "All":
    df_filtered = df_filtered[df_filtered['year'] == selected_year]

# Filter Kota
if selected_city:
    df_filtered = df_filtered[df_filtered['customer_city'].isin(selected_city)]

st.subheader("Data Setelah Filter")
st.dataframe(df_filtered.head())

# Menghitung KPI
total_transaksi = df_filtered.shape[0]
total_produk_terjual = df_filtered['product_category_name_english'].count()
rata_rating = df_filtered['review_score'].mean()
jumlah_kota = df_filtered['customer_city'].nunique()

# Buat 4 kolom KPI
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Transaksi", total_transaksi)
col2.metric("Total Produk Terjual", total_produk_terjual)
col3.metric("Rata-rata Rating", round(rata_rating, 2))
col4.metric("Jumlah Kota Aktif", jumlah_kota)


col1, col2 = st.columns(2)

#layout 1 kolom untuk top produk terlaris
with col1:
    # Menganalisis Top 10 Produk Terlaris
    top_produk = (
    df_filtered['product_category_name_english']
    .value_counts()
    .head(10)
    .reset_index()
    )

    top_produk.columns = ['product_category_name_english', 'total_penjualan']

    # Visualisasi top 10 produk terlaris
    st.subheader("Top 10 Produk Terlaris")

    st.bar_chart(
        top_produk.set_index('product_category_name_english')
    )


#layout 2 kolom untuk rating per produk

with col2:

    # RATING PER PRODUK
    rating_produk = (
        df_filtered
        .groupby('product_category_name_english')
        .agg(
            rata_rating=('review_score', 'mean'),
            jumlah_review=('review_score', 'count')
        )
        .sort_values(by='jumlah_review', ascending=False)
        .head(10)
        .sort_values(by='rata_rating', ascending=True)
        )

    st.subheader("Top 10 Produk Berdasarkan Rating")

    fig, ax = plt.subplots(figsize=(10,6))

    ax.barh(
        rating_produk.index,
        rating_produk['rata_rating']
    )

    ax.set_xlabel("Rata-rata Rating")
    ax.set_ylabel("Produk")
    ax.set_xlim(0, 5)

    st.pyplot(fig)


#Dipisahkan agar lebih rapi, dan mudah dibaca, karena top kota dan tren waktu lebih banyak data yang ditampilkan


# ambil nama kategori top 10 saja
top10_categories = df_filtered['product_category_name_english'].value_counts().head(10).index

# filter dataframe hanya untuk top 10 kategori
df_top10 = df_filtered[df_filtered['product_category_name_english'].isin(top10_categories)]

st.subheader("Perbandingan Penjualan dan Rata-rata Rating untuk Top 10 Kategori Produk")    

# membuat kolom jumlah barang beserta rata-rata review_score
df2 = df_top10.groupby('product_category_name_english').agg({
    'review_score': 'mean',
    'product_category_name_english': 'count'
}).rename(columns={
    'product_category_name_english': 'jumlah rate',
    'review_score': 'rata_rata_review'
}).reset_index()


fig, ax1 = plt.subplots(figsize=(10, 6))

df2['jumlah rate'].plot(kind='bar', ax=ax1, color='skyblue', position=1, width=0.4, label='Penjualan')
ax1.set_ylabel('Jumlah Penjualan', color='blue')
ax1.set_xlabel('product_category_name_english')
ax1.set_xticklabels(df2['product_category_name_english'], rotation=45)

ax2 = ax1.twinx()
df2['rata_rata_review'].plot(kind='bar', ax=ax2, color='orange', position=0, width=0.4, label='Rata-rata Rating')
ax2.set_ylabel('Rata-rata Rating', color='orange')

plt.title('Dual Insight: Penjualan vs Rating')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.tight_layout()
ax1.set_xticks(range(len(df2)))
ax1.set_xticklabels(df2['product_category_name_english'], rotation=45, ha='right')
st.pyplot(fig)

# TREN WAKTU
df_filtered['order_purchase_timestamp'] = pd.to_datetime(
    df_filtered['order_purchase_timestamp']
    )

# Group per bulan
tren_bulanan = (
    df_filtered
    .set_index('order_purchase_timestamp')
    .resample('M')
    .size()
)

st.subheader("Tren Penjualan per Bulan")

fig, ax = plt.subplots(figsize=(10,6))

ax.plot(
    tren_bulanan.index,
    tren_bulanan.values,
    marker='o'
)

ax.set_xlabel("Bulan")
ax.set_ylabel("Total Penjualan")

plt.xticks(rotation=45)

st.pyplot(fig)
