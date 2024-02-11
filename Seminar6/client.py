"""
Простейший чат-клиент
"""

import socket
import threading


class SimpleClient:
    """
    Класс простейшего чат-клиента
    """

    def __init__(self, **kwargs):
        """
        Класс простейшего чат-клиента.
        Аргументы:
            host: str   - строка с адресом хоста
            port: int   - номер порта
            nick: str   - Никнейм клиента
        """
        default_host = '127.0.0.1'
        default_port = 55555
        default_nick = 'Anonymouse'
        default_pwrd = 'default'

        self.receive_thread = None
        self.write_thread = None
        self._receive_flag = True
        self._write_flag = True

        self._nickname = kwargs.get('nick', default_nick)
        self._password = kwargs.get('password', default_pwrd)
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._client.connect(
                (kwargs.get('host', default_host),
                 kwargs.get('port', default_port)))
        except ConnectionRefusedError:
            self._receive_flag = False
            self._write_flag = False
            print('Выход по ошибке 1.')

    def _receive(self):
        """
        Получение данных в кодировке utf-8
        """
        while self._receive_flag:
            try:
                message = self._client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self._client.send(self._nickname.encode('utf-8'))
                elif message == 'PASSWD':
                    self._client.send(self._password.encode('utf-8'))
                elif message[:8] == 'NEWNICK:':
                    self._nickname = message[8:]
                elif message == 'Пароль неверный!':
                    print(message)
                    self._receive_flag = False
                    self._write_flag = False
                    print('Выход по ошибке 2. Нажмите Enter.')
                elif message == 'EXIT':
                    self._receive_flag = False
                    self._write_flag = False
                    print('До новых встреч. Нажмите Enter.')
                else:
                    print(message)
            except Exception as e:
                print(f"Ошибка получения данных чата {e}.")
                self._receive_flag = False
                self._write_flag = False
                print('Выход по ошибке 3. Нажмите Enter.')

    def _write(self):
        """
        Отправка данных в кодировке utf-8
        """
        while self._write_flag:
            user_input = input('')
            message = '{}: {}'.format(self._nickname, user_input)
            self._client.send(message.encode('utf-8'))

    def run(self):
        """
        Запуск клиента
        """
        self.receive_thread = threading.Thread(target=self._receive)
        self.receive_thread.start()

        self.write_thread = threading.Thread(target=self._write)
        self.write_thread.start()


params = dict()
host = input('Введите адрес сервера [127.0.0.1] >> ')
if host != '':
    params['host']: host

port = input('Введите порт сервера [55555] >> ')
if port != '':
    params['port']: port

nick = input('Введите ваш ник [Anonymouse] >> ')
if nick != '':
    params['nick'] = nick
    params['password'] = input('Введите пароль >> ')

app = SimpleClient(**params)
app.run()
