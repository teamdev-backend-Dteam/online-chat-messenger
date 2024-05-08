import socket
import secrets
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

class TCPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.server_address, self.server_port))
    
    def start(self):
        self.sock.listen()
        connection, client_address = self.sock.accept()
        header = connection.recv(32)
        room_name_size = int.from_bytes(header[0], "big")
        operation = int.from_bytes(header[1], "big")
        state = int.from_bytes(header[2], "big")
        body = int.from_bytes(header[3:], "big")
        room_name = body[:room_name_size]

        # 接続してきたクライアントからオペレーションコードを受け取る
        # 新しいチャットルームを作成する
        if operation == 1:
            self.create_chatroom()
        # ルーム名と必要であればパスワードを入力して既存のチャットルームに入る
        elif operation == 2:
            self.join_chatroom()

        # 特定のクライアントトークンを生成して、クライアントに送り、TCP接続を閉じる
        token = self.genereate_token()
        self.sock.send(token)
        # クライアントはトークンを使い、UDPを経由してサーバーが管理するチャットルームに接続する
        '''
        Chatroomが以下を管理する
        チャットルームの構成
        rooms = {
            ルーム名：[(address, token), ...]
        }

        serverは送られたデータからどのROOMか判断し、メッセージを転送する
        '''
    def genereate_token():
        return secrets.token_bytes()

    def create_chatroom():
        chatroom.create_room()

    def join_chatroom():
        chatroom.add_member()


class Chatroom:
    def __init__(self):
        self.rooms = {}
        self.clients_token = {}

    def add_client(self, client_address, token):
        self.client_address = client_address
        self.token = token

    def create_room(self, room_name, client_address, client_port):
        self.rooms[room_name] = (client_address, client_port)
        return

    def add_member(self, room_name, client_address, client_port):
        self.rooms[room_name].append((client_address, client_port))
        return

    def is_valid_token(self, client_address, token):
        if self.client_token[client_address] == token:
            return True
        return False
    
    
if __name__ == "__main__":
    server_address = '0.0.0.0'
    server_port = 9001
    print('starting up on port {}'.format(server_port))
    server = UDPServer(server_address, server_port)
    server.start()
    
    chatroom = Chatroom()

    tcp_server = TCPServer(server_address, server_port)
    tcp_server.start()
