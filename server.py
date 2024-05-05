import socket
'''
- アドレス情報をリストで保存しているが, ユーザー名とアドレスをハッシュマップで管理するように今後変更
- 各クライアントの最後のメッセージ送信時刻を追跡する昨日は今後実装．

'''

class UDPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.clients = []
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
            if (not client_address in self.clients):
                print("新しいユーザーです -> ", data.decode('utf-8'))
                self.clients.append(client_address)
                print(client_address)

            else:
                usernamelen = data[0] # 最初のバイトがユーザー名の長さを表す
                username = data[1:usernamelen + 1].decode() # ユーザー名を取得
                message = data[usernamelen + 1:].decode() # メッセージを取得
                print(f"{username}: {message}")
                self.relay_message(username + ": " + message) # 接続ユーザ全員に送信(送信元のユーザも含む)
    
    # リレーシステム
    def relay_message(self, message):
        for client_address in self.clients:
            self.sock.sendto(message.encode(), client_address)

    def start(self):
        self.handle_message()

if __name__ == "__main__":
    server_address = '0.0.0.0'
    server_port = 9001
    print('starting up on port {}'.format(server_port))
    server = UDPServer(server_address, server_port)
    server.start()

