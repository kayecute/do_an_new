from tkinter import *
import mysql.connector
from mysql.connector.errors import Error
from tkinter import ttk
from datetime import datetime
import math
#Kết nối database
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pankaye9x!",
        database="newdb"
    )
    print("Database connected successfully")
except Error as e:
    print(e)

#Tạo Table1 và Table2 (nếu Table chưa tồn tại)
cursor = mydb.cursor()
try:
    cursor.execute("""CREATE TABLE Table1 ( 
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        ten VARCHAR(255),
                        ngay_vao DATETIME)""")
    cursor.execute("""CREATE TABLE Table2 ( 
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        ten VARCHAR(255),
                        ngay_vao DATETIME,
                        ngay_ra DATETIME,
                        tien_tra int)""")
    print("Tables created successfully")
except Error as e:
    print("Tables already exist")

#Hàm để lấy dữ liệu table vào Output 1
def fetch_data_table1():
    sql = 'SELECT * FROM Table1;'
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        table1.insert("", "end", text=row[0], values=(row[0], row[1], row[2]))

#Hàm để lấy dữ liệu table vào Output 2
def fetch_data_table2():
    sql = 'SELECT * FROM Table2;'
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        table2.insert("", "end", text=row[0], values=(row[0], row[1], row[2], row[3] , row[4]))
def clear_data():
    # Xóa dữ liệu của bảng 1
    cursor.execute("DELETE FROM Table1")
    mydb.commit()
    table1.delete(*table1.get_children())

    # Xóa dữ liệu của bảng 2
    cursor.execute("DELETE FROM Table2")
    mydb.commit()
    table2.delete(*table2.get_children())
#Update Gui khi nhấn nút Submit
def update_gui():
    # Lấy giá trị từ input field
    name = entry.get()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Kiểm tra tên đã có trong bảng 1 hay không
    cursor.execute("SELECT COUNT(*) FROM Table1 WHERE ten = %s", (name,))
    
    if cursor.fetchone()[0] == 0:
        # Thêm mới tên vào bảng 1
        cursor.execute("INSERT INTO Table1 (ten, ngay_vao) VALUES (%s, %s)", (name, now))
        mydb.commit()
    else:   
        # Nếu tên đã tồn tại trong Table1 thì chỉ thực hiện việc chuyển dữ liệu sang Table2  
        
        # Lấy dữ liệu của name đó trong Table1
        cursor.execute("SELECT * FROM Table1 WHERE ten = %s LIMIT 1", (name,))
        data = cursor.fetchone()
        id_table1 = data[0]
        ngay_vao_table1 = data[2]

        # Xóa dữ liệu của name đó sang bảng 1
        cursor.execute("DELETE FROM Table1 WHERE ten = %s", (name,))
        mydb.commit()

        # Tính giá trị tiền trả cho name thông qua ngày vào/ra.
        ngay_ra_table2 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ngay_vao_table2 = datetime.strptime(str(ngay_vao_table1), '%Y-%m-%d %H:%M:%S')
        so_gio = math.ceil((datetime.strptime(ngay_ra_table2, '%Y-%m-%d %H:%M:%S') - ngay_vao_table2).seconds / 3600)
        tien_tra = int(so_gio * 10000)

        # Thêm mới dữ liệu của name đó sang bảng 2 với giá trị tiền trả tính toán được
        cursor.execute("INSERT INTO Table2 (ten, ngay_vao, ngay_ra, tien_tra) VALUES (%s, %s, %s, %s)", 
                       (name, ngay_vao_table1, ngay_ra_table2, tien_tra))
        mydb.commit()

    # Xóa Input Field sau khi Submit
    entry.delete(0, END)

    # Tạo lại các entries trong Table1 và Table2 để hiển thị các mục được thêm mới
    table1.delete(*table1.get_children())
    fetch_data_table1()

    table2.delete(*table2.get_children())
    fetch_data_table2()


#Tạo GUI - Giao diện chương trình
root = Tk()
root.geometry('1200x400')

#Khung Input Name
input_frame = Frame(root)
input_frame.pack(pady=20)

# label = Label(input_frame, text="Name: ")
# label.pack(side=LEFT, padx=10)

# entry = Entry(input_frame)
# entry.pack(side=LEFT, padx=10)

button = Button(input_frame, text="Submit", command=update_gui)
button.pack(side=LEFT, padx=10)
clear_button = Button(input_frame, text="Clear All Data", command=clear_data)
clear_button.pack(side=LEFT, padx=10)
#Khung Output Tables
output_frame = Frame(root)
output_frame.pack(pady=20)

#Table 1
table1_frame = Frame(output_frame)
table1_frame.pack(side=LEFT, padx=20, pady=10)

Label(table1_frame, text="Bảng 1").pack(pady=5)

table1_headers = ["ID", "Tên", "Ngày Vào"]
table1 = ttk.Treeview(table1_frame, columns=table1_headers, show="headings")

for header in table1_headers:
    table1.heading(header, text=header.title())
    table1.column(header, width=120)

table1.pack(fill=BOTH, expand=YES)

fetch_data_table1()

#Table 2
table2_frame = Frame(output_frame)
table2_frame.pack(side=RIGHT, padx=20, pady=10)

Label(table2_frame, text="Bảng 2").pack(pady=5)

table2_headers = ["ID", "Tên", "Ngày Vào", "Ngày Ra" ,"Tiền Trả"]
table2 = ttk.Treeview(table2_frame, columns=table2_headers, show="headings")

for header in table2_headers:
    table2.heading(header, text=header.title())
    table2.column(header, width=120)

table2.pack(fill=BOTH, expand=YES)

fetch_data_table2()
root.mainloop()