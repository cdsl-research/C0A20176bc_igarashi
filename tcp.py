import time
import socket
import numpy as np
import openpyxl


excel_url = 'C:\\Users\\admin\\Desktop\\CDSL\\Lab\\python\\TCP.xlsx'
book = openpyxl.load_workbook(excel_url)
sheet = book['Sheet1']

# "192.168.2.112", 
HOST_NAME = ["192.168.2.112", "192.168.2.113", "192.168.2.114", "192.168.2.111", "192.168.2.115"]
PORT = 1234
LOCALHOST = socket.gethostbyname(socket.gethostname())
# FILE_NAME = "send_100k.txt"
FILE_NAME = 'send_500k.txt'


# sock.settimeout(3)


file_d = ""
file_s = 0
with open(FILE_NAME, 'rb') as f:
  file_d = f.read()
  file_s = len(file_d)



for i in range(2, 22):
    end = 0
    start = time.time()
    for ip in HOST_NAME:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # sock.settimeout(3)
      sock.connect((ip, PORT))

      chunks = np.array([file_d[i:i+1000] for i in range(0, file_s, 1000)])

      for chunk in np.nditer(chunks):
          sock.send(chunk)

      sock.close()
  
    end = time.time()

    cell = "T" + str(i)
    sheet[cell] = round(end - start, 3)
    print(round(end - start, 3))
        
    time.sleep(1.5)

# 一台の場合
# for i in range(2, 52):

#     start = time.time()
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect((HOST_NAME[0], PORT))

#     chunks = np.array([file_d[i:i+1000] for i in range(0, file_s, 1000)])

#     for chunk in np.nditer(chunks):
#         sock.send(chunk)

#     sock.close()
#     end = time.time()
    
#     cell = "A" + str(i)
#     sheet[cell] = round(end - start, 3)
        
#     time.sleep(0.4)
    
book.save(excel_url)
