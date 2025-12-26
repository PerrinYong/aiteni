// pages/about/about.js
const app = getApp();

Page({
  data: {
    safeTopPadding: 20, // 页面容器顶部安全留白（rpx）
    version: '1.0.0',
    userInfo: null,
    features: [
      {
        title: 'NTRP专业评估',
        desc: '基于国际网球评级标准，提供科学准确的水平评估'
      },
      {
        title: '多维度分析',
        desc: '从10个维度全面分析您的网球技术水平'
      },
      {
        title: '个性化建议',
        desc: '根据评估结果提供针对性的训练建议'
      },
      {
        title: '历史记录',
        desc: '保存每次评估记录，追踪您的进步历程'
      }
    ]
  },

  onLoad() {
    // 初始化安全区域适配
    this.initSafeArea();
  },

  /**
   * 初始化安全区域适配
   */
  initSafeArea() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const navBarHeight = 44;
      const totalHeightPx = statusBarHeight + navBarHeight;
      const totalHeightRpx = totalHeightPx * 2;
      const safeTopPadding = totalHeightRpx + 20;
      
      this.setData({ safeTopPadding });
    } catch (error) {
      console.error('[About SafeArea] 适配失败：', error);
      this.setData({ safeTopPadding: 120 });
    }
  },

  /**
   * 返回"我的"界面
   */
  goBack() {
    wx.switchTab({
      url: '/pages/profile/profile'
    });
  }
})
