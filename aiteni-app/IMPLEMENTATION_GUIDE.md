# 前端实现指南

## 📝 实现步骤

### Step 1: 更新 questionnaire.js 实现两阶段评估

```javascript
// pages/questionnaire/questionnaire.js
const api = require('../../utils/api');

Page({
  data: {
    questions: [],           // 当前阶段的问题列表
    currentIndex: 0,         // 当前问题索引
    answers: {},             // 当前阶段答案
    basicAnswers: {},        // 基础题答案（保存用于第二阶段）
    stage: 'basic',          // 当前阶段：'basic' 或 'advanced'
    progress: 0,             // 答题进度
    isSubmitting: false      // 是否正在提交
  },

  onLoad(options) {
    // 获取阶段参数
    const stage = options.stage || 'basic';
    this.setData({ stage });
    
    // 加载题目
    this.loadQuestions();
  },

  /**
   * 加载题目配置
   */
  async loadQuestions() {
    try {
      wx.showLoading({ title: '加载题目中...' });
      
      // 从服务器获取题目配置
      let questions = wx.getStorageSync('questions_config');
      
      if (!questions) {
        // 缓存中没有，从服务器获取
        const config = await api.questionnaire.getConfig();
        questions = config.questions;
        // 缓存到本地
        wx.setStorageSync('questions_config', questions);
      }
      
      // 根据当前阶段筛选题目
      const filteredQuestions = questions.filter(q => 
        q.question_tier === this.data.stage
      );
      
      this.setData({ 
        questions: filteredQuestions,
        progress: 0
      });
      
      wx.hideLoading();
      
    } catch (error) {
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
    }
  },

  /**
   * 选择答案
   */
  onSelectOption(e) {
    const { questionId, optionValue } = e.currentTarget.dataset;
    
    this.setData({
      [`answers.${questionId}`]: optionValue
    });
    
    // 更新进度
    this.updateProgress();
    
    // 保存答题进度（断点续答）
    this.saveProgress();
  },

  /**
   * 更新答题进度
   */
  updateProgress() {
    const { questions, answers } = this.data;
    const answeredCount = Object.keys(answers).length;
    const progress = Math.floor((answeredCount / questions.length) * 100);
    
    this.setData({ progress });
  },

  /**
   * 保存答题进度
   */
  saveProgress() {
    wx.setStorageSync('current_answers', this.data.answers);
    wx.setStorageSync('current_stage', this.data.stage);
  },

  /**
   * 上一题
   */
  onPrevious() {
    if (this.data.currentIndex > 0) {
      this.setData({
        currentIndex: this.data.currentIndex - 1
      });
    }
  },

  /**
   * 下一题
   */
  onNext() {
    const { currentIndex, questions, answers } = this.data;
    const currentQuestion = questions[currentIndex];
    
    // 检查是否已回答当前题目
    if (!answers[currentQuestion.id]) {
      wx.showToast({
        title: '请先选择答案',
        icon: 'none'
      });
      return;
    }
    
    // 如果是最后一题，显示提交按钮提示
    if (currentIndex === questions.length - 1) {
      wx.showToast({
        title: '已完成所有题目，请点击提交',
        icon: 'none'
      });
      return;
    }
    
    this.setData({
      currentIndex: currentIndex + 1
    });
  },

  /**
   * 提交答案
   */
  async onSubmit() {
    const { questions, answers, stage } = this.data;
    
    // 验证是否所有题目都已回答
    const unansweredQuestions = questions.filter(q => !answers[q.id]);
    if (unansweredQuestions.length > 0) {
      wx.showModal({
        title: '还有题目未回答',
        content: `还有 ${unansweredQuestions.length} 道题目未回答，是否继续提交？`,
        success: (res) => {
          if (res.confirm) {
            this.submitAnswers();
          }
        }
      });
    } else {
      this.submitAnswers();
    }
  },

  /**
   * 执行提交
   */
  async submitAnswers() {
    if (this.data.isSubmitting) return;
    
    this.setData({ isSubmitting: true });
    wx.showLoading({ title: '评估中...' });
    
    try {
      if (this.data.stage === 'basic') {
        // 第一阶段：提交基础题
        await this.submitBasicStage();
      } else {
        // 第二阶段：提交完整答案
        await this.submitAdvancedStage();
      }
    } catch (error) {
      console.error('提交失败:', error);
      wx.showModal({
        title: '提交失败',
        content: '网络连接失败，请检查网络后重试',
        confirmText: '重试',
        success: (res) => {
          if (res.confirm) {
            this.submitAnswers();
          }
        }
      });
    } finally {
      this.setData({ isSubmitting: false });
      wx.hideLoading();
    }
  },

  /**
   * 提交基础题阶段
   */
  async submitBasicStage() {
    const { answers } = this.data;
    
    // 调用基础评估接口
    const result = await api.evaluation.evaluateBasic(answers);
    
    // 保存基础题答案，用于后续合并
    this.setData({ basicAnswers: answers });
    wx.setStorageSync('basic_answers', answers);
    
    // 判断是否需要进阶题
    if (result.level >= 3.0) {
      // 需要进阶题
      wx.showModal({
        title: '继续进阶评估',
        content: `您的初步水平约为 NTRP ${result.rounded_level}。为了获得更准确的评估结果，建议继续完成进阶题目。`,
        confirmText: '继续',
        cancelText: '查看结果',
        success: (res) => {
          if (res.confirm) {
            // 继续进阶题
            this.loadAdvancedQuestions();
          } else {
            // 直接查看结果（基于基础题的评估）
            this.navigateToResult(result);
          }
        }
      });
    } else {
      // 不需要进阶题，直接显示结果
      wx.showModal({
        title: '评估完成',
        content: `您的NTRP水平约为 ${result.rounded_level}`,
        showCancel: false,
        success: () => {
          this.navigateToResult(result);
        }
      });
    }
  },

  /**
   * 加载进阶题
   */
  async loadAdvancedQuestions() {
    this.setData({
      stage: 'advanced',
      currentIndex: 0,
      answers: {},
      progress: 0
    });
    
    await this.loadQuestions();
    
    wx.showToast({
      title: '已进入进阶评估',
      icon: 'success'
    });
  },

  /**
   * 提交进阶题阶段
   */
  async submitAdvancedStage() {
    // 合并基础题和进阶题答案
    const basicAnswers = this.data.basicAnswers || wx.getStorageSync('basic_answers') || {};
    const advancedAnswers = this.data.answers;
    
    const allAnswers = {
      ...basicAnswers,
      ...advancedAnswers
    };
    
    // 调用完整评估接口
    const result = await api.evaluation.evaluateFull(allAnswers);
    
    // 跳转到结果页
    this.navigateToResult(result);
  },

  /**
   * 跳转到结果页
   */
  navigateToResult(result) {
    // 缓存结果
    wx.setStorageSync('latest_result', result);
    
    // 清除答题进度
    wx.removeStorageSync('current_answers');
    wx.removeStorageSync('current_stage');
    wx.removeStorageSync('basic_answers');
    
    // 跳转到结果页
    wx.redirectTo({
      url: '/pages/result/result'
    });
  },

  /**
   * 退出评测
   */
  onExit() {
    wx.showModal({
      title: '确认退出',
      content: '答题进度将会保存，下次可以继续',
      success: (res) => {
        if (res.confirm) {
          // 保存进度后返回
          this.saveProgress();
          wx.navigateBack();
        }
      }
    });
  }
});
```

