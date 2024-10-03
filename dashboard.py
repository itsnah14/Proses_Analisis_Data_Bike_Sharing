import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets
df_day = pd.read_csv("day.csv")
df_hour = pd.read_csv("hour.csv")

# Pastikan kolom 'dteday' dalam format datetime
df_day['dteday'] = pd.to_datetime(df_day['dteday'])

# Dashboard title
st.title("Dashboard Penyewaan Sepeda")

# ------------------------------------------------
# METRIC: TOTAL RENTALS, CASUAL, REGISTERED (Filtered Data)
# ------------------------------------------------
col1, col2, col3 = st.columns([1, 1.5, 1.5])  # Memberikan lebih banyak ruang untuk kolom ke-3

# ---------------------------------
# FILTERING BERDASARKAN TANGGAL
# ---------------------------------
st.sidebar.header("Filter Data Berdasarkan Tanggal")

# Mengonversi min_date dan max_date ke tipe datetime.date agar sesuai dengan date_input Streamlit
min_date = df_day['dteday'].min().date()
max_date = df_day['dteday'].max().date()
date_selected = st.sidebar.date_input("Pilih Rentang Tanggal", value=[min_date, max_date], min_value=min_date, max_value=max_date)

# Konversikan rentang tanggal yang dipilih kembali ke datetime untuk filtering
df_day_filtered = df_day[(df_day['dteday'] >= pd.to_datetime(date_selected[0])) & (df_day['dteday'] <= pd.to_datetime(date_selected[1]))]

# Metrics berdasarkan data yang difilter
total_rentals = df_day_filtered['cnt'].sum()
with col1:
    st.metric(label="Total Penyewaan Sepeda", value=total_rentals)

total_casual = df_day_filtered['casual'].sum()
with col2:
    st.metric(label="Total Penyewaan Pelanggan Casual", value=total_casual)

total_registered = df_day_filtered['registered'].sum()
with col3:
    st.metric(label="Total Penyewaan Pelanggan Registered", value=total_registered)

# ---------------------------------
# VISUALISASI UNTUK DATA KATEGORIKAL (Question 1)
# ---------------------------------
st.subheader("Faktor-Faktor yang Mempengaruhi Penyewaan Sepeda (Data Kategorikal)")

# Grouping and calculating mean for filtered data
grouped_season = df_day_filtered.groupby('season').agg({"cnt": ["mean"]})
grouped_weathersit = df_day_filtered.groupby('weathersit').agg({"cnt": ["mean"]})
grouped_workingday = df_day_filtered.groupby('workingday').agg({"cnt": ["mean"]})
grouped_holiday = df_day_filtered.groupby('holiday').agg({"cnt": ["mean"]})
grouped_weekday = df_day_filtered.groupby('weekday').agg({"cnt": ["mean"]})

# Calculate differences between max and min means for each factor
season_diff = grouped_season['cnt']['mean'].max() - grouped_season['cnt']['mean'].min()
weathersit_diff = grouped_weathersit['cnt']['mean'].max() - grouped_weathersit['cnt']['mean'].min()
workingday_diff = grouped_workingday['cnt']['mean'].max() - grouped_workingday['cnt']['mean'].min()
holiday_diff = grouped_holiday['cnt']['mean'].max() - grouped_holiday['cnt']['mean'].min()
weekday_diff = grouped_weekday['cnt']['mean'].max() - grouped_weekday['cnt']['mean'].min()

# Create DataFrame to store the differences
diff_comparison = pd.DataFrame({
    'Kategori': ['season', 'weathersit', 'workingday', 'holiday', 'weekday'],
    'Selisih (mean tertinggi - mean terendah)': [season_diff, weathersit_diff, workingday_diff, holiday_diff, weekday_diff]
})

# Sort by difference
diff_comparison_sorted = diff_comparison.sort_values(by='Selisih (mean tertinggi - mean terendah)', ascending=False)

# Reset index for cleaner output
diff_comparison_sorted = diff_comparison_sorted.reset_index(drop=True)

# Visualization: Bar Chart of Categorical Factors
colors = ['#66CDAA' if i <= 1 else '#D3D3D3' for i in range(len(diff_comparison_sorted))]
plt.figure(figsize=(10,5))
plt.barh(diff_comparison_sorted['Kategori'], diff_comparison_sorted['Selisih (mean tertinggi - mean terendah)'], color=colors)
plt.xlabel('Selisih Rata-rata Penyewaan')
plt.title('Urutan Faktor Kategorikal Berdasarkan Pengaruhnya')
plt.gca().invert_yaxis()  # Sort from largest to smallest
st.pyplot(plt)

# ---------------------------------
# VISUALISASI UNTUK DATA NUMERIK (Question 1)
# ---------------------------------
st.subheader("Pengaruh Faktor Numerik Terhadap Penyewaan Sepeda")

