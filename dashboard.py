import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency


def create_total_orders(df):
    # total orders
    total_orders = df['order_id'].nunique()
    return total_orders

def create_total_revenue_df(df):
    # total revenue
    total_revenue = df['price'].sum()
    return total_revenue

def create_total_customers_df(df):
    # total customers
    total_customers = df['customer_unique_id'].nunique()
    return total_customers

def create_monthly_trend_df(df):
    df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    monthly_orders = df.groupby('order_month')['order_id'].nunique().reset_index(name='order_count')
    monthly_revenue = df.groupby('order_month')['price'].sum().reset_index(name='revenue')

    return monthly_orders, monthly_revenue

def create_accuracy_delivery_df(df):
    # accuracy delivery
    delivery_counts = df['delivery_accuracy'].value_counts().reset_index(name='order_count').rename(columns={'index': 'delivery_accuracy'})
    return delivery_counts

def create_category_performance_df(df):
    category_perf = df.groupby('product_category_name').agg(
        total_order=('order_id', 'count'),
        total_revenue=('price', 'sum')
    ).sort_values(by='total_revenue', ascending=False).reset_index().head(10)
    return category_perf

def create_rfm_df(df):
   reference_date = df['order_purchase_timestamp'].max()

   rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
   }).reset_index()

   rfm_df.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']

   return rfm_df

# Load data
all_df = pd.read_csv('all_df.csv')

# Streamlit App
st.set_page_config(layout="wide")
st.title("📦 E-Commerce Sales Dashboard")

all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.title("📦 E-Commerce Sales Dashboard")
    start_date, end_date = st.date_input(
        label='Rentang Waktu Pembelian Pesanan',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan rentang tanggal
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & (all_df["order_purchase_timestamp"] <= str(end_date))]

# Metrik Utama
total_orders = create_total_orders(main_df)
total_revenue = create_total_revenue_df(main_df)
total_customers = create_total_customers_df(main_df)
monthly_orders, monthly_revenue = create_monthly_trend_df(main_df)
delivery_counts = create_accuracy_delivery_df(main_df)
category_performance = create_category_performance_df(main_df)
rfm = create_rfm_df(main_df)

# Menampilkan Metrik Utama
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", total_orders)
with col2:
    st.metric("Total Revenue", format_currency(total_revenue, 'USD', locale='en_US'))
with col3:
    st.metric("Total Customers", total_customers)

# Visualisasi Tren Bulanan
st.subheader("📈 Revenue Over Time")
col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots(figsize=(10,7.15))
    ax1.plot(monthly_orders['order_month'], monthly_orders['order_count'], marker='o')
    ax1.set_title('Tren Jumlah Pesanan per Bulan')
    ax1.set_xlabel('Bulan')
    ax1.set_ylabel('Jumlah Pesanan')
    plt.xticks(rotation=75)
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots(figsize=(10,7))
    ax2.plot(monthly_revenue['order_month'], monthly_revenue['revenue'], marker='o')
    ax2.set_title('Tren Pendapatan per Bulan')
    ax2.set_xlabel('Bulan')
    ax2.set_ylabel('Jumlah Pendapatan')
    plt.xticks(rotation=75)
    st.pyplot(fig2)

st.write("**Secara umum, jumlah pesanan dan revenue menunjukkan pola yang sejalan, di mana saat order meningkat maka pendapatan juga ikut naik. Namun, pada beberapa periode terlihat bahwa kenaikan jumlah pesanan tidak selalu diikuti lonjakan revenue yang signifikan, menandakan adanya perbedaan nilai transaksi antar produk atau kategori.**")
st.markdown("---")

# Visualisasi Akurasi Pengiriman
st.subheader("🚚 Delivery Accuracy")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    fig3, ax3 = plt.subplots(figsize=(5,3.5))
    
    sns.barplot(
        data=delivery_counts,
        x='delivery_accuracy',
        y='order_count',
        ax=ax3
    )
    
    ax3.set_title('Akurasi Pengiriman Pesanan')
    ax3.set_xlabel('Akurasi Pengiriman')
    ax3.set_ylabel('Jumlah Pesanan')
    
    st.pyplot(fig3)

st.write("**Mayoritas pesanan terkirim lebih cepat dari estimasi yang diberikan. Meski demikian, masih terdapat sebagian pesanan yang mengalami keterlambatan, walaupun jumlahnya relatif kecil. Ini menunjukkan sistem estimasi pengiriman sudah cukup baik, tetapi masih bisa ditingkatkan untuk kasus-kasus tertentu.**")
st.markdown("---")

