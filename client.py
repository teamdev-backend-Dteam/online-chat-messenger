import socket
import threading
import time
import sys

class UDPClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_address = ''
        self.client_port = self.find_free_port()
        self.client_info = str(self.client_address)+ "," + str(self.client_port)
        self.sock.bind((self.client_address, self.client_port))
        self.username = ''
        self.rooms = {}
    
    # サーバに接続後，最初にusernameを入力
    def input_username(self):
            USER_NAME_MAX_BYTE_SIZE = 255
            self.username = input("Please enter your username: ") # username入力
            # 何も入力がなければやり直し
            if self.username == '':
                print("Input is incorrect!")
                self.input_username()

            username_size = len(self.username.encode("utf-8"))

            # バイトサイズが255バイトより大きければやり直し
            if username_size > USER_NAME_MAX_BYTE_SIZE:
                print("User name byte: " + str(username_size) + " is too large.")
                print("The user name must not exceed 255 bytes.")
                self.input_username()
            
            # 問題がなければサーバに送信
            self.sock.sendto(self.username.encode('utf-8'), (self.server_address, self.server_port))
    
    # username入力後の処理
    def send_message(self):
        while True:
            message = input("")
            print("\033[1A\033[1A") # "\033[1A": カーソルを現在の行の先頭に移動 -> これにより、ターミナル上の出力を更新または消去
            #print("You: " + message)
            usernamelen = len(self.username).to_bytes(1, byteorder='big')# UTF-8 エンコーディングを使用して変換 (指定されたバイト数（ここでは1バイト）のバイト列に変換します)
            data = usernamelen + self.username.encode() + message.encode() # ユーザー名とメッセージを結合して送信
            # サーバへのデータ送信
            self.sock.sendto(data, (self.server_address, self.server_port))

            time.sleep(0.1)

         # 他ユーザのメッセージの受信処理
    def receive_message(self):
        while True:
            rcv_data = self.sock.recvfrom(4096)[0].decode("utf-8")

            if (rcv_data == "Timeout!"): # タイムアウト処理
                print(rcv_data)
                self.sock.close()
                sys.exit()
            else:
                print(rcv_data)


    # 空きポートの割り当て
    def find_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', 0)) # ソケットにローカルホスト上の空きポートをバインド (ポート番号を0に指定でOS空きポートを自動的に割り当て)
        port = sock.getsockname()[1] # ソケットがバインドされているアドレス情報を取得(port番号)
        sock.close()
        return port

    # トークンをセットする
    def set_token(self, room_name, token):
        self.rooms[room_name] = token

    def start(self):
        self.input_username()
        # 並列処理
        thread_send = threading.Thread(target = self.send_message)
        thread_receive = threading.Thread(target = self.receive_message)

        thread_send.start()
        thread_receive.start()
        thread_send.join()
        thread_receive.join()

class TCPClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_address, self.server_port))
    
    def start(self):
        self.send_message()
        self.receive_message()

    # オペレーションコードを入力する
    def input_op_code(self):
        op_code = input('1または2を入力してください 1: ルームを作成  2: ルームに参加')

        # ルーム作成が１
        if op_code == '1':
            return 1
        
        # ルーム参加が２
        elif op_code == '2':
            return 2
        
        else:
            print('1, 2以外が入力されました。')
            self.input_op_code()


    def input_roomname(self):
        ROOMNAME_MAX_LEN = 255
        roomname = input('チャットルーム名を入力してください')
        roomname_bytes = roomname.encode('utf-8')

        if len(roomname_bytes) > ROOMNAME_MAX_LEN:
            print('ルーム名は {ROOMNAME_MAX_LEN} バイト以下にしてください')
            self.input_roomname()
            return
        
        return roomname
        

    def send_message(self):
        header = self.make_header()
        self.sock.send(header)
        # print(header.decode('utf-8'))


    def make_header(self):
        roomname_byte = self.input_roomname().encode()
        roomname_size_byte = len(roomname_byte).to_bytes(1, "big")
        operation_byte = self.input_op_code().to_bytes(1, "big")
        state = 1
        state_byte = state.to_bytes(1, "big")
        return roomname_size_byte + operation_byte + state_byte + roomname_byte

    def receive_message(self):
        data = self.sock.recv(1024)
        room_name_len = int.from_bytes(data[:1])
        room_name = data[1:room_name_len + 1]
        token = data[room_name_len + 1:]
        # UDPクライアントにトークンをセットする
        udp_client.set_token(room_name, token)

if __name__ == "__main__":

    server_address = '0.0.0.0'
    udp_server_port = 9001
    tcp_server_port = 9002
    tcp_client = TCPClient(server_address, tcp_server_port)
    udp_client = UDPClient(server_address, udp_server_port)
    tcp_client.start()
    udp_client.start()   


































































































































