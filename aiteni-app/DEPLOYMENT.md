# 前后端集成部署指南

## ✅ 已完成的工作

### 后端接口实现

1. **新增两个评估接口**：
   - `POST /api/evaluation/basic` - 基础题评估（第一阶段）
   - `POST /api/evaluation/full` - 完整评估（第二阶段或直接完整评测）

2. **更新URL配置**：
   - 已在 `backend/urls.py` 中添加新路由

3. **实现评估逻辑**：
   - 基础评估：判断是否需要进阶题（level >= 3.0）
   - 完整评估：返回详细的评估结果

### 前端实现

1. **API接口更新**：
   - 更新 `utils/api.js`，添加两阶段评估接口
   - 修正 BASE_URL 和业务状态码

2. **欢迎页更新**：
   - 支持断点续答提示
   - 自动检测未完成的评测

3. **问卷页实现**：
   - 创建了完整的两阶段评估逻辑
   - 支持基础题 → 判断 → 进阶题流程

---

## 🚀 部署步骤

### Step 1: 后端部署

#### 1.1 启动后端服务

```bash
cd aiteni-backend

# 激活虚拟环境（如果有）
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行服务
python manage.py runserver 0.0.0.0:8000
```

#### 1.2 验证后端接口

访问以下URL测试接口是否正常：

```bash
# 健康检查
curl http://localhost:8000/api/health

# 获取题目配置
curl http://localhost:8000/api/evaluation/questions

# 基础评估测试
curl -X POST http://localhost:8000/api/evaluation/basic \
  -H "Content-Type: application/json" \
  -d '{"answers":{"Q1":"Q1_A1","Q2":"Q2_A2"}}'
```

---

### Step 2: 前端部署

#### 2.1 替换 questionnaire.js

将新实现的文件内容复制到原文件：

```bash
# 备份原文件
cp miniprogram/pages/questionnaire/questionnaire.js miniprogram/pages/questionnaire/questionnaire.js.bak

# 使用新实现
cp miniprogram/pages/questionnaire/questionnaire-two-stage.js miniprogram/pages/questionnaire/questionnaire.js
```

或手动复制 `questionnaire-two-stage.js` 的内容到 `questionnaire.js`

#### 2.2 配置 API 地址

编辑 `miniprogram/utils/api.js`，确认 BASE_URL 正确：

```javascript
const CONFIG = {
  // 开发环境使用本地地址
  BASE_URL: 'http://localhost:8000/api',
  
  // 生产环境使用服务器地址
  // BASE_URL: 'https://your-domain.com/api',
  
  TIMEOUT: 10000
}
```

#### 2.3 微信开发者工具配置

1. 打开微信开发者工具
2. 导入项目：选择 `aiteni-app` 目录
3. **关键设置**：
   - 进入"详情" → "本地设置"
   - ✅ 勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"
   - 这样才能访问本地 `http://localhost:8000`

4. 点击"编译"运行小程序

---

### Step 3: 完整测试流程

#### 3.1 欢迎页测试

1. 启动小程序，查看欢迎页
2. 点击"开始评测"，应该跳转到问卷页

#### 3.2 基础题评测

1. 回答基础题（应该有 6-8 道题）
2. 点击"提交"
3. 观察结果：
   - 如果分数 < 3.0：直接跳转到结果页
   - 如果分数 >= 3.0：弹窗询问是否继续进阶题

#### 3.3 进阶题评测

1. 选择"继续"进阶评估
2. 回答进阶题（应该有 4-6 道题）
3. 点击"提交"
4. 应该跳转到结果页，显示详细评估结果

#### 3.4 结果页测试

1. 查看 NTRP 等级
2. 查看优势和短板分析
3. 展开维度详情
4. 确认历史记录已保存

#### 3.5 断点续答测试

1. 在答题中途点击左上角返回
2. 确认弹窗询问是否保存进度
3. 返回欢迎页，再次点击"开始评测"
4. 应该弹窗询问是否继续上次评测

---

## 🔧 常见问题排查

### 问题 1: 前端无法连接后端

**症状**：点击"开始评测"后一直转圈，或提示"网络请求失败"

**排查步骤**：

1. 确认后端服务已启动：
   ```bash
   curl http://localhost:8000/api/health
   ```

2. 检查微信开发者工具网络权限：
   - 详情 → 本地设置 → 不校验合法域名（必须勾选）

3. 查看调试器 Console 是否有错误信息

4. 确认 API 地址配置正确（`utils/api.js` 中的 BASE_URL）

---

### 问题 2: 题目加载失败

**症状**：进入问卷页后提示"暂无题目"

**排查步骤**：

1. 检查后端配置文件是否存在：
   ```bash
   ls aiteni-backend/config/questions.json
   ```

2. 测试后端接口：
   ```bash
   curl http://localhost:8000/api/evaluation/questions
   ```

3. 查看后端日志是否有错误

4. 检查 questions.json 中的 question_tier 字段是否正确设置

---

### 问题 3: 评估结果异常

**症状**：提交后报错或结果不正常

**排查步骤**：

1. 检查答案格式是否正确：
   - 答案应该是 `{question_id: option_id}` 格式
   - 例如：`{"Q1": "Q1_A1", "Q2": "Q2_A3"}`

2. 查看后端日志中的错误信息

3. 检查配置文件中的选项ID是否与答案匹配

---

### 问题 4: 二阶段流程不正常

**症状**：完成基础题后没有提示进阶题

**排查步骤**：

1. 检查基础评估接口返回：
   ```bash
   curl -X POST http://localhost:8000/api/evaluation/basic \
     -H "Content-Type: application/json" \
     -d '{"answers":{"Q1":"Q1_A1"}}'
   ```
   应该返回 `need_advanced` 字段

2. 确认前端代码正确处理 `result.need_advanced`

3. 检查是否有 JavaScript 错误（开发者工具 Console）

---

## 📝 后续优化建议

### 1. 生产环境部署

```bash
# 后端使用 gunicorn 部署
pip install gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000

# 或使用 uwsgi
pip install uwsgi
uwsgi --http :8000 --module backend.wsgi
```

### 2. HTTPS 配置

小程序正式版必须使用 HTTPS，需要：
1. 申请 SSL 证书
2. 配置 Nginx 反向代理
3. 在微信公众平台配置服务器域名

### 3. 性能优化

- 启用 Redis 缓存题目配置
- 使用 CDN 加速静态资源
- 优化数据库查询（如果使用数据库）

### 4. 监控和日志

- 配置日志收集（ELK、Sentry等）
- 添加性能监控（APM）
- 配置错误告警

---

## 🎯 测试检查清单

- [ ] 后端服务启动成功
- [ ] 健康检查接口正常
- [ ] 题目配置接口返回数据
- [ ] 基础评估接口正常
- [ ] 完整评估接口正常
- [ ] 前端能正常连接后端
- [ ] 题目正常显示
- [ ] 答题流程顺畅
- [ ] 基础题 → 进阶题流程正常
- [ ] 评估结果正确显示
- [ ] 历史记录保存成功
- [ ] 断点续答功能正常

---

## 📞 技术支持

如有问题，请检查：
1. 后端日志：`aiteni-backend/logs/`
2. 前端 Console：微信开发者工具调试器
3. 网络请求：微信开发者工具 Network 面板
