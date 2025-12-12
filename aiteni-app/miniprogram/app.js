// app.js
App({
  globalData: {
    userInfo: null,
    openId: null,
    hasLogin: false
  },

  onLaunch: function () {
    // 检查登录状态
    this.checkLoginStatus();
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    try {
      const userInfo = wx.getStorageSync('userInfo');
      const openId = wx.getStorageSync('openId');
      if (userInfo && openId) {
        this.globalData.userInfo = userInfo;
        this.globalData.openId = openId;
        this.globalData.hasLogin = true;
      }
    } catch (e) {
      console.error('检查登录状态失败:', e);
    }
  },

  /**
   * 微信登录
   */
  login() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            // 发送 res.code 到后台换取 openId, sessionKey, unionId
            console.log('登录成功，code:', res.code);
            // TODO: 调用后端API换取openId
            // 这里暂时使用本地存储模拟
            this.globalData.hasLogin = true;
            resolve(res.code);
          } else {
            console.error('登录失败！', res.errMsg);
            reject(res.errMsg);
          }
        },
        fail: (err) => {
          console.error('wx.login调用失败:', err);
          reject(err);
        }
      });
    });
  },

  /**
   * 获取用户信息
   */
  getUserInfo() {
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          console.log('获取用户信息成功:', res.userInfo);
          this.globalData.userInfo = res.userInfo;
          // 保存到本地
          wx.setStorageSync('userInfo', res.userInfo);
          resolve(res.userInfo);
        },
        fail: (err) => {
          console.error('获取用户信息失败:', err);
          reject(err);
        }
      });
    });
  },

  /**
   * 退出登录
   */
  logout() {
    this.globalData.userInfo = null;
    this.globalData.openId = null;
    this.globalData.hasLogin = false;
    wx.removeStorageSync('userInfo');
    wx.removeStorageSync('openId');
  }
});
