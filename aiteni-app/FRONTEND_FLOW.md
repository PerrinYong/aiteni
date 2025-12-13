# 前端交互流程设计

## 📋 总体流程（基于 aiteni-core）

```
欢迎页 → 基础评测 → (条件判断) → 进阶评测 → 结果页
         (第一阶段)               (第二阶段)
```

## 🔄 详细流程

### 1. 欢迎页 (welcome.wxml)

**功能：**
- 展示 NTRP 介绍
- 显示评测说明
- 点击"开始评测"进入评测流程

**交互：**
```javascript
// 点击开始评测
startTest() {
  // 1. 从服务器获取题目配置
  // 2. 筛选出基础题（question_tier: "basic"）
  // 3. 跳转到问卷页
  wx.navigateTo({
    url: '/pages/questionnaire/questionnaire?stage=basic'
  })
}
```

---

### 2. 问卷页 - 基础阶段 (questionnaire.wxml)

**功能：**
- 显示基础题（question_tier: "basic"）
- 收集用户答案
- 提交后获取初步评估

**数据流：**
```javascript
onLoad(options) {
  const stage = options.stage; // 'basic' or 'advanced'
  
  // 从服务器获取题目
  this.loadQuestions(stage);
}

// 用户完成基础题，点击提交
submitBasicAnswers() {
  // 1. 收集答案
  const answers = this.data.answers;
  
  // 2. 发送到服务器进行初步评估
  const result = await api.evaluateBasic(answers);
  
  // 3. 根据初步等级判断
  if (result.level >= 3.0) {
    // 需要进阶题
    wx.showModal({
      title: '继续进阶评估',
      content: `您的初步水平约为 NTRP ${result.level}，请继续完成进阶题目获得更准确的评估`,
      success: (res) => {
        if (res.confirm) {
          this.loadAdvancedQuestions();
        }
      }
    });
  } else {
    // 直接显示结果
    this.navigateToResult(result);
  }
}
```

---

### 3. 问卷页 - 进阶阶段（可选）

**功能：**
- 显示进阶题（question_tier: "advanced"）
- 收集答案并合并基础题答案
- 提交完整答案获取最终评估

**数据流：**
```javascript
// 用户完成进阶题，点击提交
submitAllAnswers() {
  // 1. 合并基础题和进阶题答案
  const allAnswers = {
    ...this.data.basicAnswers,
    ...this.data.advancedAnswers
  };
  
  // 2. 发送到服务器进行完整评估
  const finalResult = await api.evaluateFull(allAnswers);
  
  // 3. 跳转到结果页
  this.navigateToResult(finalResult);
}
```

---

### 4. 结果页 (result.wxml)

**功能：**
- 显示 NTRP 等级（简略卡片）
- 显示优势和短板
- 展示维度详情（可展开）
- 保存到历史记录

**显示内容：**
- 🎾 NTRP 等级 + 等级描述
- 📊 技术能力概览（雷达图数据）
- 💪 主要优势（前3个）
- 🎯 提升重点（前3个）
- 📝 各维度详细评估（可折叠展开）

**数据流：**
```javascript
onLoad(options) {
  // 从上一页传递或从缓存读取评估结果
  const result = this.getEvaluationResult();
  
  // 渲染结果
  this.renderResult(result);
  
  // 保存到历史记录
  this.saveToHistory(result);
}
```

---

## 🔌 API 接口设计

### 1. 获取题目配置

```javascript
GET /api/v1/questionnaire/config

Response:
{
  "questions": [
    {
      "id": "q1",
      "question_tier": "basic",  // "basic" 或 "advanced"
      "dimension": "baseline_consistency",
      "question_text": "...",
      "options": [
        { "text": "A. ...", "score": 1.0 },
        { "text": "B. ...", "score": 2.0 }
      ]
    }
  ]
}
```

### 2. 提交答案并评估（基础题）

```javascript
POST /api/v1/evaluate/basic

Request:
{
  "answers": {
    "q1": "A",
    "q2": "C"
  }
}

Response:
{
  "level": 2.8,
  "rounded_level": 3.0,
  "need_advanced": false
}
```

### 3. 提交答案并评估（完整）

```javascript
POST /api/v1/evaluate/full

Request:
{
  "answers": {
    "q1": "A",
    "q2": "C",
    "q3": "B"  // 包含所有题目答案
  }
}

Response:
{
  "total_level": 3.8,
  "rounded_level": 4.0,
  "level_label": "业余中级选手",
  "dimension_scores": {
    "baseline_consistency": 3.5,
    "serve_quality": 4.2,
    ...
  },
  "advantages": ["serve_quality", "net_play"],
  "weaknesses": ["baseline_consistency"],
  "dimension_comments": {
    "baseline_consistency": "...",
    ...
  },
  "summary_text": "...",
  "chart_data": { ... }
}
```

