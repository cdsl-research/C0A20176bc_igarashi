import socket
import time
from math import ceil
import threading
import openpyxl
import numpy as np


excel_url = 'C:\\Users\\admin\\Desktop\\CDSL\\Lab\\python\\mUDP_10.xlsx'
book = openpyxl.load_workbook(excel_url)
sheet = book['Sheet1']

M_Group = "239.1.2.3"
LOCALHOST = socket.gethostbyname(socket.gethostname())
PORT = 1234

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


start = 0
end = [0]
file_d = ""
len_d = 0

# FILE_NAME = 'send_100k.txt'
FILE_NAME = 'send_500k.txt'
with open(FILE_NAME, 'r') as f:
    file_d = f.read()
    len_d = len(file_d)


# データ受信ループ関数
def recv_client(sock, addr):
	recv_seq_ary = []

	while sock:
		res_data = sock.recv(1024)

		recv_seq_ary = res_data.decode().split(",")
		recv_seq_ary.pop(-1)

		recv_seq_ary = list(map(int, recv_seq_ary))

		for i in recv_seq_ary:
			# chunk = file_d[(i-1)*10:(i-1)*10+10]
			chunk = file_d[(i-1)*1000:(i-1)*1000+1000]
			sock.send(chunk.encode())

		sock.close()
		end[0] = time.time()
		end.append(len(recv_seq_ary))
		sock=None


count=0
for i in range(2, 22):
	start = time.time()
	# chunks = [file_d[i:i+10] for i in range(0, len_d, 10)]
	chunks = np.array([file_d[i:i+1000] for i in range(0, len_d, 1000)])
	max_seq = str(ceil(len_d / 1000))

	for chunk in chunks:
		count+=1
		chunk = max_seq + ":" + str(count) + ":" + chunk
		udp_sock.sendto(chunk.encode(), (M_Group, PORT))
		time.sleep(0.001)


	while True:
		try:
			client, addr = tcp_sock.accept()

			thread = threading.Thread(target=recv_client, args=(client, addr))

			thread.start()
		except:
			break

	while len(end) < 6:
		end.append(0)

	cell = "K" + str(i)
	sheet[cell] = round(end[0] - start, 3)
	cell = "L" + str(i)
	sheet[cell] = end[1]
	cell = "M" + str(i)
	sheet[cell] = end[2]
	cell = "N" + str(i)
	sheet[cell] = end[3]
	# cell = "Z" + str(i)
	# sheet[cell] = end[4]
	# cell = "AA" + str(i)
	# sheet[cell] = end[4]
	count = 0
	print(f'{end[1:]} time: {round(end[0] - start, 3)}')
	end = [0]

	time.sleep(2)

book.save(excel_url)














