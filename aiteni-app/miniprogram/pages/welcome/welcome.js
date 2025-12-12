// pages/welcome/welcome.js
Page({
  data: {
    statusBarHeight: 0,
    hasHistory: false
  },

  onLoad(options) {
    // 获取状态栏高度
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 0
    })

    // 检查是否有历史记录
    this.checkHistory()
  },

  onShow() {
    // 每次显示时检查历史记录
    this.checkHistory()
  },

  /**
   * 检查是否有历史评测记录
   */
  checkHistory() {
    try {
      const history = wx.getStorageSync('evaluationHistory')
      this.setData({
        hasHistory: history && history.length > 0
      })
    } catch (e) {
      console.error('读取历史记录失败:', e)
    }
  },

  /**
   * 开始评测
   */
  startTest() {
    wx.navigateTo({
      url: '/pages/questionnaire/questionnaire'
    })
  },

  /**
   * 查看历史记录
   */
  viewHistory() {
    wx.switchTab({
      url: '/pages/history/history'
    })
  }
})