---

### Step 2: 更新 result.js 展示评估结果

```javascript
// pages/result/result.js
const api = require('../../utils/api');
const util = require('../../utils/util');

Page({
  data: {
    result: null,            // 评估结果
    level: 0,                // NTRP等级
    levelLabel: '',          // 等级描述
    advantages: [],          // 优势维度
    weaknesses: [],          // 短板维度
    dimensionDetails: [],    // 维度详情
    expandedDimensions: {},  // 展开状态
    showDetailedReport: false // 是否显示详细报告
  },

  onLoad(options) {
    // 从缓存获取最新结果
    const result = wx.getStorageSync('latest_result');
    
    if (result) {
      this.renderResult(result);
      this.saveToHistory(result);
    } else {
      wx.showToast({
        title: '未找到评估结果',
        icon: 'none',
        success: () => {
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        }
      });
    }
  },

  /**
   * 渲染评估结果
   */
  renderResult(result) {
    // 处理优势维度
    const advantages = (result.advantages || []).map(dim => ({
      id: dim,
      name: this.getDimensionName(dim),
      score: result.dimension_scores[dim],
      comment: result.dimension_comments[dim]
    }));
    
    // 处理短板维度
    const weaknesses = (result.weaknesses || []).map(dim => ({
      id: dim,
      name: this.getDimensionName(dim),
      score: result.dimension_scores[dim],
      comment: result.dimension_comments[dim]
    }));
    
    // 处理所有维度详情
    const dimensionDetails = Object.keys(result.dimension_scores || {}).map(dim => ({
      id: dim,
      name: this.getDimensionName(dim),
      score: result.dimension_scores[dim],
      comment: result.dimension_comments[dim],
      isAdvantage: (result.advantages || []).includes(dim),
      isWeakness: (result.weaknesses || []).includes(dim)
    }));
    
    this.setData({
      result,
      level: result.rounded_level,
      levelLabel: result.level_label,
      advantages,
      weaknesses,
      dimensionDetails
    });
  },

  /**
   * 获取维度中文名称
   */
  getDimensionName(dimension) {
    const dimensionMap = {
      'baseline_consistency': '底线稳定性',
      'serve_quality': '发球质量',
      'net_play': '网前技术',
      'tactical_awareness': '战术意识',
      // ... 其他维度映射
    };
    return dimensionMap[dimension] || dimension;
  },

  /**
   * 切换维度详情展开/收起
   */
  toggleDimension(e) {
    const { dimension } = e.currentTarget.dataset;
    const key = `expandedDimensions.${dimension}`;
    
    this.setData({
      [key]: !this.data.expandedDimensions[dimension]
    });
  },

  /**
   * 查看详细报告
   */
  viewDetailedReport() {
    this.setData({
      showDetailedReport: !this.data.showDetailedReport
    });
  },

  /**
   * 保存到历史记录
   */
  saveToHistory(result) {
    try {
      const history = wx.getStorageSync('evaluation_history') || [];
      
      const record = {
        id: Date.now(),
        date: new Date().toISOString(),
        level: result.rounded_level,
        levelLabel: result.level_label,
        result: result
      };
      
      history.unshift(record);
      
      // 最多保存20条记录
      if (history.length > 20) {
        history.pop();
      }
      
      wx.setStorageSync('evaluation_history', history);
      
    } catch (error) {
      console.error('保存历史记录失败:', error);
    }
  },

  /**
   * 分享结果
   */
  onShare() {
    // TODO: 实现分享功能
    wx.showToast({
      title: '分享功能开发中',
      icon: 'none'
    });
  },

  /**
   * 查看训练建议
   */
  onViewTraining() {
    // TODO: 跳转到训练建议页
    wx.showToast({
      title: '训练建议开发中',
      icon: 'none'
    });
  },

  /**
   * 重新评测
   */
  onRetest() {
    wx.redirectTo({
      url: '/pages/questionnaire/questionnaire?stage=basic'
    });
  },

  /**
   * 返回首页
   */
  onBackHome() {
    wx.switchTab({
      url: '/pages/welcome/welcome'
    });
  }
});
```

