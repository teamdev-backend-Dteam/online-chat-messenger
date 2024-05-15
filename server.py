import socket
import threading
import time
import secrets

'''
- アドレス情報をリストで保存しているが, ユーザー名とアドレスをハッシュマップで管理するように今後変更
- 各クライアントの最後のメッセージ送信時刻を追跡する昨日は今後実装．

'''

class UDPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
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
            room_name_size = data[0]
            token_size = data[1]
            room_name = data[2:2 + room_name_size].decode()
            token = data[2 + room_name_size:2 + room_name_size + token_size]
            message = data[2 + room_name_size + token_size:].decode()
            address = client_address[0] # アドレスのみを取得
            if self.is_valid_token(room_name, address, token):
                print(f'Message from {client_address} in room {room_name}: {message}')
                self.relay_message(room_name, message)
            else:
                print(f'Invalid token from {client_address}')


            # 新しいクライアントからの受信 -> clientsリストにアドレスを保存
            # if (not client_address in self.clientsmap):
            #     name = data.decode('utf-8')
            #     self.clientsmap.update({client_address : [name, time.time()]})
            #     print("新しいユーザーです -> ", name)
            #     print(client_address)
            #     print("新しいユーザーです -> ", self.clientsmap[client_address], time.ctime())
            # else:
            #     self.clientsmap[client_address][1] = time.time() # クライアントの最終送信時刻を更新
            #     usernamelen = data[0] # 最初のバイトがユーザー名の長さを表す
            #     username = data[1:usernamelen + 1].decode() # ユーザー名を取得
            #     message = data[usernamelen + 1:].decode() # メッセージを取得
            #     print(f"{username}: {message}")
            #     self.relay_message(username + ": " + message) # 接続ユーザ全員に送信(送信元のユーザも含む)
    
    # リレーシステム
    def relay_message(self, room_name, message):
        if room_name in self.clientsmap:
            for client_address, token in self.clientsmap[room_name].items():
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

    # トークンの有効性を確認
    def is_valid_token(self, room_name, client_address, token):
        return (room_name in chatroom.rooms and client_address in chatroom.rooms[room_name] and chatroom.rooms[room_name][client_address] == token)

    # アクティブでないクライアントの削除
    def remove_inactive_clients(self):
        while True:
            time.sleep(60)
            current_time = time.time()
            for room in list(self.clientsmap):
                for client in list(self.clientsmap[room]):
                    if current_time - self.clientsmap[room][client][1] > 300:
                        del self.clientsmap[room][client]
                        self.sock.sendto(b"Timeout!", client)
                        print(f'{client} in room {room} has been disconnected due to inactivity.')

    def start(self):
        thread_main = threading.Thread(target = self.handle_message)
        thread_tracking = threading.Thread(target = self.send_time_tracking)
        thread_main.start()
        thread_tracking.start()
        thread_main.join()
        thread_tracking.join()


class TCPServer:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.server_address, self.server_port))
        print('TCPサーバー起動しました')
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
    udp_server_port = 9001
    tcp_server_port = 9002
    print('starting up on port {}'.format(udp_server_port))
    udp_server = UDPServer(server_address, udp_server_port)
    tcp_server = TCPServer(server_address, tcp_server_port)
    chatroom = Chatroom()
    # UDP用
    thread_udp = threading.Thread(target=udp_server.start)
    thread_udp.start()
    # TCP接続用
    thread_tcp = threading.Thread(target=tcp_server.start)
    thread_tcp.start()
    thread_udp.join()
    thread_tcp.join()

