from tkinter import *
import mysql.connector
from mysql.connector.errors import Error
from tkinter import ttk
from datetime import datetime
import math
import cv2
import numpy as np
import Preprocess
from collections import Counter
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
#lấy biển số
def run():
    ADAPTIVE_THRESH_BLOCK_SIZE = 19
    ADAPTIVE_THRESH_WEIGHT = 9

    Min_char_area = 0.015
    Max_char_area = 0.06

    Min_char = 0.01
    Max_char = 0.09

    Min_ratio_char = 0.25
    Max_ratio_char = 0.7

    max_size_plate = 18000
    min_size_plate = 5000

    RESIZED_IMAGE_WIDTH = 20
    RESIZED_IMAGE_HEIGHT = 30

    tongframe = 0
    biensotimthay = 0

    # Load KNN model
    npaClassifications = np.loadtxt("classifications.txt", np.float32)
    npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
    npaClassifications = npaClassifications.reshape(
        (npaClassifications.size, 1))  # reshape numpy array to 1d, necessary to pass to call to train
    kNearest = cv2.ml.KNearest_create()  # instantiate KNN object
    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
    bienso = []
    # Đọc video
    cap = cv2.VideoCapture(0)
    while (cap.isOpened()):

        # tiền xử lý ảnh
        ret, img = cap.read()
        tongframe = tongframe + 1
        # img = cv2.resize(img, None, fx=0.5, fy=0.5)
        imgGrayscaleplate, imgThreshplate = Preprocess.preprocess(img)
        canny_image = cv2.Canny(imgThreshplate, 250, 255)  # Tách biên bằng canny
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(canny_image, kernel,
                                iterations=1)  # tăng sharp cho egde (Phép nở). để biên canny chỗ nào bị đứt thì nó liền lại để vẽ contour

        # lọc vùng biển số
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]  # Lấy 10 contours có diện tích lớn nhất
        screenCnt = []
        for c in contours:
            peri = cv2.arcLength(c, True)  # Tính chu vi
            approx = cv2.approxPolyDP(c, 0.06 * peri, True)  # làm xấp xỉ đa giác, chỉ giữ contour có 4 cạnh
            [x, y, w, h] = cv2.boundingRect(approx.copy())
            ratio = w / h
            if (len(approx) == 4) and (0.8 <= ratio <= 1.5 or 4.5 <= ratio <= 6.5):
                screenCnt.append(approx)
        if screenCnt is None:
            detected = 0
            print("No plate detected")
        else:
            detected = 1

        if detected == 1:
            n = 1
            for screenCnt in screenCnt:

                ################## Tính góc xoay###############
                (x1, y1) = screenCnt[0, 0]
                (x2, y2) = screenCnt[1, 0]
                (x3, y3) = screenCnt[2, 0]
                (x4, y4) = screenCnt[3, 0]
                array = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                sorted_array = array.sort(reverse=True, key=lambda x: x[1])
                (x1, y1) = array[0]
                (x2, y2) = array[1]

                doi = abs(y1 - y2)
                ke = abs(x1 - x2)
                angle = math.atan(doi / ke) * (180.0 / math.pi)
                #################################################

                # Masking the part other than the number plate
                mask = np.zeros(imgGrayscaleplate.shape, np.uint8)
                new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )

                # Now crop
                (x, y) = np.where(mask == 255)
                (topx, topy) = (np.min(x), np.min(y))
                (bottomx, bottomy) = (np.max(x), np.max(y))

                roi = img[topx:bottomx + 1, topy:bottomy + 1]
                imgThresh = imgThreshplate[topx:bottomx + 1, topy:bottomy + 1]

                ptPlateCenter = (bottomx - topx) / 2, (bottomy - topy) / 2

                if x1 < x2:
                    rotationMatrix = cv2.getRotationMatrix2D(ptPlateCenter, -angle, 1.0)
                else:
                    rotationMatrix = cv2.getRotationMatrix2D(ptPlateCenter, angle, 1.0)

                roi = cv2.warpAffine(roi, rotationMatrix, (bottomy - topy, bottomx - topx))
                imgThresh = cv2.warpAffine(imgThresh, rotationMatrix, (bottomy - topy, bottomx - topx))

                roi = cv2.resize(roi, (0, 0), fx=3, fy=3)
                imgThresh = cv2.resize(imgThresh, (0, 0), fx=3, fy=3)

                # Tiền xử lý biển số

                kerel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                thre_mor = cv2.morphologyEx(imgThresh, cv2.MORPH_DILATE, kerel3)
                cont, hier = cv2.findContours(thre_mor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # Phân đoạn kí tự
                char_x_ind = {}
                char_x = []
                height, width, _ = roi.shape
                roiarea = height * width
                # print ("roiarea",roiarea)
                for ind, cnt in enumerate(cont):
                    area = cv2.contourArea(cnt)
                    (x, y, w, h) = cv2.boundingRect(cont[ind])
                    ratiochar = w / h
                    if (Min_char * roiarea < area < Max_char * roiarea) and (0.25 < ratiochar < 0.7):
                        if x in char_x:  # Sử dụng để dù cho trùng x vẫn vẽ được
                            x = x + 1
                        char_x.append(x)
                        char_x_ind[x] = ind

                # Nhận diện kí tự và in ra số xe
                if len(char_x) in range(7, 10):
                    cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

                    char_x = sorted(char_x)
                    strFinalString = ""
                    first_line = ""
                    second_line = ""

                    for i in char_x:
                        (x, y, w, h) = cv2.boundingRect(cont[char_x_ind[i]])
                        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        imgROI = thre_mor[y:y + h, x:x + w]  # cắt kí tự ra khỏi hình

                        imgROIResized = cv2.resize(imgROI,
                                                (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))  # resize lại hình ảnh
                        npaROIResized = imgROIResized.reshape(
                            (1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))  # đưa hình ảnh về mảng 1 chiều
                        # cHUYỂN ảnh thành ma trận có 1 hàng và số cột là tổng số điểm ảnh trong đó
                        npaROIResized = np.float32(npaROIResized)  # chuyển mảng về dạng float
                        _, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized,
                                                                                k=3)  # call KNN function find_nearest; neigh_resp là hàng xóm
                        strCurrentChar = str(chr(int(npaResults[0][0])))  # Lấy mã ASCII của kí tự đang xét
                        cv2.putText(roi, strCurrentChar, (x, y + 50), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 3)

                        if (y < height / 3):  # Biển số 1 hay 2 hàng
                            first_line = first_line + strCurrentChar
                        else:
                            second_line = second_line + strCurrentChar

                    strFinalString = first_line + second_line
                    #print( strFinalString )
                    bienso.append(strFinalString)
                    #print("\n License Plate " + str(n) + " is: " + first_line + " - " + second_line + "\n")
                    cv2.putText(img, strFinalString, (topy, topx), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 1)
                    n = n + 1
                    biensotimthay = biensotimthay + 1

                    cv2.imshow("a", cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))

        imgcopy = cv2.resize(img, (1280,720), fx=0.5, fy=0.5)
        cv2.imshow('License plate', imgcopy)
        # print("biensotimthay", biensotimthay)
        # print("tongframe", tongframe)
        # print("ti le tim thay bien so:", 100 * biensotimthay / (368), "%")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    counter = Counter(bienso)
    most_frequent_word =counter.most_common(1)[0][0]

    print(most_frequent_word)
    cap.release()
    cv2.destroyAllWindows()
    return most_frequent_word
#Update Gui khi nhấn nút Submit
def update_gui():
    # Lấy giá trị từ input field
    name = run()
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

    # Tạo lại các entries trong Table1 và Table2 để hiển thị các mục được thêm mới
    table1.delete(*table1.get_children())
    fetch_data_table1()

    table2.delete(*table2.get_children())
    fetch_data_table2()
    root.after(3000, update_gui) 

#Tạo GUI - Giao diện chương trình
root = Tk()
root.geometry('1000x400')
input_frame = Frame(root)
input_frame.pack(pady=20)
# # Mở camera và update
# clear_button = Button(input_frame, text="Start", command=update_gui)
# clear_button.pack(side=LEFT, padx=10)
#Khung Input Name
input_frame = Frame(root)
input_frame.pack(pady=20)

clear_button = Button(input_frame, text="Clear All Data", command=clear_data)
clear_button.pack(side=LEFT, padx=10)
input_frame = Frame(root)
input_frame.pack(pady=20)

clear_button = Button(input_frame, text="Exit", command=exit)
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
# Cập nhật GUI bằng cách lặp lại hàm update_gui() sau mỗi 3s
root.after(3000, update_gui) 
root.mainloop()