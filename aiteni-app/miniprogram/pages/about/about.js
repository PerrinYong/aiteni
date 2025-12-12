// pages/about/about.js
Page({
  data: {
    statusBarHeight: 0,
    navbarHeight: 88
  },

  onLoad() {
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight || 0
    })
  }
})