---

## 📱 页面跳转流程图

```
┌─────────────┐
│  welcome    │  用户点击"开始评测"
│  (欢迎页)    │
└──────┬──────┘
       │
       ↓ 获取题目配置，筛选基础题
┌─────────────┐
│questionnaire│  用户回答基础题
│  (基础阶段)  │
└──────┬──────┘
       │
       ↓ 提交基础答案，获取初步评估
       │
   ┌───┴────┐
   │level<3?│
   └───┬────┘
       │
   ┌───┴─────┐
   │ No      │ Yes
   │         │
   ↓         ↓
┌──────┐  ┌─────────────┐
│result│  │questionnaire│  用户回答进阶题
│(结果)│  │  (进阶阶段)  │
└──────┘  └──────┬──────┘
                 │
                 ↓ 提交完整答案，获取最终评估
          ┌─────────────┐
          │   result    │  显示详细结果
          │   (结果页)   │
          └─────────────┘
```

---

## 💾 本地存储策略

### 1. 缓存题目配置
```javascript
// 首次加载时缓存，避免重复请求
wx.setStorageSync('questions_config', questions);
```

### 2. 保存答题进度（断点续答）
```javascript
// 实时保存答题进度
wx.setStorageSync('current_answers', answers);
wx.setStorageSync('current_stage', 'basic'); // 'basic' or 'advanced'
```

### 3. 保存历史记录
```javascript
// 评估完成后保存
const history = wx.getStorageSync('evaluation_history') || [];
history.unshift({
  id: Date.now(),
  date: new Date().toISOString(),
  level: result.rounded_level,
  level_label: result.level_label,
  result: result
});
wx.setStorageSync('evaluation_history', history);
```

---

## 🎯 关键实现要点

### 1. 题目分阶段加载
```javascript
// questionnaire.js
loadQuestions(stage) {
  const allQuestions = wx.getStorageSync('questions_config');
  const filteredQuestions = allQuestions.filter(q => 
    q.question_tier === stage
  );
  this.setData({ questions: filteredQuestions });
}
```

### 2. 答案合并逻辑
```javascript
// 基础题完成后，保存基础答案
this.basicAnswers = { ...this.data.answers };

// 进阶题完成后，合并答案
const allAnswers = {
  ...this.basicAnswers,
  ...this.data.answers
};
```

### 3. 结果页数据展示
```javascript
// result.js
renderResult(result) {
  // 处理优势维度
  const advantages = result.advantages.map(dim => ({
    name: this.getDimensionName(dim),
    score: result.dimension_scores[dim]
  }));
  
  // 处理短板维度
  const weaknesses = result.weaknesses.map(dim => ({
    name: this.getDimensionName(dim),
    score: result.dimension_scores[dim]
  }));
  
  this.setData({
    level: result.rounded_level,
    levelLabel: result.level_label,
    advantages: advantages,
    weaknesses: weaknesses,
    dimensionDetails: this.processDimensions(result.dimension_scores)
  });
}
```

---

## 🔍 错误处理

### 1. 网络请求失败
```javascript
try {
  const result = await api.evaluate(answers);
  // 处理结果
} catch (error) {
  wx.showModal({
    title: '评估失败',
    content: '网络连接失败，请检查网络后重试',
    confirmText: '重试',
    success: (res) => {
      if (res.confirm) {
        this.submitAnswers(); // 重试
      }
    }
  });
}
```

### 2. 题目配置加载失败
```javascript
loadQuestions() {
  wx.showLoading({ title: '加载题目中...' });
  
  api.getQuestions()
    .then(questions => {
      wx.hideLoading();
      this.setData({ questions });
    })
    .catch(error => {
      wx.hideLoading();
      wx.showModal({
        title: '加载失败',
        content: '题目加载失败，请重试',
        success: (res) => {
          if (res.confirm) {
            this.loadQuestions();
          } else {
            wx.navigateBack();
          }
        }
      });
    });
}
```

---

## 📊 用户体验优化

1. **加载状态提示**：题目加载、评估计算时显示 loading
2. **断点续答**：保存答题进度，允许中途退出后继续
3. **答案验证**：提交前检查是否所有题目都已回答
4. **结果缓存**：评估结果临时缓存，支持返回查看
5. **历史记录**：自动保存每次评估结果，支持查看历史

---

## 🚀 后续优化方向

1. **离线支持**：缓存题目和算法，支持离线评估
2. **进度可视化**：显示答题进度条
3. **结果分享**：生成结果海报，支持分享给好友
4. **对比分析**：支持多次评估结果对比
5. **个性化建议**：根据短板维度推荐训练计划
