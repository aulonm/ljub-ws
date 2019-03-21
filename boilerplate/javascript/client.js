#!/usr/bin/env node
const jsonStream = require('duplex-json-stream');
const net = require('net');

const port = 3876;

const client = jsonStream(net.connect(port));

client.on('data', msg => {
  console.log('Teller received:', msg);
});

const args = process.argv.slice(2);
command = args[0];

function balance() {
    client.end({cmd: 'balance'});
}

function deposit(amount) {
    client.end({
        cmd: 'deposit', 
        amount: amount
    });
}

function withdraw(amount) {
    client.end({
        cmd: 'withdraw', 
        amount: amount
    });
}

commands = {
    'balance': balance,
    'deposit': deposit,
    'withdraw': withdraw
};

try{
    commands[command](...args.slice(1));
} catch(err) {
    console.log("Something went wrong when executing command");
}
