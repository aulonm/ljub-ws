#!/usr/bin/env node
const jsonStream = require('duplex-json-stream');
const net = require('net');
const fs = require('fs');

let auditLog = (() => { // Get log from log.json if exists.
    let log = [];
    try {
        log = require('./log.json');
    } catch(err) {
        console.log("No audit log found, recreating...");
    }
    return log;
})();

function getBalanceFromLog() {
    // We use reduce to derive balance from the audit log rather than storing the value itself.
    return auditLog.reduce((accumulated, current) => { 
        if (current.cmd == 'deposit')
            return accumulated + (parseInt(current.amount) || 0);
        else if (current.cmd == 'withdraw')
            return accumulated - (parseInt(current.amount) || 0);
        else
            return accumulated; 
    }, 0);
}

function writeLog(log) {
    fs.writeFile('log.json', JSON.stringify(log, null, 2), 'utf8', err => {
        if (err) {
            console.log("Could not write file");
            return
        }
    });
}

function updateTransactionLog(entry) {
    auditLog.push(entry);
    writeLog(auditLog);
}

function checkBalance(msg) {
    return {
        'cmd': msg.cmd, 
        'balance': getBalanceFromLog()
    };
}

function deposit(msg) {
    if (msg.amount <= 0)
        return {
            error: true,
            msg: 'You cannot deposit <= 0 schmeckels...'
        }
}

function withdraw(msg) {
    const intAmount = parseInt(msg.amount) || 0
    if (intAmount <= 0)
        return {
            error: true,
            msg: 'You cannot withdraw <= 0 schmeckels...'
        }
    else if (getBalanceFromLog() < intAmount)
        return {
            error: true,
            msg: 'Insufficient funds...'
        };
}

function noopt() {
    return {
        error: true, 
        msg: 'No such command...'
    };
}

const commands = { // Object mapping command name to a function.
    'balance': checkBalance,
    'deposit': deposit,
    'withdraw': withdraw,
    'noopt': noopt
};

const server = net.createServer(socket => {
  socket = jsonStream(socket);

  socket.on('data', msg => {
    console.log('Bank received:', msg);
    const functionToCall = commands[msg.cmd || 'noopt'];
    const response = functionToCall(msg) || {};
    if (!response.error)
        updateTransactionLog(msg);

    socket.write(response);
  });
});

const port = 3876;
console.log(`Listening on port ${port}...`);
server.listen(port);

