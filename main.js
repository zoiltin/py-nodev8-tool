const pack_command = (command, callFrameId) => {
    // 执行表达式
    evaluateOnCallFrame = {
        id : 5,
        method : "Debugger.evaluateOnCallFrame",
        params : {
            callFrameId : callFrameId,
            expression : command,
            objectGroup : "console",
            includeCommandLineAPI : true,
            silent : false,
            returnByValue : false,
            generatePreview : true
        }
    }

    // 解除pause
    resume = {
        id : 6,
        method : "Debugger.resume",
        params : {
            terminateOnResume : false
        }
    }

    return [JSON.stringify(evaluateOnCallFrame), JSON.stringify(resume)]
}

const sleep = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main(webSocketDebuggerUrl) {
    const socket = await new WebSocket(webSocketDebuggerUrl);

    await new Promise((resolve, reject) => {
        socket.onopen = () => {
            console.log('WebSocket 已连接');
            resolve(); // 连接建立后继续执行
        };

        socket.onerror = (error) => {
            console.error('WebSocket 发生错误:', error);
            reject(error);
        };
    });

    let callFrameId;

    socket.onmessage = (event) => {
        data = JSON.parse(event.data);
        try{
            if (data['params']['callFrames'][0]['callFrameId']){
                callFrameId = data['params']['callFrames'][0]['callFrameId'];
            }
        } catch {}

        try{
            if (data['id'] == 5){
                console.log(JSON.stringify(data['result']));
            }
        } catch {}
    };

    await socket.send('{"id":1,"method":"Runtime.enable","params":{}}');
    await socket.send('{"id":2,"method":"Debugger.enable","params":{"maxScriptsCacheSize":100000000}}');
    await socket.send('{"id":3,"method":"Debugger.setSkipAllPauses","params":{"skip":False}}');
    await socket.send('{"id":4,"method":"Debugger.pause","params":{}}');

    await sleep(5000);

    c = pack_command(command, callFrameId);

    await socket.send(c[0]);
    await socket.send(c[1]);

    await sleep(5000);
}

const webSocketDebuggerUrl = "ws://";
const command = "console.log(1)";
main(webSocketDebuggerUrl);