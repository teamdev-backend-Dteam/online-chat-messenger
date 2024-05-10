import socket
import secrets
import threading
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
        self.handle_message()


    def handle_message(self):
        while True:
            self.sock.listen()
            connection, client_address = self.sock.accept()

            header = connection.recv(32)
            room_name_size = int.from_bytes(header[:1], "big")
            operation = int.from_bytes(header[1:2], "big")
            state = int.from_bytes(header[2:3], "big")
            body = header[3:]
            room_name = body[:room_name_size].decode('utf-8')

            # 特定のクライアントトークンを生成して、クライアントに送り、TCP接続を閉じる
            token = self.generate_token()

            address, port = client_address
            # 接続してきたクライアントからオペレーションコードを受け取る
            # 新しいチャットルームを作成する
            if operation == 1:
                chatroom.create_room(room_name, address, token)

            # ルーム名と必要であればパスワードを入力して既存のチャットルームに入る
            elif operation == 2:
                print('address {}'.format(address))
                chatroom.join_chatroom(room_name, address, token)

            room_name_byte = body[:room_name_size]
            room_name_len = len(room_name_byte).to_bytes(1, "big")
            connection.send(room_name_len + room_name_byte + token)
            connection.close()
            # クライアントはトークンを使い、UDPを経由してサーバーが管理するチャットルームに接続する
            '''
            Chatroomが以下を管理する
            チャットルームの構成
            rooms = {
                ルーム名：[(address, token), ...]
            }

            serverは送られたデータからどのROOMか判断し、メッセージを転送する
            '''
        
    def generate_token(self):
        token = secrets.token_bytes()
        return token



class Chatroom:
    def __init__(self):
        self.rooms = {}

    # 新しいチャットルームの作成
    def create_room(self, room_name, address, token):
        # すでに存在する名前の場合は失敗を返信
        if room_name in self.rooms:
            # 失敗通知する
            print('ルーム {} は既に存在しています'.format(room_name))
            return
        # ルームにアドレスとトークンを保存する
        self.rooms[room_name] = {address: token}
        print('ルーム {} が作成されました'.format(room_name))
        return

    # 既存のチャットルームに参加する
    def join_chatroom(self, room_name, address, token):
        if room_name not in self.rooms:
            print('ルーム： {} が見つかりませんでした'.format(room_name))
            return
        
        if address in self.rooms[room_name]:
            print('既にルームに参加しています')
            return
        self.rooms[room_name].append({address: token})
        print('ルーム "{}" に参加しました'.format(room_name))
        return

    def is_valid_token(self, room_name, address, token):
        if address in self.rooms[room_name]:
            return True
        return False

if __name__ == "__main__":
    server_address = '0.0.0.0'
    server_port = 9001
    print('starting up on port {}'.format(server_port))
    udp_server = UDPServer(server_address, server_port)
    tcp_server = TCPServer(server_address, server_port)
    chatroom = Chatroom()

    # UDP用
    thread_udp = threading.Thread(udp_server.start())
    thread_udp.start()
    # TCP接続用
    thread_tcp = threading.Thread(tcp_server.start())
    thread_tcp.start()
    thread_udp.join()
    thread_tcp.join()