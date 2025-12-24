/**
 * 统一的调试日志工具
 * 
 * 在开发时开启详细日志，在 release 版本时可以一键关闭
 */

// ========== 配置区 ==========
// 设置为 false 可以关闭所有调试日志（release 版本）
const DEBUG_ENABLED = true;

// 可以按模块单独控制日志
const MODULE_DEBUG = {
  markdown: true,      // Markdown 渲染相关
  questionnaire: true, // 问卷页面相关
  api: true,           // API 调用相关
  auth: true,          // 认证相关
  result: true,        // 结果页相关
  history: true,       // 历史记录相关
};
// ========== 配置区结束 ==========

/**
 * 调试日志输出
 * @param {string} module - 模块名称（如 'markdown', 'questionnaire'）
 * @param {string} message - 日志消息
 * @param {any} data - 可选的数据对象
 */
function debug(module, message, data) {
  if (!DEBUG_ENABLED) return;
  if (MODULE_DEBUG[module] === false) return;
  
  const prefix = `[DEBUG:${module}]`;
  
  if (data !== undefined) {
    console.log(prefix, message, data);
  } else {
    console.log(prefix, message);
  }
}

/**
 * 调试日志 - 简化版（不需要模块名）
 */
function log(...args) {
  if (!DEBUG_ENABLED) return;
  console.log(...args);
}

/**
 * 分组日志开始
 */
function groupStart(module, title) {
  if (!DEBUG_ENABLED) return;
  if (MODULE_DEBUG[module] === false) return;
  console.log(`[DEBUG:${module}] ${'='.repeat(50)}`);
  console.log(`[DEBUG:${module}] ${title}`);
  console.log(`[DEBUG:${module}] ${'-'.repeat(50)}`);
}

/**
 * 分组日志结束
 */
function groupEnd(module) {
  if (!DEBUG_ENABLED) return;
  if (MODULE_DEBUG[module] === false) return;
  console.log(`[DEBUG:${module}] ${'='.repeat(50)}`);
}

/**
 * 打印对象的 JSON 格式（美化）
 */
function json(module, label, obj) {
  if (!DEBUG_ENABLED) return;
  if (MODULE_DEBUG[module] === false) return;
  console.log(`[DEBUG:${module}] ${label}:`, JSON.stringify(obj, null, 2));
}

/**
 * 打印表格
 */
function table(module, label, array) {
  if (!DEBUG_ENABLED) return;
  if (MODULE_DEBUG[module] === false) return;
  console.log(`[DEBUG:${module}] ${label}:`);
  if (Array.isArray(array)) {
    array.forEach((item, idx) => {
      console.log(`  [${idx}]`, item);
    });
  } else {
    console.log('  (非数组数据)', array);
  }
}

module.exports = {
  debug,
  log,
  groupStart,
  groupEnd,
  json,
  table,
  
  // 导出配置，方便外部查看
  DEBUG_ENABLED,
  MODULE_DEBUG
};

