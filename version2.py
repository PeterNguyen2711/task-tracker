import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Task Tracker", layout="wide")
st.title("📋 Task Tracker")

# Khởi tạo file nếu chưa có
file_path = "task.csv"
columns = ["TaskID", "Title", "AssignedTo", "KPI", "Priority", "Status", "Deadline", "Note"]

if not os.path.exists(file_path):
    df = pd.DataFrame(columns=columns)
    df.to_csv(file_path, index=False)
else:
    df = pd.read_csv(file_path)

# Sidebar chọn vai trò
role = st.sidebar.radio("🔑 Vai trò:", ["Người dùng", "Quản lý"])

# Hàm thêm task mới
def add_task(title, assigned_to, kpi, priority, status, deadline, note):
    new_id = df["TaskID"].max() + 1 if not df.empty else 1
    new_task = {
        "TaskID": new_id,
        "Title": title,
        "AssignedTo": assigned_to,
        "KPI": kpi,
        "Priority": priority,
        "Status": status,
        "Deadline": deadline.strftime("%Y-%m-%d"),
        "Note": note
    }
    updated_df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
    updated_df.to_csv(file_path, index=False)
    st.success(f"✅ Đã thêm task mới cho {assigned_to}")
    st.rerun()

# Người dùng
if role == "Người dùng":
    st.sidebar.header("🔍 Bộ lọc")

    # Bộ lọc theo người và priority
    selected_user = st.sidebar.selectbox("Chọn nhân viên:", df["AssignedTo"].dropna().unique())
    selected_priority = st.sidebar.multiselect(
        "Chọn mức độ ưu tiên:",
        options=df["Priority"].dropna().unique(),
        default=df["Priority"].dropna().unique()
    )

    filtered_df = df[
        (df["AssignedTo"] == selected_user) &
        (df["Priority"].isin(selected_priority))
    ]

    st.subheader(f"Các task của {selected_user}")
    st.dataframe(filtered_df)

    st.subheader("📈 Thống kê trạng thái task")
    status_count = filtered_df["Status"].value_counts()
    st.bar_chart(status_count)
    st.success(f"Tổng số task: {len(filtered_df)}")

    # Thêm task mới
    st.sidebar.markdown("---")
    st.sidebar.header("➕ Thêm task mới")

    with st.sidebar.form("new_task_form"):
        title = st.text_input("Tiêu đề task")
        assigned_to = st.text_input("Người phụ trách")
        kpi = st.text_input("KPI")
        priority = st.selectbox("Mức độ ưu tiên", ["High", "Medium", "Low"])
        status = st.selectbox("Trạng thái", ["To Do", "In Progress", "Done"])
        deadline = st.date_input("Hạn chót", value=date.today())
        note = st.text_area("Ghi chú")
        submitted = st.form_submit_button("✅ Thêm task")

        if submitted:
            add_task(title, assigned_to, kpi, priority, status, deadline, note)

    st.markdown("---")
    st.header("🛠️ Cập nhật trạng thái task")

    if not df.empty:
        df["Label"] = df["TaskID"].astype(str) + " - " + df["Title"] + " - " + df["AssignedTo"]
        task_to_update = st.selectbox("Chọn task để cập nhật:", df["Label"])
        selected_row = df[df["Label"] == task_to_update]
        current_status = selected_row["Status"].values[0]

        new_status = st.selectbox("Chọn trạng thái mới:", ["To Do", "In Progress", "Done"],
                                  index=["To Do", "In Progress", "Done"].index(current_status))

        if st.button("💾 Cập nhật trạng thái"):
            df.loc[selected_row.index, "Status"] = new_status
            df.drop(columns="Label", inplace=True)
            df.to_csv(file_path, index=False)
            st.success("✅ Cập nhật trạng thái thành công!")
            st.rerun()
    else:
        st.info("Chưa có task nào để cập nhật.")

