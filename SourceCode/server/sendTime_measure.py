import socket
import time
from math import ceil
import threading
import openpyxl
import numpy as np

M_Group = "239.1.2.3"
LOCALHOST = socket.gethostbyname(socket.gethostname())
target_IPs = ["192.168.100.122", "192.168.100.55", "192.168.100.194", "192.168.100.46", "192.168.100.147"]
PORT = 1234
SLEEP_TIME = 0.0001 # sending interval


excel_url = 'C:\\Users\\admin\\Desktop\\CDSL\\Lab\\python\\excel\\speed.xlsx'
book = openpyxl.load_workbook(excel_url)
# sheet = book['sleep_' + str(SLEEP_TIME)]
sheet = book['Sheet1']

# UDP Setting
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(LOCALHOST))
udp_sock.setsockopt(
    socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
    socket.inet_aton(M_Group) + socket.inet_aton(LOCALHOST)
)
# 自分の送ったマルチキャストパケットを自身で受け取らない
udp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)


# TCP Setting
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.settimeout(3)
tcp_sock.bind((LOCALHOST, PORT))
tcp_sock.listen(10)


recv_status = []
read_data = ""
data_len = 0

FILE_NAME = '../../SendFile/send_500k.txt'
with open(FILE_NAME, 'r') as f:
    read_data = f.read()
    data_len = len(read_data)


# データ受信ループ関数
def recv_client(sock, addr):

    while sock:
        res = sock.recv(1024)
        recv_id, res_time = res.decode().split(":")
        print(f"id: {recv_id} time: {res_time}")

        sock.close()
        recv_status.append({
            "recv_id": recv_id,
            "time": res_time
        })
        sock=None

seq = 1
for i in range(2, 52):
    start_t = time.time()
    chunks = np.array([read_data[j:j+1000] for j in range(0, data_len, 1000)])
    max_seq = str(ceil(data_len / 1000))

    for chunk in chunks:
        
        chunk = max_seq + ":" + str(seq) + ":" + chunk
        udp_sock.sendto(chunk.encode(), (M_Group, PORT))
        # time.sleep(SLEEP_TIME)

    while True:
        try:
            client, addr = tcp_sock.accept()
            thread = threading.Thread(target=recv_client, args=(client, addr))
            thread.start()
        except:
            break
        
    # 受信状況の記録
    for st in recv_status:

        # 受信機ID
        recv_id = st["recv_id"]
        # ロスしたパケットの内訳
        res_time = float(st["time"])

        cell = recv_id + str(i)

        if res_time < 0:
            sheet[cell] = "error"
        else:
            sheet[cell] = res_time

    time.sleep(2)

book.save(excel_url)














