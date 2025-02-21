import websockets
import asyncio
import requests
import json

def get_instance(ip, port):
    print('[*] 获取正在运行的instance')
    instances = []
    try:
        # HTTP GET /json/list 获取实例信息
        res = requests.get(url='http://{}:{}/json/list'.format(ip, str(port)), timeout=5)
        data = json.loads(res.text)
        for i in data:
            single = {}
            single['file'] = i['url']
            single['webSocketDebuggerUrl'] = i['webSocketDebuggerUrl']

            instances.append(single)
    except TimeoutError as e:
        print('[-] 连接超时')
        exit()
    except:
        print('[-] 数据解析错误')
        exit()

    if len(instances) > 0:
        print('[+] 有{}个instance正在运行'.format(str(len(instances))))
        for i in instances:
            print("{} -- {} -- {}".format(str(instances.index(i)), i['file'], i['webSocketDebuggerUrl']))
        num = int(input('请选择要attach的instance: '))

        if num < 0 or num >= len(instances):
            print('[-] 数字无效')
            exit() 

        return instances[num]
    else:
        print('[-] 没有instance在运行')
        exit()

def pack_command(command : str, callFrameId : str) -> list[str]:
    # 执行表达式
    evaluateOnCallFrame = {
        "id" : 5,
        "method" : "Debugger.evaluateOnCallFrame",
        "params" : {
            "callFrameId" : callFrameId,
            "expression" : command,
            "objectGroup" : "console",
            "includeCommandLineAPI" : True,
            "silent" : False,
            "returnByValue" : False,
            "generatePreview" : True
        }
    }

    # 解除pause
    resume = {
        "id" : 6,
        "method" : "Debugger.resume",
        "params" : {
            "terminateOnResume" : False
        }
    }
    return [json.dumps(evaluateOnCallFrame), json.dumps(resume)]

async def main(ip, port, command):
    instance = get_instance(ip, port)

    async with websockets.connect(instance['webSocketDebuggerUrl']) as ws:
        callFrameId = None

        await ws.send('{"id":1,"method":"Runtime.enable","params":{}}')                                         # 开启Runtime，获取帧id
        await ws.send('{"id":2,"method":"Debugger.enable","params":{"maxScriptsCacheSize":100000000}}')         # 开启debugger
        await ws.send('{"id":3,"method":"Debugger.setSkipAllPauses","params":{"skip":False}}')                  # pause
        await ws.send('{"id":4,"method":"Debugger.pause","params":{}}')                                         # pause

        while True:
            data = await ws.recv()
            data = json.loads(data)

            # 获取帧id
            if 'method' in data and data['method'] == 'Debugger.paused' and 'params' in data and 'callFrames' in data['params'] and isinstance(data['params']['callFrames'], (list, )) and len(data['params']['callFrames']) > 0:
                callFrameId = data['params']['callFrames'][0]['callFrameId']
                break

        print("callFrameId : {}".format(callFrameId))
        c = pack_command(command, callFrameId)             # pause后才能执行表达式
        
        await ws.send(c[0])
        await ws.send(c[1])
   
        while True:
            data = await ws.recv()
            data = json.loads(data)

            if 'id' in data:
                if data['id'] == 5:
                    print(data['result'])
                elif data['id'] == 6:
                    break

if __name__ == '__main__':
    IP = ''
    PORT = 9229
    EXPR = '''
console.log(1)
'''.strip()

    asyncio.run(main(IP, PORT, EXPR))