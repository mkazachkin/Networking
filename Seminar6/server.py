"""
Простейший чат-сервер
"""
import socket
import threading


class SimpleServer:
    """
    Простейший чат-сервер
    """

    def __init__(self):
        self._host = '127.0.0.1'
        self._port = 55555
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((self._host, self._port))
        self._server.listen()
        self._passwords = dict()
        self._anonumous_count = 0
        self.ONLINE = True
        self.OFFLINE = False

    def _broadcast(self, message):
        """
        Broadcast method
        """
        for client in self._passwords.values():
            if client[2] is not None:
                try:
                    client[2].send(message)
                except BrokenPipeError:
                    client[2] = None

    def _handle(self, nickname):
        """
        Handle method
        """
        while self._passwords[nickname][2] is not None:
            client = self._passwords[nickname][2]
            try:
                message = client.recv(1024)
                if message.decode('utf-8').strip() != f'{nickname}: exit':
                    self._broadcast(message)
                else:
                    client.send('EXIT'.encode('utf-8'))
                    self._passwords[nickname][1] = self.OFFLINE
                    self._passwords[nickname][2] = None
                    self._broadcast('\n{} покинул чат!'.format(
                        nickname).encode('utf-8'))
            except Exception as e:
                print(e)
                self._broadcast('{} отвалился по ошибке'.format(
                    nickname).encode('utf-8'))
                self._passwords[nickname][1] = self.OFFLINE
                self._passwords[nickname][2] = None

    def _receive(self):
        default_nick = 'Anonymouse'
        while True:
            client, address = self._server.accept()
            print("Соединение установлено {}".format(str(address)))

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            client.send('PASSWD'.encode('utf-8'))
            password = hash(client.recv(1024).decode('utf-8'))
            flag = False
            if nickname == default_nick:
                self._anonumous_count += 1
                nickname = f'{default_nick}_{self._anonumous_count}'
                client.send(f'NEWNICK:{nickname}'.encode('utf-8'))
                print(f'Ник {nickname} назначен автоматически')
                password = 'default'
                flag = True
            else:
                try:
                    if self._passwords[nickname][0] == password:
                        self._passwords[nickname][1] = self.ONLINE
                        flag = True
                        print(f'Старый друг {nickname}, пароль проверен.')
                except KeyError:
                    flag = True
                    print(f'Новый друг {nickname}, пароль запомнил.')
            if flag:
                self._passwords[nickname] = [password, self.ONLINE, client]
                print("{}".format(nickname) + ' в чате.')
                client.send('Соединение установлено! '.encode('utf-8'))
                self._broadcast("{} присоединился к чату!".format(
                    nickname).encode('utf-8'))

                thread = threading.Thread(
                    target=self._handle, args=(nickname,))
                thread.start()
            else:
                client.send('Пароль неверный!'.encode('utf-8'))

    def run(self):
        """
        Запуск сервера
        """
        print("Сервер запущен...")
        self._receive()


app = SimpleServer()
app.run()