---

### Step 3: 更新 welcome.js 启动评测

```javascript
// pages/welcome/welcome.js
const app = getApp();

Page({
  data: {
    hasHistory: false,
    safeTopPadding: 0
  },

  onLoad() {
    // 设置安全区域padding
    const systemInfo = wx.getSystemInfoSync();
    const safeTopPadding = systemInfo.statusBarHeight + 44; // 状态栏 + 导航栏
    this.setData({ safeTopPadding });
    
    // 检查是否有历史记录
    this.checkHistory();
  },

  onShow() {
    // 每次显示时检查历史记录
    this.checkHistory();
  },

  /**
   * 检查是否有历史记录
   */
  checkHistory() {
    const history = wx.getStorageSync('evaluation_history') || [];
    this.setData({
      hasHistory: history.length > 0
    });
  },

  /**
   * 开始评测
   */
  startTest() {
    // 检查是否有未完成的评测
    const savedAnswers = wx.getStorageSync('current_answers');
    const savedStage = wx.getStorageSync('current_stage');
    
    if (savedAnswers && Object.keys(savedAnswers).length > 0) {
      wx.showModal({
        title: '发现未完成的评测',
        content: '是否继续上次的评测？',
        confirmText: '继续',
        cancelText: '重新开始',
        success: (res) => {
          if (res.confirm) {
            // 继续上次的评测
            wx.navigateTo({
              url: `/pages/questionnaire/questionnaire?stage=${savedStage || 'basic'}`
            });
          } else {
            // 清除保存的进度，重新开始
            wx.removeStorageSync('current_answers');
            wx.removeStorageSync('current_stage');
            wx.removeStorageSync('basic_answers');
            
            wx.navigateTo({
              url: '/pages/questionnaire/questionnaire?stage=basic'
            });
          }
        }
      });
    } else {
      // 直接开始新评测
      wx.navigateTo({
        url: '/pages/questionnaire/questionnaire?stage=basic'
      });
    }
  },

  /**
   * 查看历史记录
   */
  viewHistory() {
    wx.switchTab({
      url: '/pages/history/history'
    });
  }
});
```

