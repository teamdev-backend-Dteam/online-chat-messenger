import socket
import threading
import time

class UDPClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_address = ''
        self.client_port = self.find_free_port()
        self.sock.bind((self.client_address, self.client_port))
        self.username = ''
    
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
            self.sock.sendto(data, (server_address, server_port))
            time.sleep(0.1)

    # 他ユーザのメッセージの受信処理
    def receive_message(self):
        while True:
            rcv_data = self.sock.recvfrom(4096)[0].decode("utf-8")
            print(rcv_data)
             
    # 空きポートの割り当て
    def find_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', 0)) # ソケットにローカルホスト上の空きポートをバインド (ポート番号を0に指定でOS空きポートを自動的に割り当て)
        port = sock.getsockname()[1] # ソケットがバインドされているアドレス情報を取得(port番号)
        sock.close()
        return port

    def start(self):
        self.input_username()
        # 並列処理
        thread_send = threading.Thread(target = self.send_message)
        thread_receive = threading.Thread(target = self.receive_message)

        thread_send.start()
        thread_receive.start()
        thread_send.join()
        thread_receive.join()


if __name__ == "__main__":
    server_address = '0.0.0.0'
    server_port = 9001
    client = UDPClient(server_address, server_port)
    client.start()