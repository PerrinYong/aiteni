# 快速开始指南 - Ai-TEni 爱特尼网球小程序

## 🚀 快速启动（5分钟）

### 步骤1：准备工具
1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 注册微信小程序账号（或使用测试号）

### 步骤2：导入项目
1. 打开微信开发者工具
2. 选择"导入项目"
3. 项目目录选择：`g:\MyProjs\AiTeni\aiteni-app`
4. AppID：使用测试号或填写你的AppID

### 步骤3：运行预览
1. 点击"编译"按钮
2. 查看效果，测试各个页面功能

---

## 📋 主要功能测试

### 1. 欢迎页
- 查看品牌介绍
- 点击"开始评测"按钮

### 2. 问卷页
- 选择答案
- 点击"下一题"
- 测试"上一题"功能
- 中途退出，再次进入（测试断点续答）
- 完成12道题后提交

### 3. 结果页
- 查看NTRP等级
- 展开/收起维度详情
- 点击"查看训练建议"
- 点击"分享"按钮

### 4. 历史记录页
- 查看评测记录列表
- 点击记录查看详情

### 5. 关于页
- 浏览应用介绍
- 查看使用说明

---

## ⚠️ 当前状态说明

### ✅ 已完成
- 所有页面UI设计和实现
- 标准微信导航栏（蓝色主题）
- 完整的交互流程
- 本地数据存储
- 断点续答功能
- 微信登录功能（在"关于"页面）

### ⚙️ 使用模拟数据
以下功能当前使用模拟数据，等待后端API对接：

1. **问卷配置** (`questionnaire.js` 第52行)
   ```javascript
   // 当前：模拟的2道问题
   // 待替换：从API获取完整12道问题
   ```

2. **评估结果** (`questionnaire.js` 第292行)
   ```javascript
   // 当前：返回固定的模拟结果
   // 待替换：调用后端评估API
   ```

3. **用户登录**
   ```javascript
   // 已实现：微信登录功能（app.js）
   // 待对接：后端登录API，获取openId和sessionKey
   ```

---

## 🔧 配置后端API

### 方式1：使用本地后端（推荐开发时使用）

1. 启动后端服务（假设运行在 localhost:8000）

2. 修改 `miniprogram/utils/api.js`：
   ```javascript
   const CONFIG = {
     BASE_URL: 'http://localhost:8000/api/v1',  // 改为本地地址
     TIMEOUT: 10000
   }
   ```

3. 在微信开发者工具中：
   - 点击右上角"详情"
   - 选择"本地设置"
   - 勾选"不校验合法域名..."

### 方式2：使用线上后端

1. 修改 `miniprogram/utils/api.js`：
   ```javascript
   const CONFIG = {
     BASE_URL: 'https://api.aiteni.com/v1',  // 改为正式域名
     TIMEOUT: 10000
   }
   ```

