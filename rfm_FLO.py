
###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

###############################################################
# İş Problemi (Business Problem)
###############################################################
# FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
# Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranış öbeklenmelerine göre gruplar oluşturulacak..

###############################################################
# Veri Seti Hikayesi
###############################################################

# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi

###############################################################
# GÖREVLER
###############################################################

# GÖREV 1: Veriyi Anlama (Data Understanding) ve Hazırlama
           # 1. flo_data_20K.csv verisini okuyunuz.
           # 2. Veri setinde
                     # a. İlk 10 gözlem,
                     # b. Değişken isimleri,
                     # c. Betimsel istatistik,
                     # d. Boş değer,
                     # e. Değişken tipleri, incelemesi yapınız.
           # 3. Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Herbir müşterinin toplam
           # alışveriş sayısı ve harcaması için yeni değişkenler oluşturun.
           # 4. Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.
           # 5. Alışveriş kanallarındaki müşteri sayısının, ortalama alınan ürün sayısının ve ortalama harcamaların dağılımına bakınız.
           # 6. En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.
           # 7. En fazla siparişi veren ilk 10 müşteriyi sıralayınız.
           # 8. Veri ön hazırlık sürecini fonksiyonlaştırınız.

# 1
import datetime as dt
import pandas as pd
pd.set_option("display.width", 1000)
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: "%.3f" % x)

df_ = pd.read_csv("flo_data_20k.csv")
df = df_.copy()

df.describe().T
df.isnull().sum()

# 2
df.head(10)
df.columns

df["master_id"].count()
df.describe().T
df.isnull().sum()
df.value_counts("master_id")
df.shape
df.info()

# 3
df["total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

df["total_price"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# 4
df.info()
df["first_order_date"] = pd.to_datetime(df["first_order_date"])        # datetime tipine çevirme
df["last_order_date"] = pd.to_datetime(df["last_order_date"])
df["last_order_date_online"] = pd.to_datetime(df["last_order_date_online"])
df["last_order_date_offline"] = pd.to_datetime(df["last_order_date_offline"])

# 5
df["order_channel"].value_counts()
df.groupby("order_channel").agg({"master_id": "count",
                                 "total_order": ["sum", "mean"],
                                 "total_price": ["sum", "mean"]})

# 6
df.groupby("master_id").agg({"total_price": "sum"}).sort_values("total_price", ascending=False).head(10)

# 7
df.groupby("master_id").agg({"total_order": "sum"}).sort_values("total_order", ascending=False).head(10)

# 8. Veri ön hazırlık sürecini fonksiyonlaştırınız.
# ??????????????????????????????


# GÖREV 2: RFM Metriklerinin Hesaplanması
df["last_order_date_offline"].max()

today_date = today_date = dt.datetime(2021, 6, 1)

today_date - df["last_order_date"].max()

rfm = df.groupby("master_id").agg({"last_order_date": lambda date: (today_date - date.max()).days,
                             "total_order": "sum",
                             "total_price": "sum"})

rfm.columns = ["recency", "frequency", "monetary"]


rfm.head()

rfm.info()
rfm.min()
rfm.max()

###############################################################
# GÖREV 3: RF ve RFM Skorlarının Hesaplanması (Calculating RF and RFM Scores)
###############################################################

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])


# recency_score ve frequency_score’u tek bir değişken olarak ifade edilmesi ve RF_SCORE olarak kaydedilmesi
rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)


###############################################################
# GÖREV 4: RF Skorlarının Segment Olarak Tanımlanması
###############################################################

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["SEGMENT"] = rfm["RF_SCORE"].replace(seg_map, regex=True)


rfm.head()


###############################################################
# GÖREV 5: Aksiyon zamanı!
###############################################################
# 1. Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.
rfm.groupby("SEGMENT").agg({"recency": "mean",
                            "frequency": "mean",
                            "monetary": "mean"})


# 2. RFM analizi yardımı ile 2 case için ilgili profildeki müşterileri bulunuz ve müşteri id'lerini csv ye kaydediniz.

# a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri tercihlerinin üstünde. Bu nedenle markanın
# tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak iletişime geçeilmek isteniliyor. Bu müşterilerin sadık  ve
# kadın kategorisinden alışveriş yapan kişiler olması planlandı. Müşterilerin id numaralarını csv dosyasına yeni_marka_hedef_müşteri_id.cvs
# olarak kaydediniz.
rfm_f = df.merge(rfm, on="master_id", how="left")

rfm_f[(rfm_f["SEGMENT"] == "champions") |
    (rfm_f["SEGMENT"] == "loyal_customers") &
    (rfm_f['interested_in_categories_12'].str.contains("ERKEK"))]

rfm_f["master_id"].to_csv("case_a_target_cust.csv")


    # Kadın kategorisinden de alışveriş yapanlar:
cust_list1 = list((df[df["interested_in_categories_12"].str.contains("KADIN")])["master_id"]) # kadın kategorisinde alışveriş yapanlar
cust_list2 = list(rfm[(rfm["SEGMENT"] == "champions") | (rfm["SEGMENT"] == "loyal_customers")].index)

def check(list1, list2):
    target_customers = []
    for row in list1:
        if row in list2:
            target_customers.append(row)
    return target_customers


casea_cutomers = check(cust_list1, cust_list2)
len(casea_cutomers)



# b. Erkek ve Çoçuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte iyi müşterilerden olan ama uzun süredir
# alışveriş yapmayan ve yeni gelen müşteriler özel olarak hedef alınmak isteniliyor. Uygun profildeki müşterilerin id'lerini csv dosyasına indirim_hedef_müşteri_ids.csv
# olarak kaydediniz.

rfm_f = df.merge(rfm, on="master_id", how="left")

rfm_f[(rfm_f['interested_in_categories_12'].str.contains("ERKEK")) &
      (rfm_f['interested_in_categories_12'].str.contains("COCUK")) &
      ((rfm_f["SEGMENT"] == "cant_loose") |
       (rfm_f["SEGMENT"] == "about_to_sleep") |
       (rfm_f["SEGMENT"] == "new_customers"))]

rfm_f["master_id"].to_csv("case_b_target_cust.csv")


















