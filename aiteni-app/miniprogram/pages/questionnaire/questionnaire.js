// pages/questionnaire/questionnaire.js

// 维度名称映射
const DIMENSION_NAMES = {
  baseline: '底线综合',
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  return: '接发球',
  net: '网前与高压',
  footwork: '步伐与覆盖',
  tactics: '战术与心理',
  match_result: '实战成绩',
  training: '训练背景'
}

Page({
  data: {
    statusBarHeight: 0,
    navbarHeight: 88,
    isLoading: true,
    
    // 问卷数据
    questions: [],
    totalQuestions: 0,
    currentIndex: 0,
    currentQuestion: null,
    
    // 答案数据
    answers: {},
    selectedAnswer: '',
    
    // UI状态
    progress: 0,
    isLastQuestion: false,
    questionAnimation: null
  },

  onLoad(options) {
    // 获取状态栏高度
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 0
    })

    // 加载问卷数据
    this.loadQuestions()
  },

  /**
   * 加载问卷数据
   */
  async loadQuestions() {
    try {
      this.setData({ isLoading: true })

      // TODO: 从后端API获取问卷数据
      // 目前使用模拟数据
      const questions = await this.fetchQuestionsFromAPI()
      
      // 处理问卷数据，添加维度名称
      const processedQuestions = questions.map(q => ({
        ...q,
        dimensionName: DIMENSION_NAMES[q.dimension] || q.dimension
      }))

      this.setData({
        questions: processedQuestions,
        totalQuestions: processedQuestions.length,
        currentQuestion: processedQuestions[0],
        progress: 0,
        isLoading: false
      })

      // 检查是否有已保存的答案（用于断点续答）
      this.loadSavedAnswers()
    } catch (error) {
      console.error('加载问卷失败:', error)
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      })
    }
  },

  /**
   * 从API获取问卷数据
   * TODO: 替换为实际的API调用
   */
  async fetchQuestionsFromAPI() {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 500))

    // 模拟问卷数据（实际应该从后端获取）
    return [
      {
        id: "Q1",
        dimension: "baseline",
        text: "你和水平相近的球友,从底线相互对拉时(中速,不是全力爆抽),通常能稳定打多少拍?",
        options: [
          {
            id: "Q1_A1",
            text: "很难连续超过 3 拍，经常 1～2 拍就下网或出界"
          },
          {
            id: "Q1_A2",
            text: "偶尔能打到 4～6 拍，但失误仍然很多"
          },
          {
            id: "Q1_A3",
            text: "经常能打到 6～10 拍，中速球勉强稳定，但深度方向不太可控"
          },
          {
            id: "Q1_A4",
            text: "经常能打到 10 拍以上，双方主要靠主动进攻或战术变化结束回合"
          },
          {
            id: "Q1_A5",
            text: "在中速对拉中失误很少，更多是通过主动加速、变线得分或失分"
          }
        ]
      },
      {
        id: "Q2",
        dimension: "baseline",
        text: "从整体情况看,你的底线来回球,一般能把球打到多深?",
        options: [
          {
            id: "Q2_A1",
            text: "多数球都落在发球线附近或更短，很难把对手顶到底线"
          },
          {
            id: "Q2_A2",
            text: "能偶尔打到中后场，但多数球还是偏短，容易被对手抓机会"
          },
          {
            id: "Q2_A3",
            text: "经常能把球打到中后场，让对手退在底线附近，但深度不算很稳定"
          },
          {
            id: "Q2_A4",
            text: "大多数来回都能打出中深场，偶尔用更深的球制造压力"
          }
        ]
      }
      // 更多问题...
    ]
  },

  /**
   * 加载已保存的答案（断点续答功能）
   */
  loadSavedAnswers() {
    try {
      const savedAnswers = wx.getStorageSync('currentAnswers')
      if (savedAnswers && Object.keys(savedAnswers).length > 0) {
        // 询问用户是否继续上次的评测
        wx.showModal({
          title: '提示',
          content: '检测到未完成的评测，是否继续？',
          success: (res) => {
            if (res.confirm) {
              this.setData({ answers: savedAnswers })
              this.resumeFromSaved()
            } else {
              wx.removeStorageSync('currentAnswers')
            }
          }
        })
      }
    } catch (e) {
      console.error('加载已保存答案失败:', e)
    }
  },

  /**
   * 从保存的位置恢复
   */
  resumeFromSaved() {
    const { answers, questions } = this.data
    const answeredCount = Object.keys(answers).length
    
    if (answeredCount > 0 && answeredCount < questions.length) {
      // 跳转到第一个未回答的问题
      const nextIndex = questions.findIndex(q => !answers[q.id])
      if (nextIndex >= 0) {
        this.goToQuestion(nextIndex)
      }
    }
  },

  /**
   * 选择选项
   */
  selectOption(e) {
    const optionId = e.currentTarget.dataset.optionId
    const { currentQuestion } = this.data
    
    this.setData({
      selectedAnswer: optionId,
      [`answers.${currentQuestion.id}`]: optionId
    })

    // 保存当前答案
    this.saveCurrentAnswers()
  },

  /**
   * 保存当前答案到本地存储
   */
  saveCurrentAnswers() {
    try {
      wx.setStorageSync('currentAnswers', this.data.answers)
    } catch (e) {
      console.error('保存答案失败:', e)
    }
  },

  /**
   * 下一题
   */
  nextQuestion() {
    const { currentIndex, totalQuestions, selectedAnswer } = this.data

    if (!selectedAnswer) {
      wx.showToast({
        title: '请选择一个选项',
        icon: 'none'
      })
      return
    }

    if (currentIndex < totalQuestions - 1) {
      // 下一题
      this.goToQuestion(currentIndex + 1)
    } else {
      // 最后一题，提交评测
      this.submitQuestionnaire()
    }
  },

  /**
   * 上一题
   */
  prevQuestion() {
    const { currentIndex } = this.data
    if (currentIndex > 0) {
      this.goToQuestion(currentIndex - 1)
    }
  },

  /**
   * 跳转到指定问题
   */
  goToQuestion(index) {
    const { questions, answers } = this.data
    const question = questions[index]
    const savedAnswer = answers[question.id] || ''

    // 创建切换动画
    const animation = wx.createAnimation({
      duration: 200,
      timingFunction: 'ease'
    })
    animation.opacity(0).scale(0.95).step()
    
    this.setData({
      questionAnimation: animation.export()
    })

    setTimeout(() => {
      const newAnimation = wx.createAnimation({
        duration: 200,
        timingFunction: 'ease'
      })
      newAnimation.opacity(1).scale(1).step()

      const progress = Math.round(((index + 1) / questions.length) * 100)
      
      this.setData({
        currentIndex: index,
        currentQuestion: question,
        selectedAnswer: savedAnswer,
        progress,
        isLastQuestion: index === questions.length - 1,
        questionAnimation: newAnimation.export()
      })
    }, 200)
  },

  /**
   * 提交问卷
   */
  async submitQuestionnaire() {
    const { answers, totalQuestions } = this.data

    // 检查是否所有问题都已回答
    if (Object.keys(answers).length < totalQuestions) {
      wx.showModal({
        title: '提示',
        content: '还有问题未回答，确定要提交吗？',
        success: (res) => {
          if (res.confirm) {
            this.doSubmit()
          }
        }
      })
    } else {
      this.doSubmit()
    }
  },

  /**
   * 执行提交
   */
  async doSubmit() {
    try {
      wx.showLoading({
        title: '评估中...',
        mask: true
      })

      // TODO: 调用后端API进行评估
      const result = await this.submitToAPI(this.data.answers)

      // 清除当前答案缓存
      wx.removeStorageSync('currentAnswers')

      // 保存评估结果到历史记录
      this.saveToHistory(result)

      wx.hideLoading()

      // 跳转到结果页
      wx.redirectTo({
        url: `/pages/result/result?resultId=${result.id}`
      })
    } catch (error) {
      wx.hideLoading()
      console.error('提交失败:', error)
      wx.showToast({
        title: '提交失败，请重试',
        icon: 'none'
      })
    }
  },

  /**
   * 提交到API
   * TODO: 替换为实际的API调用
   */
  async submitToAPI(answers) {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 1500))

    // 模拟返回结果
    return {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      overallLevel: 3.5,
      levelLabel: '发展中业余选手',
      dimensions: {
        baseline: 3.0,
        forehand: 3.8,
        backhand: 3.3,
        serve: 3.0,
        return: 3.2,
        net: 3.4,
        footwork: 3.4,
        tactics: 3.6
      },
      advantages: ['正手', '步伐与覆盖', '战术与心理'],
      weaknesses: ['发球', '底线稳定性'],
      suggestions: {}
    }
  },

  /**
   * 保存到历史记录
   */
  saveToHistory(result) {
    try {
      let history = wx.getStorageSync('evaluationHistory') || []
      history.unshift(result)
      
      // 最多保存10条记录
      if (history.length > 10) {
        history = history.slice(0, 10)
      }
      
      wx.setStorageSync('evaluationHistory', history)
      wx.setStorageSync('latestResult', result)
    } catch (e) {
      console.error('保存历史记录失败:', e)
    }
  },

  /**
   * 返回
   */
  goBack() {
    if (Object.keys(this.data.answers).length > 0) {
      wx.showModal({
        title: '提示',
        content: '当前进度会自动保存，确定要退出吗？',
        success: (res) => {
          if (res.confirm) {
            wx.navigateBack()
          }
        }
      })
    } else {
      wx.navigateBack()
    }
  }
})
