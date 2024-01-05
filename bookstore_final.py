import streamlit as st
from datetime import datetime
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import copy
import os
import json


# 讀取設定檔
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

import toml
from toml import TomlDecodeError

# 初始化身份驗證
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
#global login
#login = 0

# 初始化使用者資訊
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "shopping_cart": [],
        "order_history": [],
        "group_buy":[]
    }

# 用戶訂單歷史檔案路徑
orders_path = "./orders/"

# 確保訂單目錄存在
if not os.path.exists(orders_path):
    os.makedirs(orders_path) 

# 加載用戶訂單歷史
def load_user_order_history(username):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        return pd.read_csv(order_history_file)
    return pd.DataFrame(columns=["title", "quantity"])

# 保存用戶訂單歷史
def save_user_order_history(username, current_orders):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        # 如果檔案已存在，則讀取並附加新訂單
        existing_orders = pd.read_csv(order_history_file)
        updated_orders = pd.concat([existing_orders, pd.DataFrame(current_orders)], ignore_index=True)
    else:
        # 如果檔案不存在，則創建新的 DataFrame
        updated_orders = pd.DataFrame(current_orders)
    
    # 保存更新後的訂單歷史
    updated_orders.to_csv(order_history_file, index=False)



def login_page():
    # 在登入頁面以對話框的形式顯示用戶消息
    page =  st.sidebar.radio("選擇頁面", [  "商品總覽", "團購", "購物車", "歷史訂單", "留言板"])
    if page == "商品總覽":
        view_products()
    elif page == "歷史訂單":        
        order_history()
    elif page == "購物車":
            shopping_cart_page()
    elif page == "留言板":
        message_board()
    elif page == "團購":
        groupbuy_page()

    

import csv

csv_file_path = 'book.csv'

# 讀取CSV檔案，將資料存入DataFrame

books = pd.read_csv(csv_file_path)


# 初始化 session_state
if "shopping_cart" not in st.session_state:
    st.session_state.shopping_cart = []
if "group_buy" not in st.session_state:
    st.session_state.group_buy = []


# 定義各頁面
    
# 首頁
def home():
    st.title("麗文校園網")
    st.write("歡迎光臨麗文校園電商平台！")

    st.error("同學你好,現在起,團購數量超過10本即可享9折優惠喔~~快去找同學一起團購吧")



# 商品總覽
def view_products():
    st.title("商品總覽")

    for i in range(0, len(books)):
        st.write(f"## {books.at[i, 'title']}")
        st.image(books.at[i, "image"], caption=books.at[i, "title"], width=300)  
        st.write(f"**作者:** {books.at[i, 'author']}")
        st.write(f"**類型:** {books.at[i, 'genre']}")
        st.write(f"**原價:** {books.at[i, 'price']}")
        st.write(f"**九折價:** {books.at[i, 'discount']}")
        
        quantity = st.number_input(f"購買書籍編號 {i}數量", min_value=1, value=1, key=f"quantity_{i}")

        if st.button(f"購買 {books.at[i, 'title']}", key=f"buy_button_{i}"):
            if "shopping_cart" not in st.session_state:
                st.session_state.shopping_cart = []
            st.session_state.shopping_cart.append({
                "title": books.at[i, "title"],
                "quantity": quantity,
                "total_price" : int(books.at[i, 'price']) * int(quantity)  # Total price calculation
            })
            st.info(f"已將 {quantity} 本 {books.at[i, 'title']} 加入購物車")

        #新增團購按鈕
        quantity_group = st.number_input(f"登記書籍編號 {i} 數量", min_value=1, value=1, key=f"quantity_group_{i}")

        if st.button(f"團購 {books.at[i, 'title']}", key=f"group_button_{i}"):
            if "group_buy" not in st.session_state:
                st.session_state.group_buy = []
            #確認是否開團
            existing_group = next((group for group in st.session_state.group_buy if group["書名"] == books.at[i, "title"]), None)
            if existing_group:
                existing_group["我的團購"] = quantity_group
                existing_group["目前累計"] += quantity_group
                existing_group["總金額"] = int(existing_group["目前累計"]) * int(books.at[i, 'discount'])  # Updated total price calculation
            else:
                st.session_state.group_buy.append({
                    "書名": books.at[i, "title"],
                    "我的團購": quantity_group,
                    "目前累計": quantity_group,  # Start with the current quantity
                    "開團時間": date_range,
                    "總金額": int(int(books.at[i, 'discount']) * int(quantity_group) )  # Total price calculation
                })
            st.success(f"已成功登記 {quantity_group} 本 {books.at[i, 'title']}") 
        
        st.write("---")

# 團購區間限時設定
from datetime import datetime, timedelta
order_date = datetime.now()

# 計算結束日期（下單日的基礎上加上三天）
end_date = order_date + timedelta(days=2)  # 2代表三天減一

# 顯示區間字符串
date_range = f"{order_date.strftime('%m/%d')} ~ {end_date.strftime('%m/%d')}"

    
# 顯示訂單
def display_order():
    st.title("訂單明細")

    # 顯示購物車中的商品
    for item in st.session_state.shopping_cart:
        st.write(f"{item['quantity']} 本 {item['title']}")

    # 顯示其他訂單相關資訊，例如總金額、訂單時間等
    total_expense = sum(item["total_price"] for item in st.session_state.shopping_cart)
    st.write(f"總金額: {total_expense}")

    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"訂單時間: {order_time}")

#顯示團購訂單
def display_order_group():
    st.title("團購訂單明細")

    # 顯示團購的商品
    for item in st.session_state.group_buy:
        st.write(f"{item['我的團購']} 本 {item['書名']}")

    # 顯示其他訂單相關資訊，例如總金額、訂單時間等
    total_expense = sum(item["總金額"] for item in st.session_state.group_buy)
    st.write(f"總金額: {total_expense}")

    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"訂單時間: {order_time}")

