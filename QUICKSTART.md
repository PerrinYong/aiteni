# 🚀 快速开始指南

## 一、启动后端（5分钟）

### Windows 系统

```bash
# 方式1: 使用启动脚本（推荐）
start-backend.bat

# 方式2: 手动启动
cd aiteni-backend
python manage.py runserver
```

### 验证后端服务

浏览器访问：http://localhost:8000/api/health

看到响应表示成功 ✅

---

## 二、配置前端（3分钟）

### 1. 打开微信开发者工具

- 点击"导入项目"
- 选择目录：`g:\MyProjs\AiTeni\aiteni-app`
- 填写 AppID（测试号即可）

### 2. 关键配置 ⭐

进入 **详情 → 本地设置**，必须勾选：
```
✅ 不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书
```

不勾选将无法连接本地后端！

### 3. 点击"编译"

看到欢迎页表示成功 ✅

---

## 三、测试流程（10分钟）

### 完整评估流程

1. **开始评测** - 点击欢迎页的"开始评测"按钮
2. **基础题** - 回答 6-8 道基础题目
3. **提交** - 点击"提交"按钮
4. **判断分支**：
   - **高水平用户（≥3.0）**：弹窗询问是否继续进阶题
     - 点击"继续" → 进入进阶题
     - 点击"查看结果" → 直接查看基础评估结果
   - **低水平用户（<3.0）**：直接跳转到结果页
5. **进阶题**（如果继续）- 回答 4-6 道进阶题目
6. **查看结果** - 显示完整的评估报告

### 断点续答测试

1. 开始答题，回答 2-3 题后点击左上角返回
2. 确认保存进度
3. 返回欢迎页，再次点击"开始评测"
4. 看到"检测到未完成的评测，是否继续？"提示
5. 点击"继续"，应恢复到之前的进度

---

## 四、常见问题

### Q1: 点击"开始评测"没反应

**原因**：后端服务未启动或未关闭域名校验

**解决**：
1. 确认后端服务运行（看到 `Starting development server at http://127.0.0.1:8000/`）
2. 确认微信开发者工具中勾选了"不校验合法域名"

### Q2: 显示"暂无题目"

**原因**：题目配置文件缺失或格式错误

**解决**：
1. 检查文件是否存在：`aiteni-backend/config/questions.json`
2. 测试接口：在浏览器访问 `http://localhost:8000/api/evaluation/questions`

### Q3: 提交后报错

**原因**：答案格式不正确或后端评估逻辑出错

**解决**：
1. 打开微信开发者工具的"调试器" → "Network"
2. 查看请求和响应内容
3. 检查 Console 是否有错误信息

### Q4: 没有触发进阶题

**原因**：基础评估等级 < 3.0（不满足阈值）

**说明**：这是正常的！只有评估等级 ≥ 3.0 的用户才会被建议继续进阶评估。

**测试方法**：在基础题中选择较高分值的选项（如"能够持续回球，较少失误"）

---

## 五、文件结构

```
AiTeni/
├── start-backend.bat          # 后端启动脚本
├── check-frontend.bat         # 前端检查脚本
├── IMPLEMENTATION_SUMMARY.md  # 实现总结（详细）
│
├── aiteni-backend/            # 后端代码
│   ├── backend/
│   │   ├── urls.py           # [已更新] 新增 basic/full 路由
│   │   └── evaluation_views.py # [已更新] 新增评估函数
│   └── config/
│       └── questions.json    # 题目配置
│
└── aiteni-app/               # 前端代码
    ├── DEPLOYMENT.md         # [新增] 部署指南
    ├── FRONTEND_TEST_GUIDE.md # [新增] 测试指南
    ├── miniprogram/
    │   ├── pages/
    │   │   ├── welcome/
    │   │   │   └── welcome.js  # [已更新] 断点续答
    │   │   ├── questionnaire/
    │   │   │   ├── questionnaire.js  # [已替换] 两阶段版本
    │   │   │   └── questionnaire.js.bak # [备份] 原始版本
    │   │   └── result/
    │   │       └── result.js   # 结果页
    │   └── utils/
    │       └── api.js         # [已更新] API 客户端
    └── ...
```

---

## 六、核心 API

### 1. 获取题目配置
```
GET /api/evaluation/questions
```

### 2. 基础评估
```
POST /api/evaluation/basic
Body: {"answers": {"Q1": "Q1_A1", ...}}
Response: {
  "code": 0,
  "data": {
    "level": 3.2,
    "need_advanced": true
  }
}
```

### 3. 完整评估
```
POST /api/evaluation/full
Body: {"answers": {"Q1": "Q1_A1", ...}}
Response: {
  "code": 0,
  "data": {
    "level": 3.5,
    "advantages": [...],
    "weaknesses": [...],
    "dimension_details": [...]
  }
}
```

---

## 七、调试工具

### 微信开发者工具

1. **Console** - 查看 JavaScript 错误和日志
2. **Network** - 查看网络请求和响应
3. **Storage** - 查看 LocalStorage 缓存
   - `questions_config` - 题目配置
   - `current_answers` - 当前答案
   - `basic_answers` - 基础题答案
   - `latest_result` - 最新结果

### 后端调试

查看后端日志（Terminal 输出）：
- 请求URL和方法
- 请求参数
- 响应状态码

---

## 八、检查清单

开始测试前，确保：

- [ ] 后端服务正常运行（访问 http://localhost:8000/api/health 有响应）
- [ ] 微信开发者工具已勾选"不校验合法域名"
- [ ] `api.js` 中的 BASE_URL 为 `http://localhost:8000/api`
- [ ] `questions.json` 文件存在且格式正确
- [ ] 问卷页已更新为两阶段版本

---

## 九、获取帮助

遇到问题？查看详细文档：

- **部署问题**：阅读 `aiteni-app/DEPLOYMENT.md`
- **测试问题**：阅读 `aiteni-app/FRONTEND_TEST_GUIDE.md`
- **架构理解**：阅读 `IMPLEMENTATION_SUMMARY.md`

---

**开发愉快！** 🎾
