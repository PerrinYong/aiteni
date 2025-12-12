/**
 * 通用工具函数
 */

/**
 * 格式化日期
 * @param {Date|string} date 日期对象或ISO字符串
 * @param {string} format 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (typeof date === 'string') {
    date = new Date(date)
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

/**
 * 获取相对时间描述
 * @param {Date|string} date 日期
 */
function getRelativeTime(date) {
  if (typeof date === 'string') {
    date = new Date(date)
  }

  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else if (days < 30) {
    const weeks = Math.floor(days / 7)
    return `${weeks}周前`
  } else if (days < 365) {
    const months = Math.floor(days / 30)
    return `${months}个月前`
  } else {
    const years = Math.floor(days / 365)
    return `${years}年前`
  }
}

/**
 * 防抖函数
 */
function debounce(fn, delay = 300) {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 */
function throttle(fn, delay = 300) {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn.apply(this, args)
      lastTime = now
    }
  }
}

/**
 * 深拷贝
 */
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime())
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item))
  }

  const clonedObj = {}
  for (let key in obj) {
    if (obj.hasOwnProperty(key)) {
      clonedObj[key] = deepClone(obj[key])
    }
  }
  return clonedObj
}

/**
 * 保存数据到本地存储（带过期时间）
 * @param {string} key 键名
 * @param {any} data 数据
 * @param {number} expire 过期时间（秒），默认不过期
 */
function setStorage(key, data, expire = null) {
  const item = {
    data,
    timestamp: Date.now(),
    expire: expire ? expire * 1000 : null
  }
  
  try {
    wx.setStorageSync(key, item)
    return true
  } catch (e) {
    console.error('Storage save failed:', e)
    return false
  }
}

/**
 * 从本地存储获取数据（检查过期）
 * @param {string} key 键名
 */
function getStorage(key) {
  try {
    const item = wx.getStorageSync(key)
    if (!item) return null

    // 检查是否过期
    if (item.expire && Date.now() - item.timestamp > item.expire) {
      wx.removeStorageSync(key)
      return null
    }

    return item.data
  } catch (e) {
    console.error('Storage read failed:', e)
    return null
  }
}

/**
 * 清除过期的本地存储数据
 */
function clearExpiredStorage() {
  try {
    const info = wx.getStorageInfoSync()
    const keys = info.keys || []

    keys.forEach(key => {
      const item = wx.getStorageSync(key)
      if (item && item.expire && Date.now() - item.timestamp > item.expire) {
        wx.removeStorageSync(key)
      }
    })
  } catch (e) {
    console.error('Clear expired storage failed:', e)
  }
}

/**
 * 数组去重
 */
function unique(arr, key = null) {
  if (!key) {
    return [...new Set(arr)]
  }
  
  const seen = new Set()
  return arr.filter(item => {
    const val = item[key]
    if (seen.has(val)) {
      return false
    }
    seen.add(val)
    return true
  })
}

/**
 * 等级转换为描述
 */
function getLevelDescription(level) {
  const descriptions = {
    '1.0': '网球入门',
    '1.5': '网球入门',
    '2.0': '初学者',
    '2.5': '初学者',
    '3.0': '初级业余选手',
    '3.5': '发展中业余选手',
    '4.0': '中级业余选手',
    '4.5': '高级业余选手',
    '5.0': '优秀业余选手',
    '5.5': '顶尖业余/初级职业',
    '6.0': '初级职业选手',
    '6.5': '职业选手',
    '7.0': '世界级职业选手'
  }
  
  return descriptions[String(level)] || '业余选手'
}

/**
 * 维度名称映射
 */
const DIMENSION_NAMES = {
  baseline: '底线综合',
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  return: '接发球',
  net: '网前与高压',
  footwork: '步伐与场地覆盖',
  tactics: '战术与心理',
  match_result: '实战成绩',
  training: '训练背景'
}

/**
 * 获取维度中文名称
 */
function getDimensionName(key) {
  return DIMENSION_NAMES[key] || key
}

module.exports = {
  formatDate,
  getRelativeTime,
  debounce,
  throttle,
  deepClone,
  setStorage,
  getStorage,
  clearExpiredStorage,
  unique,
  getLevelDescription,
  getDimensionName,
  DIMENSION_NAMES
}
