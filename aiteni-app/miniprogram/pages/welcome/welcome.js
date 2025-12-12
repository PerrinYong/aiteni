// pages/welcome/welcome.js
Page({
  data: {
    hasHistory: false,
    safeTopPadding: 20 // 页面容器顶部安全留白（rpx）
  },

  onLoad(options) {
    // 初始化安全区域适配
    this.initSafeArea();
    // 检查是否有历史记录
    this.checkHistory()
  },

  /**
   * 初始化安全区域适配（首页特殊处理：减少顶部留白）
   * 首页标题可以与导航栏顶部对齐，无需额外留白
   */
  initSafeArea() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const navBarHeight = 44; // 原生导航栏高度
      const totalHeightPx = statusBarHeight + navBarHeight;
      // px转rpx：简化方案 1px ≈ 2rpx
      const totalHeightRpx = totalHeightPx * 2;
      // 首页留白 = 导航栏总高度（无额外边距，让标题与导航栏对齐）
      const safeTopPadding = totalHeightRpx - 40; // 减少留白，让内容更紧凑
      
      this.setData({ safeTopPadding });
    } catch (error) {
      console.error('[Welcome SafeArea] 适配失败：', error);
      this.setData({ safeTopPadding: 80 }); // 降级默认值（更小）
    }
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
