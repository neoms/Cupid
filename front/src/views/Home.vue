<template>
  <div class="home">
    <h1>晓夕成家</h1>
    <p class="subtitle">找到那个对的人</p>

    <div v-if="status === 'ok'" class="status">🟢 服务运行中</div>
    <div v-else-if="status === 'error'" class="status error">
      🔴 后端未连接 — 请先启动服务
    </div>
    <div v-else class="status">⏳ 正在检测...</div>

    <div class="nav-cards">
      <router-link to="/search/natural" class="card">
        <span class="icon">🔍</span>
        <div>
          <h3>语义搜索</h3>
          <p>用自然语言描述你心中的 TA，AI 帮你精准匹配</p>
        </div>
      </router-link>
      <router-link to="/search/structured" class="card">
        <span class="icon">📋</span>
        <div>
          <h3>条件筛选</h3>
          <p>按年龄、学历、地区等条件精确查找</p>
        </div>
      </router-link>
      <router-link to="/create" class="card">
        <span class="icon">📝</span>
        <div>
          <h3>创建资料</h3>
          <p>完善你的交友资料，让对的人更快找到你</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { healthCheck } from '../api'

const status = ref<'loading' | 'ok' | 'error'>('loading')

onMounted(async () => {
  try {
    await healthCheck()
    status.value = 'ok'
  } catch {
    status.value = 'error'
  }
})
</script>

<style scoped>
.home { max-width: 680px; margin: 0 auto; padding: 80px 20px; text-align: center; }
h1 { font-size: 2.4rem; font-weight: 800; color: #e0526e; margin-bottom: 4px; }
.subtitle { font-size: 1.05rem; color: #7d8e9e; margin-bottom: 28px; }
.status { font-size: 0.85rem; padding: 6px 16px; border-radius: 20px; display: inline-block; background: #f0faf0; color: #2d6a4f; margin-bottom: 48px; }
.status.error { background: #fff0f0; color: #c62828; }
.nav-cards { display: flex; flex-direction: column; gap: 14px; }
.card {
  display: flex; align-items: center; gap: 20px;
  padding: 20px 24px; border-radius: 12px; background: #fff;
  border: 1px solid #eef1f5; text-decoration: none;
  text-align: left; transition: box-shadow 0.15s, border-color 0.15s;
}
.card:hover { box-shadow: 0 2px 16px rgba(0,0,0,0.06); border-color: #dde0e5; }
.icon { font-size: 1.6rem; flex-shrink: 0; }
.card h3 { font-size: 1rem; font-weight: 700; color: #2c3e50; margin-bottom: 4px; }
.card p { font-size: 0.85rem; color: #7d8e9e; margin: 0; }
</style>