# Quản lý
elif role == "Quản lý":
    st.subheader("📊 Tổng quan task toàn team")
    st.dataframe(df)

    st.markdown("---")
    st.subheader("📌 Cập nhật độ ưu tiên (Priority)")

    df["Label"] = df["TaskID"].astype(str) + " - " + df["Title"] + " - " + df["AssignedTo"]
    task_to_edit = st.selectbox("Chọn task để chỉnh Priority:", df["Label"])
    selected_row = df[df["Label"] == task_to_edit]
    current_priority = selected_row["Priority"].values[0]

    new_priority = st.selectbox("Chọn Priority mới:", ["High", "Medium", "Low"],
                                index=["High", "Medium", "Low"].index(current_priority))

    if st.button("🚦 Cập nhật Priority"):
        df.loc[selected_row.index, "Priority"] = new_priority
        df.drop(columns="Label", inplace=True)
        df.to_csv(file_path, index=False)
        st.success("✅ Đã cập nhật Priority!")
        st.rerun()

    st.markdown("---")
    st.subheader("➕ Giao task mới")

    with st.form("assign_task_form"):
        title = st.text_input("Tiêu đề task")
        assigned_to = st.text_input("Giao cho")
        kpi = st.text_input("KPI")
        priority = st.selectbox("Mức độ ưu tiên", ["High", "Medium", "Low"], key="assign_priority")
        status = st.selectbox("Trạng thái", ["To Do", "In Progress", "Done"], key="assign_status")
        deadline = st.date_input("Hạn chót", key="assign_deadline", value=date.today())
        note = st.text_area("Ghi chú", key="assign_note")
        assign_submit = st.form_submit_button("📤 Giao task")

        if assign_submit:
            add_task(title, assigned_to, kpi, priority, status, deadline, note)

st.subheader("📂 Bộ lọc theo nhân viên")
selected_manager_user = st.selectbox("Chọn nhân viên:", ["Tất cả"] + sorted(df["AssignedTo"].dropna().unique().tolist()))

if selected_manager_user != "Tất cả":
    view_df = df[df["AssignedTo"] == selected_manager_user]
else:
    view_df = df

st.dataframe(view_df)

st.markdown("---")
st.subheader("🛠️ Cập nhật KPI và Deadline")

task_to_edit_info = st.selectbox("Chọn task:", df["Label"], key="kpi_edit")
selected_row_edit = df[df["Label"] == task_to_edit_info]

current_kpi = selected_row_edit["KPI"].values[0]
current_deadline = pd.to_datetime(selected_row_edit["Deadline"].values[0])

new_kpi = st.text_input("KPI mới:", value=current_kpi)
new_deadline = st.date_input("Deadline mới:", value=current_deadline)

if st.button("📆 Cập nhật KPI & Deadline"):
    df.loc[selected_row_edit.index, "KPI"] = new_kpi
    df.loc[selected_row_edit.index, "Deadline"] = new_deadline.strftime("%Y-%m-%d")
    df.drop(columns="Label", inplace=True)
    df.to_csv(file_path, index=False)
    st.success("✅ Đã cập nhật KPI và Deadline!")
    st.rerun()

from datetime import datetime, timedelta

def highlight_deadline(row):
    try:
        deadline = pd.to_datetime(row["Deadline"])
        today = datetime.today()
        if deadline < today:
            return ['background-color: #ffcccc'] * len(row)  # Đỏ nhạt
        elif deadline <= today + timedelta(days=2):
            return ['background-color: #fff3cd'] * len(row)  # Vàng nhạt
        else:
            return [''] * len(row)
    except:
        return [''] * len(row)

st.subheader("🗂️ Task với màu cảnh báo")
st.dataframe(view_df.style.apply(highlight_deadline, axis=1))

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# --- THÔNG TIN GMAIL NGƯỜI GỬI ---
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# --- ĐỌC TASK CSV ---
df = pd.read_csv("task.csv")

# --- TÍNH NGÀY HÔM NAY ---
today = datetime.today()
warning_days = 2  # Gửi email nếu task sắp hết hạn trong 2 ngày

# --- DUYỆT CÁC TASK GẦN ĐẾN HẠN / QUÁ HẠN ---
for idx, row in df.iterrows():
    try:
        deadline = datetime.strptime(row["Deadline"], "%Y-%m-%d")
        delta = (deadline - today).days
        if row["Status"] != "Done" and delta <= warning_days:
            # Tạo nội dung email
            receiver_email = f"{row['AssignedTo'].replace(' ', '').lower()}@yourcompany.com"  # Tùy chỉnh email người nhận
            subject = f"[NHẮC NHỞ] Task sắp đến hạn: {row['Title']}"
            body = f"""
Xin chào {row['AssignedTo']},

Bạn có task: **{row['Title']}**
- Trạng thái: {row['Status']}
- Hạn chót: {row['Deadline']}
- Mức độ ưu tiên: {row['Priority']}
- Ghi chú: {row['Note']}

Vui lòng cập nhật hoặc hoàn thành task đúng hạn!

Trân trọng,
Hệ thống Task Tracker
            """

            # Gửi email
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            print(f"📧 Đã gửi nhắc nhở cho {receiver_email}")
    except Exception as e:
        print(f"Lỗi gửi mail cho task: {row['Title']} - {e}")
