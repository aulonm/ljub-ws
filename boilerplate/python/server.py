#!/usr/bin/env python3
import socketserver
import json
from functools import reduce

TRANSACTION_LOG_FILE = "log.json"


class Bank:
    def __init__(self):
        self.balance = 0
        self.log = []

        try:
            with open(TRANSACTION_LOG_FILE, 'r') as lf:
                self.log = json.load(lf)
                self.balance = self.get_balance_from_log()
        except:
            self.log = []

    def get_balance_from_log(self):
        def handle_log_item(acc: int, log_item: dict):
            cmd = log_item.get("cmd")
            if cmd == "deposit":
                acc += log_item.get("amount", 0)
            elif cmd == "withdraw":
                acc -= log_item.get("amount", 0)

            return acc

        return reduce(handle_log_item, self.log, 0)

    def handle_command(self, request: dict):
        handlers = {
            'balance': self.check_balance,
            'deposit': self.deposit,
            'withdraw': self.withdraw,
            'noop': self.noop
        }

        cmd = request.get('cmd', 'noop')
        cmd_function = handlers.get(cmd, self.noop)
        res = cmd_function(request)
        self.log_me(request, res)
        return res

    def log_me(self, request, response):
        try:
            if not response.get('error', False):
                self.log.append(request)

            with open(TRANSACTION_LOG_FILE, 'w') as lf:
                json.dump(self.log, lf)
        except:
            return {'error': True, 'msg': 'Logging error'}

    def check_balance(self, _):
        return {'balance': self.get_balance_from_log()}

    def deposit(self, args: dict):
        amount = args.get('amount', 0)
        try:
            if amount > 0:
                self.balance += amount
            else:
                return {'error': True, 'msg': 'Deposit needs to be bigger than 0'}
        except:
            return {'error': True, 'msg': 'We need an int pls'}
        return {}

    def withdraw(self, args: dict):
        amount = args.get('amount', 0)
        try:
            if amount in range(0, self.balance + 1):
                self.balance -= amount
            else:
                return {'error': True, 'msg': 'You can not withdraw more than you have...'}
        except:
            return {'error': True, 'msg': 'We need an int pls'}
        return {}

    @staticmethod
    def noop(args: dict):
        cmd = args.get('cmd', None)
        if cmd:
            return {'error': True, 'msg': 'Invalid command'}
        return {'error': True, 'msg': 'No command selected'}


class MyHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.data = None
        self.recieved_dict = None
        super().__init__(request, client_address, server)

    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        self.recieved_dict = json.loads(self.data)

        bank_response = self.server.bank.handle_command(self.recieved_dict)

        result = {**bank_response, **self.recieved_dict}
        print("Bank received: {}, and bank responded: {}".format(self.data, result))
        self.request.sendall(json.dumps(result).encode('utf-8'))
        self.recieved_dict = None


if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    HOST, PORT = ("localhost", 3876)
    with socketserver.TCPServer((HOST, PORT), MyHandler) as serv:
        serv.bank = Bank()
        print("Listening on {}:{} for connections...".format(HOST, PORT))
        serv.serve_forever()
