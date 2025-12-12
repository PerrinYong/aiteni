// pages/about/about.js
const app = getApp();

Page({
  data: {
    userInfo: null,
    safeTopPadding: 20 // 页面容器顶部安全留白（rpx）
  },

  onLoad() {
    // 初始化安全区域适配
    this.initSafeArea();
    this.loadUserInfo();
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

  onShow() {
    // 每次显示时刷新用户信息
    this.loadUserInfo();
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    const userInfo = app.globalData.userInfo;
    this.setData({ userInfo });
  },

  /**
   * 微信登录
   */
  async handleLogin() {
    try {
      wx.showLoading({ title: '登录中...' });

      // 调用微信登录
      await app.login();

      // 获取用户信息
      const userInfo = await app.getUserInfo();
      
      this.setData({ userInfo });
      
      wx.hideLoading();
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      });
    } catch (err) {
      wx.hideLoading();
      console.error('登录失败:', err);
      
      if (err.errMsg && err.errMsg.includes('getUserProfile:fail auth deny')) {
        wx.showToast({
          title: '您取消了授权',
          icon: 'none'
        });
      } else {
        wx.showToast({
          title: '登录失败，请重试',
          icon: 'none'
        });
      }
    }
  },

  /**
   * 退出登录
   */
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.logout();
          this.setData({ userInfo: null });
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
        }
      }
    });
  }
})
