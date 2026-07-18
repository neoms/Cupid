<template>
  <div class="layout">
    <aside class="sidebar">
      <h2>📋 条件筛选</h2>

      <label>性别</label>
      <select v-model="params.gender"><option value="">不限</option><option value="男">男</option><option value="女">女</option></select>

      <label>学历</label>
      <select v-model="params.education"><option value="">不限</option><option value="高中">高中</option><option value="大专">大专</option><option value="本科">本科</option><option value="硕士">硕士</option><option value="博士">博士</option></select>

      <label>婚姻状况</label>
      <select v-model="params.marriage_status"><option value="">不限</option><option value="未婚">未婚</option><option value="离异">离异</option><option value="丧偶">丧偶</option></select>

      <label>年龄范围</label>
      <div class="range">
        <input type="number" v-model.number="params.age_min" min="18" max="100" placeholder="不限" />
        <span>—</span>
        <input type="number" v-model.number="params.age_max" min="18" max="100" placeholder="不限" />
      </div>

      <label>身高范围 (cm)</label>
      <div class="range">
        <input type="number" v-model.number="params.height_min" min="140" max="220" placeholder="不限" />
        <span>—</span>
        <input type="number" v-model.number="params.height_max" min="140" max="220" placeholder="不限" />
      </div>

      <label>省份</label>
      <input v-model="params.province" placeholder="不限" />
      <label>城市</label>
      <input v-model="params.city" placeholder="不限" />
      <label>职业</label>
      <input v-model="params.occupation" placeholder="不限" />

      <button @click="search" :disabled="loading">搜索</button>
    </aside>

    <section class="main">
      <div v-if="error" class="error">{{ error }}</div>

      <div v-if="!results.length && !loading" class="empty">
        <span class="empty-icon">🔎</span>
        <p>设置筛选条件，开始查找</p>
      </div>

      <div class="result-area" v-if="results.length">
        <p class="count">共 {{ total }} 条结果（第 {{ params.page }} 页）</p>

        <div class="profile-card" v-for="(p, idx) in results" :key="idx">
          <div class="card-top">
            <div class="avatar-circle">{{ p.nickname.charAt(0) }}</div>
            <div class="card-info">
              <div class="name-row">
                <strong>{{ p.nickname }}</strong>
              </div>
              <div class="meta">
                {{ p.gender }} · {{ p.age }}岁 · {{ p.height }}cm · {{ p.education }}
              </div>
              <div class="meta secondary">
                {{ p.occupation }} · {{ p.province }} {{ p.city }}
              </div>
            </div>
          </div>
          <p class="intro" v-if="p.self_intro">{{ p.self_intro }}</p>
        </div>

        <div class="pagination" v-if="total > pageSize">
          <button :disabled="params.page <= 1" @click="params.page--; search()">上一页</button>
          <span>{{ params.page }} / {{ Math.ceil(total / pageSize) }}</span>
          <button :disabled="params.page >= Math.ceil(total / pageSize)" @click="params.page++; search()">下一页</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { searchProfiles } from '../api'
import type { Profile, SearchParams } from '../types/api'

const pageSize = 20

const params = reactive<SearchParams>({
  gender: undefined, education: undefined, marriage_status: undefined,
  age_min: undefined, age_max: undefined,
  height_min: undefined, height_max: undefined,
  province: '', city: '', occupation: '',
  page: 1, page_size: pageSize, sort_by: 'created_at',
})

const loading = ref(false)
const error = ref('')
const results = ref<Profile[]>([])
const total = ref(0)

async function search() {
  loading.value = true
  error.value = ''
  results.value = []
  try {
    const body: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(params)) {
      if (v !== '' && v !== undefined && v !== null) body[k] = v
    }
    const { data } = await searchProfiles(body as SearchParams)
    results.value = data.results
    total.value = data.total
  } catch (e: any) {
    error.value = '搜索失败：' + (e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.layout { display: flex; height: calc(100vh - 54px); }

/* ── 左侧 ── */
.sidebar {
  width: 24%; min-width: 240px; max-width: 300px;
  background: #fff; border-right: 1px solid #eef1f5;
  padding: 24px 20px; overflow-y: auto;
  position: sticky; top: 54px; height: calc(100vh - 54px);
}
.sidebar h2 { font-size: 1.1rem; font-weight: 700; margin-bottom: 18px; color: #2c3e50; }
.sidebar label { display: block; font-size: 0.8rem; font-weight: 600; color: #5a6d80; margin: 10px 0 4px; text-transform: uppercase; letter-spacing: 0.3px; }
.sidebar input, .sidebar select {
  width: 100%; padding: 9px 11px; border: 1px solid #dde0e5; border-radius: 8px;
  font-size: 0.88rem; font-family: inherit; box-sizing: border-box;
  background: #fafbfc; color: #2c3e50; transition: border-color 0.15s, background 0.15s;
}
.sidebar input:focus, .sidebar select:focus { outline: none; border-color: #e0526e; background: #fff; }
.range { display: flex; align-items: center; gap: 6px; }
.range input { flex: 1; }
.range span { color: #b0bcc8; font-size: 0.85rem; flex-shrink: 0; }
button {
  width: 100%; padding: 10px; margin-top: 20px; border: none; border-radius: 8px;
  font-size: 0.9rem; font-weight: 600; cursor: pointer;
  background: #e0526e; color: #fff; transition: background 0.15s;
}
button:hover { background: #cc3d58; }
button:disabled { background: #dde0e5; color: #9ba8b4; cursor: not-allowed; }

/* ── 右侧 ── */
.main { flex: 1; overflow-y: auto; padding: 28px 32px; background: #f8f9fa; }
.result-area { max-width: 680px; margin: 0 auto; }
.error { max-width: 680px; margin: 0 auto 18px; background: #fff0f0; border: 1px solid #fdd; padding: 12px 16px; border-radius: 8px; color: #c62828; font-size: 0.9rem; }
.empty { max-width: 680px; margin: 120px auto 0; text-align: center; }
.empty-icon { font-size: 2.4rem; display: block; margin-bottom: 12px; }
.empty p { color: #9ba8b4; font-size: 0.95rem; }
.count { font-size: 0.85rem; color: #9ba8b4; margin-bottom: 14px; }

.profile-card {
  background: #fff; border: 1px solid #eef1f5; border-radius: 12px;
  padding: 18px 20px; margin-bottom: 12px; transition: box-shadow 0.15s;
}
.profile-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.card-top { display: flex; align-items: flex-start; gap: 14px; }
.avatar-circle {
  width: 44px; height: 44px; border-radius: 50%; background: #fff0f3;
  color: #e0526e; font-weight: 700; font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.card-info { flex: 1; min-width: 0; }
.name-row { display: flex; align-items: center; gap: 10px; margin-bottom: 3px; }
.name-row strong { font-size: 0.95rem; color: #2c3e50; }
.meta { font-size: 0.83rem; color: #5a6d80; overflow: hidden; text-overflow: ellipsis; }
.meta.secondary { color: #9ba8b4; }
.intro { margin-top: 12px; font-size: 0.88rem; color: #5a6d80; line-height: 1.6; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 28px; }
.pagination button { width: auto; padding: 7px 22px; background: #fff; color: #5a6d80; border: 1px solid #dde0e5; }
.pagination button:hover:not(:disabled) { background: #f8f9fa; border-color: #b0bcc8; }
.pagination button:disabled { background: #f8f9fa; border-color: #eef1f5; color: #c0c8d0; }
.pagination span { font-size: 0.9rem; color: #5a6d80; }
</style>
