import os
import numpy as np
import pandas as pd
import streamlit as st

def data_preprocess(data):
    #data clearing

    data["Lost profit"] = data["Lost profit"].str.replace(",",".")
    data["Lost profit"] = data["Lost profit"].astype(float)

    #create new columns

    #вспомогательные столбцы
    data["Price rank"] = data["Final price"].rank(ascending = 1)/data.shape[0]
    data["Cumulative revenue"] = np.cumsum(data["Revenue"])

    #добавляем столбцы
    data["Group A"] = data["Cumulative revenue"].apply(lambda x: 1 if x/data["Revenue"].sum()<0.8 else 0)
    data["Price range"] = data["Price rank"].apply(lambda x: "Эконом" if x < 0.11 else ("Эконом+" if x<0.22 else("Средний-" if x < 0.33 else("Средний" if x < 0.44 else("Средний+" if x < 0.55 else("Бизнес-" if x < 0.66 else("Бизнес" if x < 0.77 else("Бизнес+" if x < 0.88 else "Люкс"))))))))

    return data

def price_segmentation(data):
  #ranges list
  ranges = ["Эконом", "Эконом+","Средний-","Средний","Средний+","Бизнес-","Бизнес","Бизнес+","Люкс"]

  #lists
  diapazon = []
  mean_price = []
  overall_share = []
  sku = []
  revenue_per_sku = []
  sku_with_sales = []
  percent_sku_with_sales = []
  sku_over1m = []
  percent_sku_over1m = []
  sales = []
  sales_over1m = []
  share_sales_over1m = []
  revenue = []
  revenue_over1m = []
  share_revenue_over1m = []
  lost_profit = []
  share_lost_profit = []
  group_a = []
  share_group_a = []

  #append information to lists
  for Range in ranges:
      df = data[data["Price range"] == Range]
      diapazon.append(str(df["Final price"].min())+'-'+str(df["Final price"].max()))
      mean_price.append(np.median(df["Final price"]))
      overall_share.append(df["Revenue"].sum()/data["Revenue"].sum()*100)
      sku.append(df.shape[0])
      revenue_per_sku.append(df["Revenue"].sum()/df.shape[0])
      sku_with_sales.append(df[df["Sales"]>1].shape[0])
      percent_sku_with_sales.append(df[df["Sales"]>1].shape[0]/df.shape[0]*100)
      sku_over1m.append(df[df["Revenue"]>1000000].shape[0])
      sales.append(df["Sales"].sum())
      sales_over1m.append(df[df["Revenue"]>1000000]["Sales"].sum())
      share_sales_over1m.append(df[df["Revenue"]>1000000]["Sales"].sum()/df["Sales"].sum())
      revenue.append(df["Revenue"].sum())
      revenue_over1m.append(df[df["Revenue"]>1000000]["Revenue"].sum())
      share_revenue_over1m.append(df[df["Revenue"]>1000000]["Revenue"].sum()/df["Revenue"].sum())
      lost_profit.append(df["Lost profit"].sum())
      share_lost_profit.append(df["Lost profit"].sum()/df["Revenue"].sum()*100)
      group_a.append(df["Group A"].sum())
      share_group_a.append(df["Group A"].sum()/df.shape[0]*100)

  #create df
  final_ps = pd.DataFrame({"Диапазон": diapazon,"Ценовой сегмент": ranges, "Средняя цена": mean_price, "Доля в ТО": overall_share, "SKU всего": sku, "SKU с продажами >1млн" : sku_over1m,
                                 "Выручка на SKU": revenue_per_sku, "SKU с продажами": sku_with_sales, "% SKU с продажами": percent_sku_with_sales,
                                "Продажи": sales, "Продажи SKU >1млн": sales_over1m, "Доля продаж SKU >1млн": share_sales_over1m,
                                "Выручка": revenue, "Выручка SKU >1млн": revenue_over1m, "Доля выручки SKU >1млн": share_revenue_over1m,
                                "Упущенная выручка": lost_profit, "Доля упущенной выручки": share_lost_profit, "Товаров группы А": group_a,
                                "Доля товаров группы А": share_group_a})
  final_ps["Коэффициент"] = final_ps["Доля товаров группы А"]*final_ps["Выручка"]*final_ps["% SKU с продажами"]*final_ps["Упущенная выручка"]*final_ps["SKU с продажами >1млн"]*final_ps["Доля продаж SKU >1млн"]/1000000000000000000

  #return df
  return final_ps


def goods_list(t, data):
  #фильтр
  t = t.sort_values(by = "Коэффициент", ascending = False)
  df = data[data["Price range"] == t["Ценовой сегмент"][0]]

  proxy_df = df[["Name", "SKU", "Category", "Brand", "Seller", "Median price", "Sales", "Revenue", "Price range", "Lost profit", "Days with sales", "First Date"]]
  proxy_df["URL"] = proxy_df["SKU"].apply(lambda x: "https://www.wildberries.ru/catalog/"+str(x)+"/detail.aspx?targetUrl=SP")
  return proxy_df[:10]


def analisys(data):
  t = price_segmentation(data_preprocess(data))
  csv_file1 = t
  g = goods_list(t, data)
  csv_file2 = g
  return csv_file1, csv_file2


st.title("Аналитический отчет")
# Create a file uploader
uploaded_file = st.file_uploader("Select a CSV file", type=["csv"])
df_from_file = pd.read_csv(uploaded_file, sep = ";")
if uploaded_file is not None:
  file_contents = uploaded_file.read()
    
  # Process the uploaded file
  csv_file1, csv_file2 = analisys(df_from_file)

  # Display the output CSV files
  st.write("Ниже можно скачать крутые таблички :smile: ")
  st.write("Анализ ЦС:")
  st.write(csv_file1)
  #st.markdown(f"[Download]({csv_file1.to_csv})")  
  st.write("Список товаров:")
  st.write(csv_file2)
  #st.markdown(f"[Download]({csv_file2.to_csv})")  
if uploaded_file is None:
    st.stop()
