// pages/agreement/agreement.js
Page({
  data: {
    type: 'user', // 'user' 或 'privacy'
    safeTopPadding: 0,
    scrollHeight: 1000 // 滚动视图高度（rpx）
  },

  onLoad(options) {
    // 获取协议类型：user 或 privacy
    const type = options.type || 'user';
    this.setData({ type });
    
    // 设置导航栏标题
    wx.setNavigationBarTitle({
      title: type === 'user' ? '用户服务协议' : '隐私政策'
    });

    // 初始化安全区域适配
    this.initSafeArea();
    
    // 计算滚动视图高度
    this.calculateScrollHeight();
  },

  /**
   * 计算滚动视图高度
   */
  calculateScrollHeight() {
    const systemInfo = wx.getSystemInfoSync();
    const windowHeight = systemInfo.windowHeight;
    const statusBarHeight = systemInfo.statusBarHeight || 20;
    const navBarHeight = 44;
    const safeTopPadding = (statusBarHeight + navBarHeight) * 2; // 转换为rpx
    const scrollHeight = (windowHeight * 2) - safeTopPadding - 80; // 减去padding
    
    this.setData({ scrollHeight });
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
      console.error('[Agreement SafeArea] 适配失败：', error);
      this.setData({ safeTopPadding: 120 });
    }
  },

  /**
   * 返回上一页
   */
  goBack() {
    wx.navigateBack();
  }
});