2. 在小程序管理后台配置服务器域名：
   - 登录 [小程序管理后台](https://mp.weixin.qq.com/)
   - 开发 → 开发管理 → 服务器域名
   - 添加 `https://api.aiteni.com`

---

## 📝 对接后端API步骤

### 1. 问卷页面对接

**文件**: `pages/questionnaire/questionnaire.js`

**需要修改的方法**: `fetchQuestionsFromAPI` (第69行)

```javascript
// 修改前（模拟数据）
async fetchQuestionsFromAPI() {
  await new Promise(resolve => setTimeout(resolve, 500))
  return [ /* 模拟数据 */ ]
}

// 修改后（真实API）
async fetchQuestionsFromAPI() {
  const api = require('../../utils/api.js')
  const config = await api.questionnaire.getConfig()
  return config.questions
}
```

### 2. 评估提交对接

**文件**: `pages/questionnaire/questionnaire.js`

**需要修改的方法**: `submitToAPI` (第309行)

```javascript
// 修改前（模拟数据）
async submitToAPI(answers) {
  await new Promise(resolve => setTimeout(resolve, 1500))
  return { /* 模拟结果 */ }
}

// 修改后（真实API）
async submitToAPI(answers) {
  const api = require('../../utils/api.js')
  const result = await api.evaluation.submit(answers)
  return result
}
```

### 3. 测试API对接

1. 在问卷页面完成答题
2. 点击"提交评测"
3. 检查网络请求（开发者工具 → 网络面板）
4. 验证返回的结果数据格式
5. 确认结果页面正常显示

---

## 🐛 常见问题

### Q1: 编译报错"Cannot find module 'XXX'"
**A**: 检查文件路径是否正确，特别是 `require()` 的路径

### Q2: 页面空白或样式异常
**A**: 
1. 检查 `app.json` 配置是否正确
2. 确认所有页面文件都存在（.wxml, .wxss, .js, .json）
3. 查看控制台是否有错误信息

### Q3: API请求失败
**A**:
1. 检查后端服务是否启动
2. 确认API地址配置正确
3. 开发环境勾选"不校验合法域名"
4. 查看网络面板的请求详情

### Q4: 本地存储数据丢失
**A**: 
- 开发环境：点击"清缓存" → "清除数据缓存"会清空
- 生产环境：用户清理微信缓存会清空
- 建议：重要数据同步到服务器

---

## 📊 项目结构导航

```
aiteni-app/
├── miniprogram/
│   ├── pages/              # 5个页面
│   │   ├── welcome/        # → 首页/欢迎页
│   │   ├── questionnaire/  # → 评测问卷
│   │   ├── result/         # → 评估结果
│   │   ├── history/        # → 历史记录
│   │   └── about/          # → 关于页面
│   ├── utils/              # 工具类
│   │   ├── api.js          # ⚙️ 需要配置API地址
│   │   └── util.js         # 通用函数
│   ├── app.js              # 小程序入口
│   ├── app.json            # 配置：页面路由、TabBar
│   └── app.wxss            # 全局样式
├── API_SPEC.md             # 📋 API接口文档
├── README.md               # 📖 项目说明
└── DEVELOPMENT_SUMMARY.md  # ✅ 开发总结
```

---

## 🎯 关键文件说明

| 文件 | 作用 | 需要修改 |
|-----|------|---------|
| `utils/api.js` | API接口封装 | ✅ 配置BASE_URL |
| `questionnaire.js` | 问卷逻辑 | ✅ 对接真实API |
| `app.json` | 小程序配置 | ✅ 填写AppID |
| `app.wxss` | 全局样式 | ❌ 无需修改 |
| `result.js` | 结果展示 | ✅ 优化数据处理 |

---

## 🎨 自定义配置

### 修改导航栏颜色
编辑 `app.json`，修改导航栏配置：

```json
"window": {
  "navigationBarBackgroundColor": "#1D7CF2",  // 导航栏背景色
  "navigationBarTitleText": "爱特尼网球评测",  // 标题文字
  "navigationBarTextStyle": "white"           // 标题文字颜色（white/black）
}
```

### 修改主题色
编辑 `app.wxss`，修改 CSS 变量：

```css
page {
  --primary-blue: #1D7CF2;       /* 改成你的主色 */
  --tennis-yellow: #FFD84A;      /* 改成你的强调色 */
  /* ... 其他颜色 */
}
```

### 修改TabBar图标
1. 准备图标（建议81×81px）
2. 放到 `miniprogram/images/` 目录
3. 修改 `app.json` 中的 `tabBar.list[].iconPath`

---

## 📞 获取帮助

- 📄 查看 [README.md](./README.md) 了解详细功能
- 📋 查看 [API_SPEC.md](./API_SPEC.md) 了解接口规范
- ✅ 查看 [DEVELOPMENT_SUMMARY.md](./DEVELOPMENT_SUMMARY.md) 了解开发进度
- 🎨 参考 `ui-demo/ui3.html` 查看设计原型

---

**祝开发顺利！🎾**
