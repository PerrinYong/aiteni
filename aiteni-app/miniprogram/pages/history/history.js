// pages/history/history.js

// 维度名称映射
const DIMENSION_NAMES = {
  baseline: '底线综合',
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  return: '接发球',
  net: '网前',
  footwork: '步伐',
  tactics: '战术',
  match_result: '实战',
  training: '训练'
}

Page({
  data: {
    statusBarHeight: 0,
    navbarHeight: 88,
    history: []
  },

  onLoad() {
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 0
    })

    this.loadHistory()
  },

  onShow() {
    // 每次显示时刷新历史记录
    this.loadHistory()
  },

  /**
   * 加载历史记录
   */
  loadHistory() {
    try {
      const history = wx.getStorageSync('evaluationHistory') || []
      const processedHistory = history.map(item => this.processHistoryItem(item))
      
      this.setData({
        history: processedHistory
      })
    } catch (e) {
      console.error('加载历史记录失败:', e)
    }
  },

  /**
   * 处理历史记录项
   */
  processHistoryItem(item) {
    // 格式化日期
    const date = new Date(item.timestamp)
    const dateText = this.formatDate(date)
    
    // 获取前3个维度
    const topDimensions = this.getTopDimensions(item.dimensions)
    
    return {
      ...item,
      dateText,
      topDimensions
    }
  },

  /**
   * 格式化日期
   */
  formatDate(date) {
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) {
      return '今天'
    } else if (days === 1) {
      return '昨天'
    } else if (days < 7) {
      return `${days}天前`
    } else {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
  },

  /**
   * 获取前3个优势维度
   */
  getTopDimensions(dimensions) {
    if (!dimensions) return []
    
    const entries = Object.entries(dimensions)
    return entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([key]) => DIMENSION_NAMES[key] || key)
  },

  /**
   * 查看结果详情
   */
  viewResult(e) {
    const resultId = e.currentTarget.dataset.resultId
    
    // 将选中的结果设置为最新结果（用于result页面读取）
    const history = this.data.history
    const selectedResult = history.find(item => item.id === resultId)
    
    if (selectedResult) {
      wx.setStorageSync('latestResult', selectedResult)
      wx.navigateTo({
        url: `/pages/result/result?resultId=${resultId}`
      })
    }
  },

  /**
   * 开始新评测
   */
  startTest() {
    wx.navigateTo({
      url: '/pages/questionnaire/questionnaire'
    })
  }
})