# Compute correlation for numerical factors for filtered data
numerical_columns = ['temp', 'atemp', 'hum', 'windspeed'] 
corr_comparison_sorted = df_day_filtered[numerical_columns + ['cnt']].corr()['cnt'].drop('cnt').sort_values(ascending=False)

# Membuat lollipop chart
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['green' if x >= 0 else 'red' for x in corr_comparison_sorted]

# Create lollipop chart
for i, (faktor, nilai, color) in enumerate(zip(corr_comparison_sorted.index, corr_comparison_sorted, colors)):
    ax.hlines(y=i, xmin=0, xmax=nilai, color=color, alpha=0.5)
    ax.scatter(nilai, i, color=color, s=50)

# Add correlation values
for i, v in enumerate(corr_comparison_sorted):
    ax.text(v, i, f' {v:.3f}', va='center', ha='left' if v >= 0 else 'right')

# Add vertical line at x=0
ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)

# Set axis limits and grid
ax.set_xlim(min(corr_comparison_sorted) - 0.1, max(corr_comparison_sorted) + 0.1)
ax.grid(axis='x', linestyle=':', alpha=0.6)
ax.invert_yaxis()  # Flip y-axis for easier reading

# Display the plot in Streamlit
st.pyplot(fig)

# ---------------------------------
# VISUALISASI PERTANYAAN 2: POLA PENYEWAAN BERDASARKAN JAM
# ---------------------------------
st.subheader("Pola Penyewaan Sepeda Berdasarkan Jam dalam Sehari")

# Menghitung rata-rata penyewaan per jam (dari df_hour)
avg_rentals_per_hour = df_hour.groupby('hr')['cnt'].mean()

# Mengidentifikasi tiga jam dengan rata-rata penyewaan tertinggi
top_3_hours = avg_rentals_per_hour.nlargest(3).index

# Membuat warna hijau untuk 3 jam tertinggi, dan warna abu untuk yang lainnya
colors = ['#66CDAA' if hr in top_3_hours else '#D3D3D3' for hr in avg_rentals_per_hour.index]

# Membuat bar chart untuk rata-rata penyewaan per jam dengan warna yang disesuaikan
plt.figure(figsize=(10,5))
avg_rentals_per_hour.plot(kind='bar', color=colors)

# Menambahkan label dan judul
plt.xlabel('Jam')
plt.ylabel('Rata-rata Penyewaan')
plt.title('Rata-rata Penyewaan Sepeda Berdasarkan Jam dalam Sehari')

# Display plot
st.pyplot(plt)

# ------------------------------------------------
# CLUSTERING BERDASARKAN KOMBINASI WAKTU DAN CUACA
# ------------------------------------------------
st.subheader("Clustering Berdasarkan Kombinasi Waktu dan Cuaca")

# 1. Membuat kolom baru yang mengelompokkan hr menjadi interval waktu dengan label tertentu
df_hour['time_category'] = pd.cut(df_hour['hr'],
                                  bins=[-1, 6, 9, 15, 19, 23],
                                  labels=['Jam Sepi Pagi',
                                          'Jam Sibuk Pagi',
                                          'Jam Biasa',
                                          'Jam Sibuk Sore',
                                          'Jam Sepi Malam'])

# 2. Mengelompokkan cuaca menjadi 4 kategori berdasarkan weathersit
df_hour['weather_category'] = df_hour['weathersit'].apply(
    lambda x: 'Cerah' if x == 1 else
              'Berkabut/Berawan' if x == 2 else
              'Salju/Hujan Ringan' if x == 3 else
              'Hujan Lebat/Salju/Badai'
)

# 3. Mengonversi kategori ke string dan menggabungkan kategori waktu dan cuaca
df_hour['time_weather_group'] = df_hour['time_category'].astype(str) + ' - ' + df_hour['weather_category'].astype(str)

# 4. Menghitung rata-rata penyewaan berdasarkan kombinasi waktu dan cuaca
grouped_by_combination = df_hour.groupby(['time_category', 'weather_category'])['cnt'].mean().reset_index()

# 5. Membuat clustered bar chart dengan warna yang disesuaikan
plt.figure(figsize=(12,6))
sns.barplot(x='time_category', y='cnt', hue='weather_category', data=grouped_by_combination, 
            palette={'Cerah': '#66CDAA', 
                     'Berkabut/Berawan': '#FF6F61', 
                     'Salju/Hujan Ringan': '#F9E79F', 
                     'Hujan Lebat/Salju/Badai': '#A9A9A9'})

# Menambahkan label dan judul
plt.title('Rata-rata Penyewaan Sepeda Berdasarkan Waktu dan Cuaca')
plt.xlabel('Kategori Waktu')
plt.ylabel('Rata-rata Penyewaan Sepeda')

# Menampilkan plot di Streamlit
st.pyplot(plt)