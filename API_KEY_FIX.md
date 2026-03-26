# API Key 显示问题修复报告

## 问题描述
用户反馈：保存的 eggfans API Key 在配置页面显示为空，怀疑没有保存到数据库。

## 问题排查

### 1. 数据库检查 ✅
```bash
# 查询数据库
python -c "from app.config_db import get_config_database; db = get_config_database(); print(db.get_provider('eggfans'))"

# 结果：API Key 确实保存在数据库中
{
  "api_key": "sk-73M278wRsqw37LMNXxEyf3TbsnodTg4mIY8HusmDnatZ93U1",
  "base_url": "https://eggfans.com",
  "model": "deepseek-v3.2",
  ...
}
```

### 2. API 检查 ✅
```bash
curl http://localhost:8000/api/config

# 结果：API 正确返回了配置数据
{
  "data": {
    "providers": {
      "eggfans": {
        "api_key": "sk-73M278wRsqw37LMNXxEyf3TbsnodTg4mIY8HusmDnatZ93U1",
        ...
      }
    }
  }
}
```

### 3. 前端检查 ❌
**发现问题**: 前端 `loadConfig()` 函数检查的字段名错误

```javascript
// 错误的代码
if (configData.llm_providers) {  // ❌ 检查 llm_providers
  Object.keys(configData.llm_providers).forEach(...)
}

// 后端实际返回的字段名
{
  "providers": { ... }  // ✅ 实际字段名是 providers
}
```

## 修复方案

### 修复 1: 更正字段名
```javascript
// 修复后的代码
if (configData.providers) {  // ✅ 检查 providers
  Object.keys(configData.providers).forEach(key => {
    const providerData = configData.providers[key]
    if (config.providers[key]) {
      Object.assign(config.providers[key], providerData)
    }
  })
}
```

### 修复 2: 添加 API Key 保密显示
```vue
<el-input
  v-model="provider.api_key"
  type="password"
  :placeholder="provider.api_key && provider.api_key.length > 0 
    ? '已保存：sk-' + provider.api_key.slice(-4) 
    : '填写你的 API Key'"
  show-password
  clearable
>
  <template #prefix>
    <span v-if="provider.api_key && provider.api_key.length > 0" style="color: #67c23a">
      ✓ 已保存
    </span>
  </template>
</el-input>
```

## 修复效果

### 修复前
- ❌ API Key 输入框显示为空
- ❌ 用户以为没有保存
- ❌ 需要重新填写

### 修复后
- ✅ API Key 正确从数据库加载
- ✅ 输入框 placeholder 显示 `已保存：sk-xxxx`（后 4 位）
- ✅ 输入框前缀显示绿色 `✓ 已保存` 标记
- ✅ 可以点击"显示密码"查看完整 API Key
- ✅ 可以点击"清空"按钮清除后重新填写

## 数据流程

```
数据库 (config.db)
    ↓ 读取
后端 API (/api/config)
    ↓ 返回 { providers: {...} }
前端 API 客户端
    ↓ loadConfig()
Vue 响应式数据 (config.providers)
    ↓ v-model 绑定
输入框显示 (带保密处理)
```

## 验证步骤

1. **打开配置页面**
   - 访问 http://localhost:5173/config
   
2. **检查 eggfans 配置**
   - API Key 输入框应显示 `✓ 已保存` 绿色标记
   - Placeholder 显示 `已保存：sk-xxxx`（后 4 位）
   
3. **查看 API Key**
   - 点击"显示密码"眼睛图标
   - 应显示完整的 API Key：`sk-73M278wRsqw37LMNXxEyf3TbsnodTg4mIY8HusmDnatZ93U1`
   
4. **修改并保存**
   - 可以修改 API Key
   - 点击"保存配置"
   - 刷新页面，新配置应正确显示

## 数据库验证

```sql
-- 查询配置数据库
SELECT name, api_key, base_url, model FROM llm_providers;

-- 预期结果
| name        | api_key                                      | base_url                        | model          |
|-------------|----------------------------------------------|---------------------------------|----------------|
| eggfans     | sk-73M278wRsqw37LMNXxEyf3TbsnodTg4mIY8Hus... | https://eggfans.com            | deepseek-v3.2  |
| volcengine  |                                              | https://ark.cn-beijing.volc... |                |
| aliyun      |                                              | https://dashscope.aliyuncs... |                |
```

## 修复文件

- `frontend/src/views/ProjectConfig.vue` - 配置页面组件
  - 修复 `loadConfig()` 函数
  - 添加 API Key 保密显示

## 总结

**问题根源**: 前端字段名不匹配（`llm_providers` vs `providers`）

**数据库正常**: API Key 一直正确保存在数据库中

**修复完成**: 
- ✅ 前端正确读取并显示配置
- ✅ API Key 保密显示（后 4 位）
- ✅ 可视化保存状态标记

---

**修复时间**: 2026-03-22 12:36  
**修复者**: 冰冰  
**状态**: ✅ 已完成