# 購物車頁面
def shopping_cart_page():
    st.title("購物車")
    
    if not st.session_state.shopping_cart:
        st.write("購物車是空的，快去選購您喜歡的書籍吧！")
    else:
        #整理名稱相同的書籍
        cart_dict = {}
        for item in st.session_state.shopping_cart:
            title = item["title"]
            #如果書第一次出現，則...
            if title not in cart_dict:
                cart_dict[title] = {
                    "quantity": item["quantity"],
                    "total_price": item["total_price"]
                }
            else:
                cart_dict[title]["quantity"] += item["quantity"]
                cart_dict[title]["total_price"] += item["total_price"]

        # create new shopping cart data（整理後的
        cart_data = []
        for title, details in cart_dict.items():
            cart_data.append({"title": title, "quantity": details["quantity"], "total_price": details["total_price"]})

        # display as table
        cart_df = pd.DataFrame(cart_data)
        st.table(cart_df)

        pay = st.button('結帳')

        if pay:
            st.session_state.show_payment = True
        if 'show_payment' in st.session_state and st.session_state.show_payment:
            Payment_page()
        
            

#新增團購頁面
def groupbuy_page():
    st.title("團購頁面")
    st.write("團購資訊")

    if not st.session_state.group_buy:
        st.write("尚未加入團購，快去找同學揪團吧！")
    else:
        # Create a Pandas DataFrame from the group buying data
        df = pd.DataFrame(st.session_state.group_buy)

        # Display the DataFrame as a table
        st.table(df)

        confirm = st.button('確認團購')
        if confirm:
            total_group_buy_quantity = sum(item["目前累計"] for item in st.session_state.group_buy)
            if total_group_buy_quantity >= 10:
                st.success("恭喜！團購數量已達到10本。")
                st.session_state.confirm_group_buying = True
            else:
                st.warning(f"目前團購數量為 {total_group_buy_quantity} 本，還差 {10 - total_group_buy_quantity} 本達成目標。請繼續邀請更多人參加。")
                
            # 如果確認，執行結帳頁面
        if 'confirm_group_buying' in st.session_state and st.session_state.confirm_group_buying:
            Payment_page_group()
 


# 結帳頁面
def Payment_page():
    st.title("結帳")
    with st.form(key="購物清單") as form:
        購買詳情 = display_order()
        付款方式 = st.selectbox('請選擇付款方式', ['信用卡', 'Line Pay'])
        優惠碼 = st.text_input('優惠代碼')
        寄送方式 = st.selectbox('請選擇寄送方式', ['寄送到府', '寄送至指定便利商店'])
        
        submitted = st.form_submit_button("確認付款")
        
    if submitted:
        order_history_df = pd.DataFrame(st.session_state.shopping_cart)
            # 保存用戶訂單歷史
        save_user_order_history(st.session_state.user_info["name"], order_history_df)
        st.session_state.shopping_cart = []
        st.write("交易成功！")
        st.balloons()

#結帳頁面_團購
def Payment_page_group():
    st.title("結帳")
    with st.form(key="購物清單") as form:
        購買詳情 = display_order_group()
        付款方式 = st.selectbox('請選擇付款方式', ['信用卡', 'Line Pay'])
        優惠碼 = st.text_input('優惠代碼')
        寄送方式 = st.selectbox('請選擇寄送方式', ['寄送到府', '寄送至指定便利商店'])
        
        submitted = st.form_submit_button("確認付款")
        
    if submitted:
        order_history_df = pd.DataFrame(st.session_state.group_buy)
            # 保存用戶訂單歷史
        save_user_order_history(st.session_state.user_info["name"], order_history_df)
        st.session_state.group_buy = []
        st.write("交易成功！")
        st.snow()

        

# 留言頁
def message_board():
    # 初始化 session_state
    if "past_messages" not in st.session_state:
        st.session_state.past_messages = []

    # 在應用程式中以對話框的形式顯示用戶消息
    with st.chat_message("user"):
        st.write("歡迎來到留言板！")

    # 接收用戶輸入
    prompt = st.text_input("在這裡輸入您的留言")

    # 如果用戶有輸入，則將留言加入 session_state 中
    if prompt:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.past_messages.append({"user": "user", "message": f"{timestamp} - {prompt}"})

    # 留言板中顯示過去的留言
    with st.expander("過去的留言"):
        # 顯示每條留言
        for message in st.session_state.past_messages:
            with st.chat_message(message["user"]):
                st.write(message["message"])



# 訂單歷史頁面
def order_history():
    st.title("訂單歷史")
    # 將訂單資料轉換為 DataFrame
    df = load_user_order_history(st.session_state.user_info["name"])

    # 顯示表格
    st.table(df)

def main():
    
    st.title("麗文校園網")
    st.write("歡迎光臨麗文校園電商平台！")   
    st.image("https://allez.one/wp-content/uploads/2022/04/%E9%9B%BB%E5%95%86%E7%B6%93%E7%87%9F1.jpg")
    st.session_state.login = False
    st.error("同學你好,現在起,團購數量超過10本即可享9折優惠喔~~快去找同學一起團購吧")
    # 登入
    name, authentication_status, username = authenticator.login('Login', 'main')
    st.session_state.login = authentication_status
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.session_state.user_info["name"] = name
        # 加載用戶訂單歷史
        st.session_state.user_info["order_history"] = load_user_order_history(username)
        st.write(f'Welcome *{name}*')  
        login_page()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()



