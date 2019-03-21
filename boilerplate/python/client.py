#!/usr/bin/env python3
import sys
import json
import socket

HOST, PORT = ('localhost', 3876)


class MyClient:
    def _send_request(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            sock.sendall('{}\n'.format(json.dumps(data)).encode('utf-8'))
            received = str(sock.recv(1024), 'utf-8')
        print("Teller received: {}".format(received))
        return received

    def check_balance(self):
        data = {'cmd': 'balance'}
        self._send_request(data)

    def deposit(self, amount):
        data = {'cmd': 'deposit', 'amount': int(amount)}
        self._send_request(data)

    def withdraw(self, amount):
        data = {'cmd': 'withdraw', 'amount': int(amount)}
        self._send_request(data)

    def unknown(self, command):
        data = {'cmd': command}
        self._send_request(data)

    def execute(self, command, *args):
        args = tuple([arg for arg in args if arg])
        commands = {
            'deposit': self.deposit,
            'balance': self.check_balance,
            'withdraw': self.withdraw
        }

        func = commands.get(command, None)

        if func:
            return func(*args)
        else:
            return self.unknown(command)


def main(argv):
    client = MyClient()

    command = argv[1]
    args = argv[2:] or []
    client.execute(command, *args)


if __name__ == '__main__':
    main(sys.argv)