---

## 🔧 后端接口需要实现

后端需要实现以下接口（在 Django backend 中）：

### 1. 获取题目配置
```python
# backend/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_questionnaire_config(request):
    """获取问卷配置"""
    # 从配置文件加载题目
    questions = config_manager.load_questions()
    
    # 转换为前端需要的格式
    questions_data = [
        {
            'id': q.id,
            'question_tier': q.question_tier,
            'dimension': q.dimension,
            'question_text': q.question_text,
            'options': [
                {'text': opt.text, 'score': opt.score}
                for opt in q.options
            ]
        }
        for q in questions
    ]
    
    return Response({
        'code': 200,
        'data': {
            'questions': questions_data
        }
    })
```

### 2. 基础题评估
```python
@api_view(['POST'])
def evaluate_basic(request):
    """基础题评估（第一阶段）"""
    answers = request.data.get('answers', {})
    
    # 执行评估
    result = evaluator.evaluate(answers)
    
    # 判断是否需要进阶题
    need_advanced = result.total_level >= 3.0
    
    return Response({
        'code': 200,
        'data': {
            'level': result.total_level,
            'rounded_level': result.rounded_level,
            'need_advanced': need_advanced
        }
    })
```

### 3. 完整评估
```python
@api_view(['POST'])
def evaluate_full(request):
    """完整评估（第二阶段或直接完整评测）"""
    answers = request.data.get('answers', {})
    
    # 执行完整评估
    result = evaluator.evaluate(answers)
    
    # 生成图表数据
    result.chart_data = chart_generator.generate_chart_data(result)
    
    # 转换为前端需要的格式
    result_data = {
        'total_level': result.total_level,
        'rounded_level': result.rounded_level,
        'level_label': result.level_label,
        'dimension_scores': result.dimension_scores,
        'advantages': result.advantages,
        'weaknesses': result.weaknesses,
        'dimension_comments': result.dimension_comments,
        'summary_text': result.summary_text,
        'chart_data': result.chart_data
    }
    
    return Response({
        'code': 200,
        'data': result_data
    })
```

---

## ✅ 实现检查清单

- [ ] 更新 `api.js` 添加两阶段评估接口
- [ ] 实现 `questionnaire.js` 两阶段评估逻辑
- [ ] 实现 `result.js` 结果展示逻辑
- [ ] 更新 `welcome.js` 启动流程
- [ ] 后端实现题目配置接口
- [ ] 后端实现基础评估接口
- [ ] 后端实现完整评估接口
- [ ] 测试基础题 -> 进阶题流程
- [ ] 测试基础题直接出结果流程
- [ ] 测试断点续答功能
- [ ] 测试历史记录保存

---

## 🎯 关键注意事项

1. **答案格式统一**：确保前后端答案格式一致（如 `{question_id: option_value}`）
2. **错误处理完善**：网络请求失败、数据加载失败都要有友好提示
3. **用户体验优化**：加载状态、进度提示、断点续答都要实现
4. **数据缓存策略**：题目配置缓存、答题进度缓存、结果缓存要合理
5. **版本兼容性**：保留兼容旧接口，方便后续升级