# Visualisasi Kinerja Kategori Produk
st.subheader("📊 Product Category Performance")

colors_order = plt.cm.Set2(np.linspace(0, 1, len(category_performance)))
colors_revenue = plt.cm.Set3(np.linspace(0, 1, len(category_performance)))

col1, col2 = st.columns(2)
with col1:
    fig4, ax4 = plt.subplots(figsize=(10,7.25))

    sns.barplot(
        data=category_performance,
        x='product_category_name',
        y='total_order',
        color="#00FF08"
    )
    ax4.set_title('Top 10 Kategori Produk berdasarkan Jumlah Pesanan')
    ax4.set_xlabel('Kategori Produk')
    ax4.set_ylabel('Jumlah Pesanan')
    plt.xticks(rotation=75)
    st.pyplot(fig4)

with col2:
    fig5, ax5 = plt.subplots(figsize=(6,3))

    sns.barplot(
        data=category_performance,
        x='product_category_name',
        y='total_revenue',
        color="#FFEA00"
    )
    ax5.set_title('Top 10 Kategori Produk berdasarkan Pendapatan')
    ax5.set_xlabel('Kategori Produk')
    ax5.set_ylabel('Jumlah Pendapatan')
    plt.xticks(rotation=75)
    st.pyplot(fig5)

st.write("**Produk yang paling sering di-order berasal dari kategori kebutuhan rumah tangga dan gaya hidup, sementara kategori dengan revenue tertinggi tidak selalu berasal dari produk yang paling sering dibeli. Hal ini menunjukkan bahwa beberapa produk memiliki nilai transaksi yang lebih besar meskipun jumlah ordernya lebih sedikit.**")
st.markdown("---")

# Visualisasi RFM
st.subheader("Best Customer Based on RFM Parameters")
tab1, tab2, tab3 = st.tabs(["RFM Score", "Customer Behavior", "Customer Segmentation"])

with tab1:
    st.subheader("📊 Distribusi Skor RFM")

    rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1])
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1,2,3,4])
    rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4])

    rfm['RFM_score'] = rfm['R_score'].astype(int) + rfm['F_score'].astype(int) + rfm['M_score'].astype(int)
    fig, ax = plt.subplots(figsize=(8,4))
    rfm['RFM_score'].value_counts().sort_index().head(10).plot(
        kind='bar',
        ax=ax
    )

    ax.set_xlabel('RFM Score')
    ax.set_ylabel('Jumlah Pelanggan')
    ax.set_title('Distribusi Pelanggan Berdasarkan RFM Score')
    plt.xticks(rotation=0)
    st.pyplot(fig)

with tab2:
    st.subheader("💰 Perilaku Pembelian Pelanggan")

    fig, ax = plt.subplots(figsize=(6,5))

    ax.scatter(
        rfm['Frequency'],
        rfm['Monetary'],
        alpha=0.5
    )

    ax.set_xlabel('Frequency (Jumlah Order)')
    ax.set_ylabel('Monetary (Total Pengeluaran)')
    ax.set_title('Hubungan Frequency dan Monetary')

    st.pyplot(fig)

with tab3:
    st.subheader("👥 Segmentasi Pelanggan")

    def segment_rfm(row):
        if row['RFM_score'] >= 10:
            return 'High Value'
        elif row['RFM_score'] >= 7:
            return 'Medium Value'
        else:
            return 'Low Value'

    rfm['segment'] = rfm.apply(segment_rfm, axis=1)

    fig, ax = plt.subplots(figsize=(6,4))
    rfm['segment'].value_counts().plot(
        kind='bar',
        ax=ax
    )

    ax.set_xlabel('Segmen Pelanggan')
    ax.set_ylabel('Jumlah Pelanggan')
    ax.set_title('Segmentasi Pelanggan Berdasarkan RFM')
    plt.xticks(rotation=75)
    st.pyplot(fig)

st.write("**Hasil RFM Analysis menunjukkan adanya beberapa segmen pelanggan dengan karakteristik berbeda, seperti pelanggan aktif dengan frekuensi dan nilai belanja tinggi, pelanggan reguler, serta pelanggan pasif yang sudah lama tidak melakukan transaksi. Segmentasi ini membantu memahami pelanggan mana yang perlu dipertahankan dan mana yang perlu diaktifkan kembali.**")
st.markdown("---")