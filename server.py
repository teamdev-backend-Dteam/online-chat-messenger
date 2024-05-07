import socket
import threading
import time

class UDPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        # self.clients = []
        self.clientsmap = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.server_address, self.server_port))
        print("サーバが起動しました")
        print('waiting to receive message')
        print("--------------------------")
    
    # クライアントからのメッセージ受信処理 及び 他ユーザへの送信
    def handle_message(self):
        while True:

            data, client_address = self.sock.recvfrom(4096) # 最大4096byteのデータを受信
            # 新しいクライアントからの受信 -> clientsリストにアドレスを保存
            if (not client_address in self.clientsmap):
                name = data.decode('utf-8')
                # print("新しいユーザーです -> ", name)
                # self.clients.append(client_address)
                self.clientsmap.update({client_address : [name, time.time()]})
                #print(client_address)
                #print("新しいユーザーです -> ", self.clientsmap[client_address], time.ctime())
                print("新しいユーザーです -> ", name)

            else:
                self.clientsmap[client_address][1] = time.time() # クライアントの最終送信時刻を更新
                usernamelen = data[0] # 最初のバイトがユーザー名の長さを表す
                username = data[1:usernamelen + 1].decode() # ユーザー名を取得
                message = data[usernamelen + 1:].decode() # メッセージを取得
                print(f"{username}: {message}")
                self.relay_message(username + ": " + message) # 接続ユーザ全員に送信(送信元のユーザも含む)
    
    # リレーシステム
    def relay_message(self, message):
        for client_address in self.clientsmap.keys():
            self.sock.sendto(message.encode(), client_address)
    
    # 各クライアントの最後のメッセ時送信時刻を追跡
    def send_time_tracking(self):
        while True:
            time.sleep(60)# 1分単位で追跡
            print("スリープ解除")
            try:
                for address, value in self.clientsmap.items():
                    send_time = value[1]
                    if (time.time() - send_time > 300): # クライアントからの通信が5分なければclientsmapから情報を削除
                        self.clientsmap.pop(address)
                        self.sock.sendto("Timeout!".encode(), address)
                        print(value[0], address, "connection has been lost.")
            except Exception as e: # ハッシュマップの中身がない時のエラー処理
                pass

    def start(self):
        thread_main = threading.Thread(target = self.handle_message)
        thread_tracking = threading.Thread(target = self.send_time_tracking)
        thread_main.start()
        thread_tracking.start()
        thread_main.join()
        thread_tracking.join()

if __name__ == "__main__":
    server_address = '0.0.0.0'
    server_port = 9001
    print('starting up on port {}'.format(server_port))
    server = UDPServer(server_address, server_port)

    server.start()