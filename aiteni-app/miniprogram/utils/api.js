/**
 * API 接口工具
 * 封装所有后端API调用
 */

const CONFIG = {
  // TODO: 替换为实际的API地址
  BASE_URL: 'https://api.aiteni.com/v1',
  // 开发环境可以使用本地地址
  // BASE_URL: 'http://localhost:8000/api/v1',
  
  TIMEOUT: 10000 // 请求超时时间（毫秒）
}

/**
 * 通用请求方法
 */
function request(options) {
  const { url, method = 'GET', data = {}, needAuth = true } = options

  return new Promise((resolve, reject) => {
    // 构建请求头
    const header = {
      'Content-Type': 'application/json'
    }

    // 添加认证token
    if (needAuth) {
      const token = wx.getStorageSync('token')
      if (token) {
        header['Authorization'] = `Bearer ${token}`
      }
    }

    wx.request({
      url: `${CONFIG.BASE_URL}${url}`,
      method,
      data,
      header,
      timeout: CONFIG.TIMEOUT,
      success: (res) => {
        const { statusCode, data } = res

        // 处理HTTP状态码
        if (statusCode >= 200 && statusCode < 300) {
          // 处理业务状态码
          if (data.code === 200) {
            resolve(data.data)
          } else {
            // 业务错误
            wx.showToast({
              title: data.message || '操作失败',
              icon: 'none'
            })
            reject(data)
          }
        } else if (statusCode === 401) {
          // 未授权，清除token并跳转到登录
          wx.removeStorageSync('token')
          wx.showToast({
            title: '请重新登录',
            icon: 'none'
          })
          // TODO: 跳转到登录页
          reject(data)
        } else {
          // HTTP错误
          wx.showToast({
            title: `请求失败 (${statusCode})`,
            icon: 'none'
          })
          reject(data)
        }
      },
      fail: (err) => {
        console.error('Request failed:', err)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * 用户认证相关API
 */
const authAPI = {
  /**
   * 微信登录
   */
  wxLogin(code) {
    return request({
      url: '/auth/wx-login',
      method: 'POST',
      data: { code },
      needAuth: false
    })
  }
}

/**
 * 问卷配置相关API
 */
const questionnaireAPI = {
  /**
   * 获取问卷配置
   */
  getConfig() {
    return request({
      url: '/questionnaire/config',
      method: 'GET',
      needAuth: false
    })
  },

  /**
   * 获取维度配置
   */
  getDimensions() {
    return request({
      url: '/questionnaire/dimensions',
      method: 'GET',
      needAuth: false
    })
  }
}

/**
 * 评估相关API
 */
const evaluationAPI = {
  /**
   * 提交评测答案
   */
  submit(answers) {
    return request({
      url: '/evaluation/submit',
      method: 'POST',
      data: { answers }
    })
  },

  /**
   * 获取评测结果
   */
  getResult(resultId) {
    return request({
      url: `/evaluation/result/${resultId}`,
      method: 'GET'
    })
  },

  /**
   * 获取评测历史
   */
  getHistory(page = 1, pageSize = 10) {
    return request({
      url: '/evaluation/history',
      method: 'GET',
      data: { page, pageSize }
    })
  },

  /**
   * 删除评测记录
   */
  deleteResult(resultId) {
    return request({
      url: `/evaluation/result/${resultId}`,
      method: 'DELETE'
    })
  }
}

/**
 * 训练建议相关API
 */
const trainingAPI = {
  /**
   * 获取训练计划
   */
  getPlan(resultId) {
    return request({
      url: `/training/plan/${resultId}`,
      method: 'GET'
    })
  }
}

// 导出所有API
module.exports = {
  auth: authAPI,
  questionnaire: questionnaireAPI,
  evaluation: evaluationAPI,
  training: trainingAPI
}
