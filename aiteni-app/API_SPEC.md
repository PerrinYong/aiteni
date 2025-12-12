# Ai-TEni 爱特尼网球小程序 API 接口规范

## 基本信息

- **Base URL**: `https://api.aiteni.com/v1` (待定)
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: 微信登录 + Session Token

---

## 1. 用户认证

### 1.1 微信登录

**接口**: `POST /auth/wx-login`

**请求参数**:
```json
{
  "code": "string",  // 微信登录凭证
  "encryptedData": "string",  // 加密数据（可选）
  "iv": "string"  // 初始向量（可选）
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "string",  // 会话令牌
    "userId": "string",
    "userInfo": {
      "nickName": "string",
      "avatarUrl": "string"
    }
  }
}
```

---

## 2. 问卷配置

### 2.1 获取问卷配置

**接口**: `GET /questionnaire/config`

**请求参数**: 无

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "version": "1.0",
    "questions": [
      {
        "id": "Q1",
        "dimension": "baseline",
        "weight": 1.5,
        "text": "你和水平相近的球友,从底线相互对拉时...",
        "options": [
          {
            "id": "Q1_A1",
            "text": "很难连续超过 3 拍...",
            "center_level": 2.0,
            "hard_cap": 2.5
          }
        ]
      }
    ]
  }
}
```

### 2.2 获取维度配置

**接口**: `GET /questionnaire/dimensions`

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "dimensions": [
      {
        "key": "baseline",
        "name": "底线综合",
        "description": "底线多拍稳定性 + 深度",
        "weight": 1.0
      }
    ]
  }
}
```

---

## 3. 评估提交与结果

### 3.1 提交评测答案

**接口**: `POST /evaluation/submit`

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:
```json
{
  "answers": {
    "Q1": "Q1_A3",
    "Q2": "Q2_A2",
    "Q3": "Q3_A4"
    // ...所有问题的答案
  }
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "resultId": "string",
    "overallLevel": 3.5,
    "roundedLevel": 3.5,
    "levelLabel": "发展中业余选手",
    "dimensions": {
      "baseline": 3.0,
      "forehand": 3.8,
      "backhand": 3.3,
      "serve": 3.0,
      "return": 3.2,
      "net": 3.4,
      "footwork": 3.4,
      "tactics": 3.6,
      "match_result": 3.5,
      "training": 3.2
    },
    "suggestions": {
      "summary": "整体来看，你当前的综合水平约为 NTRP 3.5...",
      "advantages": [
        {
          "dimension": "forehand",
          "name": "正手",
          "score": 3.8,
          "description": "正手已经是你的核心武器..."
        }
      ],
      "weaknesses": [
        {
          "dimension": "serve",
          "name": "发球",
          "score": 3.0,
          "description": "一发威胁有限..."
        }
      ],
      "dimensionDetails": {
        "forehand": {
          "title": "正手（约 3.8 级）",
          "subtitle": "可以作为主要得分手段",
          "detail": "正手击球动作相对完整...",
          "suggestions": [
            "在不同落点之间切换",
            "增加前冲和下压"
          ]
        }
      }
    },
    "createdAt": "2024-12-12T10:30:00Z"
  }
}
```

### 3.2 获取评测结果

**接口**: `GET /evaluation/result/:resultId`

**请求头**:
```
Authorization: Bearer <token>
```

**响应数据**: 同 3.1 的响应 data 部分

---

## 4. 历史记录

### 4.1 获取评测历史

**接口**: `GET /evaluation/history`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认1）
- `pageSize`: 每页数量（默认10）

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "page": 1,
    "pageSize": 10,
    "records": [
      {
        "id": "string",
        "overallLevel": 3.5,
        "levelLabel": "发展中业余选手",
        "dimensions": { ... },
        "createdAt": "2024-12-12T10:30:00Z"
      }
    ]
  }
}
```

### 4.2 删除评测记录

**接口**: `DELETE /evaluation/result/:resultId`

**请求头**:
```
Authorization: Bearer <token>
```

**响应数据**:
```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

## 5. 训练建议

### 5.1 获取训练计划

**接口**: `GET /training/plan/:resultId`

**请求头**:
```
Authorization: Bearer <token>
```

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "plan": [
      {
        "dimension": "serve",
        "priority": 1,
        "exercises": [
          {
            "name": "一发稳定性训练",
            "description": "在发球线后2米处...",
            "duration": "15-20分钟",
            "frequency": "每次训练"
          }
        ]
      }
    ]
  }
}
```

---

## 错误码说明

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（token无效或过期） |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应格式**:
```json
{
  "code": 400,
  "message": "参数错误",
  "error": "缺少必需参数: answers"
}
```

---

## 前端调用示例

```javascript
// utils/api.js 中的示例
const BASE_URL = 'https://api.aiteni.com/v1'

// 提交评测
async function submitEvaluation(answers) {
  const token = wx.getStorageSync('token')
  
  const res = await wx.request({
    url: `${BASE_URL}/evaluation/submit`,
    method: 'POST',
    header: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    data: { answers }
  })
  
  return res.data
}
```
