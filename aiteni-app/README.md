# Ai-TEni 爱特尼网球小程序 - 前端开发文档

## 项目简介

**Ai-TEni爱特尼网球**是一款面向网球爱好者的在线评测工具，通过结构化问卷帮助用户快速了解自己的真实网球水平，对标国际通用的 **NTRP 等级体系**（1.0–7.0）。

## 技术栈

- **框架**: 微信小程序原生框架
- **语言**: JavaScript (ES6+)
- **UI设计**: 基于 ui3.html 的现代化设计系统
- **状态管理**: 本地存储 + 页面data
- **后端通信**: RESTful API

## 项目结构

```
aiteni-app/
├── miniprogram/              # 小程序源码
│   ├── pages/                # 页面
│   │   ├── welcome/          # 欢迎页/首页
│   │   ├── questionnaire/    # 评测问卷页
│   │   ├── result/           # 评估结果页
│   │   ├── history/          # 历史记录页
│   │   └── about/            # 关于页
│   ├── utils/                # 工具函数
│   │   ├── api.js            # API接口封装
│   │   └── util.js           # 通用工具函数
│   ├── images/               # 图片资源
│   ├── app.js                # 小程序主入口
│   ├── app.json              # 小程序配置
│   └── app.wxss              # 全局样式
├── API_SPEC.md               # API接口规范
└── README.md                 # 项目说明
```

## 页面说明

### 1. 欢迎页 (welcome)
- **路径**: `/pages/welcome/welcome`
- **功能**:
  - 品牌展示和产品介绍
  - NTRP等级体系说明
  - 开始评测入口
  - 查看历史记录入口

### 2. 评测问卷页 (questionnaire)
- **路径**: `/pages/questionnaire/questionnaire`
- **功能**:
  - 显示12道评测问题
  - 单选答案选择
  - 进度条显示
  - 上一题/下一题导航
  - 断点续答（自动保存进度）
  - 提交评测

### 3. 评估结果页 (result)
- **路径**: `/pages/result/result`
- **功能**:
  - NTRP等级展示（Hero卡片）
  - 主要优势分析
  - 提升重点建议
  - 各维度详细评估（可折叠）
  - 分享结果
  - 查看训练建议

### 4. 历史记录页 (history)
- **路径**: `/pages/history/history`
- **功能**:
  - 显示历史评测记录列表
  - 查看历史结果详情
  - 空状态提示

### 5. 关于页 (about)
- **路径**: `/pages/about/about`
- **功能**:
  - 应用介绍
  - NTRP说明
  - 功能特色
  - 使用说明
  - 联系方式

## 设计系统

### 颜色规范

```css
--primary-blue: #1D7CF2;        /* 主色-蓝色 */
--primary-blue-soft: #2A8CFF;   /* 主色-浅蓝 */
--primary-green: #1FA27A;       /* 成功-绿色 */
--tennis-yellow: #FFD84A;       /* 网球黄 */
--bg-gray: #F5F7FA;             /* 背景灰 */
--card-white: #FFFFFF;          /* 卡片白色 */
--text-main: #1F2933;           /* 主文本 */
--text-sub: #6B7280;            /* 次级文本 */
--border-gray: #E5E7EB;         /* 边框灰 */
--success: #16A34A;             /* 成功色 */
--warning: #F97316;             /* 警告色 */
--danger: #DC2626;              /* 危险色 */
```

### 字体规范

- **h1**: 48rpx / 700
- **h2**: 40rpx / 700
- **h3**: 32rpx / 600
- **body**: 28rpx / 400
- **caption**: 24rpx / 400

## 开发指南

### 本地开发

1. **安装微信开发者工具**
   - 下载地址: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

2. **导入项目**
   - 打开微信开发者工具
   - 选择"导入项目"
   - 选择 `aiteni-app` 目录
   - 填写AppID（测试可使用测试号）

3. **配置后端API**
   - 修改 `miniprogram/utils/api.js` 中的 `BASE_URL`
   - 开发环境可使用本地地址

### API调用示例

```javascript
// 导入API模块
const api = require('../../utils/api.js')

// 获取问卷配置
api.questionnaire.getConfig()
  .then(config => {
    console.log('问卷配置:', config)
  })

// 提交评测
api.evaluation.submit(answers)
  .then(result => {
    console.log('评测结果:', result)
  })
```

## 版本历史

- **v1.0.0** (2024-12-12)
  - 完成基础页面设计和开发
  - 实现问卷流程和结果展示
  - API接口规范定义
