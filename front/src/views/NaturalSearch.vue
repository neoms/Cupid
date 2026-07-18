<template>
  <div class="layout">
    <aside class="sidebar">
      <h2>🔍 语义搜索</h2>

      <label>描述你理想中的对象</label>
      <textarea v-model="query" placeholder="例如：30岁左右的程序员，喜欢运动和旅行，性格开朗大方" rows="4"></textarea>

      <label class="checkbox">
        <input type="checkbox" v-model="useOptimization" />
        开启 AI 查询优化
      </label>
      <label class="checkbox">
        <input type="checkbox" v-model="useRerank" />
        开启 AI 重排序
      </label>

      <div class="divider"></div>

      <label>性别</label>
      <select v-model="gender"><option value="">不限</option><option value="男">男</option><option value="女">女</option></select>

      <label>学历</label>
      <select v-model="education"><option value="">不限</option><option value="高中">高中</option><option value="大专">大专</option><option value="本科">本科</option><option value="硕士">硕士</option><option value="博士">博士</option></select>

      <label>婚姻状况</label>
      <select v-model="marriageStatus"><option value="">不限</option><option value="未婚">未婚</option><option value="离异">离异</option><option value="丧偶">丧偶</option></select>

      <label>年龄范围</label>
      <div class="range">
        <input type="number" v-model.number="ageMin" min="18" max="100" placeholder="不限" />
        <span>—</span>
        <input type="number" v-model.number="ageMax" min="18" max="100" placeholder="不限" />
      </div>

      <label>身高范围 (cm)</label>
      <div class="range">
        <input type="number" v-model.number="heightMin" min="140" max="220" placeholder="不限" />
        <span>—</span>
        <input type="number" v-model.number="heightMax" min="140" max="220" placeholder="不限" />
      </div>

      <label>省份</label>
      <input v-model="province" placeholder="不限" />
      <label>城市</label>
      <input v-model="city" placeholder="不限" />
      <label>职业</label>
      <input v-model="occupation" placeholder="不限" />

      <button @click="search" :disabled="loading || !query">
        {{ loading ? '搜索中...' : '开始搜索' }}
      </button>
    </aside>

    <section class="main">
      <div v-if="optimizedQuery" class="optimized">
        <strong>AI 优化后：</strong>{{ optimizedQuery }}
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <div v-if="!results.length && !loading && !total" class="empty">
        <span class="empty-icon">💝</span>
        <p>在左侧输入你理想中 TA 的描述，开启搜索</p>
      </div>

      <div class="result-area" v-if="results.length">
        <p class="count">共 {{ total }} 条结果（第 {{ page }} 页）</p>

        <div class="profile-card" v-for="(item, idx) in results" :key="idx">
          <div class="card-top">
            <div class="avatar-circle">{{ item.profile.nickname.charAt(0) }}</div>
            <div class="card-info">
              <div class="name-row">
                <strong>{{ item.profile.nickname }}</strong>
                <span class="match">{{ (item.score * 100).toFixed(0) }}% 匹配</span>
              </div>
              <div class="meta">
                {{ item.profile.gender }} · {{ item.profile.age }}岁 · {{ item.profile.height }}cm · {{ item.profile.education }}
              </div>
              <div class="meta secondary">
                {{ item.profile.occupation }} · {{ item.profile.province }} {{ item.profile.city }}
              </div>
            </div>
          </div>
          <p class="intro" v-if="item.profile.self_intro">{{ item.profile.self_intro }}</p>
          <div class="tags" v-if="item.profile.interests?.length">
            <span class="tag" v-for="t in item.profile.interests" :key="t">{{ t }}</span>
          </div>
        </div>

        <div class="pagination" v-if="total > pageSize">
          <button :disabled="page <= 1" @click="page--; search()">上一页</button>
          <span>{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
          <button :disabled="page >= Math.ceil(total / pageSize)" @click="page++; search()">下一页</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { naturalSearch } from '../api'
import type { SearchResult } from '../types/api'

const query = ref('')
const useOptimization = ref(false)
const useRerank = ref(true)
const gender = ref('')
const education = ref('')
const marriageStatus = ref('')
const ageMin = ref<number | null>(null)
const ageMax = ref<number | null>(null)
const heightMin = ref<number | null>(null)
const heightMax = ref<number | null>(null)
const province = ref('')
const city = ref('')
const occupation = ref('')

const loading = ref(false)
const error = ref('')
const results = ref<SearchResult[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const optimizedQuery = ref('')

async function search() {
  loading.value = true
  error.value = ''
  results.value = []
  total.value = 0
  try {
    const params = {
      query: query.value, min_score: 0.5,
      use_query_optimization: useOptimization.value,
      use_rerank: useRerank.value, rerank_top_k: 50,
      page: page.value, page_size: pageSize,
      gender: gender.value || undefined,
      education: education.value || undefined,
      marriage_status: marriageStatus.value || undefined,
      age_min: ageMin.value ?? undefined, age_max: ageMax.value ?? undefined,
      height_min: heightMin.value ?? undefined, height_max: heightMax.value ?? undefined,
      province: province.value || undefined,
      city: city.value || undefined,
      occupation: occupation.value || undefined,
    }
    const { data } = await naturalSearch(params)
    results.value = data.results
    total.value = data.total
    optimizedQuery.value = data.optimized_query || ''
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
  width: 24%; min-width: 260px; max-width: 320px;
  background: #fff; border-right: 1px solid #eef1f5;
  padding: 24px 20px; overflow-y: auto;
  position: sticky; top: 54px; height: calc(100vh - 54px);
}
.sidebar h2 { font-size: 1.1rem; font-weight: 700; margin-bottom: 18px; color: #2c3e50; }
.sidebar label { display: block; font-size: 0.8rem; font-weight: 600; color: #5a6d80; margin: 10px 0 4px; text-transform: uppercase; letter-spacing: 0.3px; }
.sidebar textarea, .sidebar input, .sidebar select {
  width: 100%; padding: 9px 11px; border: 1px solid #dde0e5; border-radius: 8px;
  font-size: 0.88rem; font-family: inherit; box-sizing: border-box;
  background: #fafbfc; color: #2c3e50; transition: border-color 0.15s, background 0.15s;
}
.sidebar textarea:focus, .sidebar input:focus, .sidebar select:focus {
  outline: none; border-color: #e0526e; background: #fff;
}
.sidebar textarea { resize: vertical; }
.checkbox { display: flex; align-items: center; gap: 8px; font-weight: 500; text-transform: none; font-size: 0.85rem; cursor: pointer; margin: 8px 0; }
.checkbox input { width: auto; accent-color: #e0526e; }
.divider { height: 1px; background: #eef1f5; margin: 14px 0 4px; }
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
.optimized { max-width: 680px; margin: 0 auto 18px; background: #fff; border: 1px solid #eef1f5; padding: 12px 16px; border-radius: 8px; font-size: 0.85rem; color: #5a6d80; }
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
.match { font-size: 0.8rem; font-weight: 700; color: #e0526e; background: #fff0f3; padding: 2px 10px; border-radius: 12px; }
.meta { font-size: 0.83rem; color: #5a6d80; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta.secondary { color: #9ba8b4; }
.intro { margin-top: 12px; font-size: 0.88rem; color: #5a6d80; line-height: 1.6; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.tag { background: #f0f2f5; padding: 3px 12px; border-radius: 20px; font-size: 0.78rem; color: #5a6d80; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 28px; }
.pagination button { width: auto; padding: 7px 22px; background: #fff; color: #5a6d80; border: 1px solid #dde0e5; }
.pagination button:hover:not(:disabled) { background: #f8f9fa; border-color: #b0bcc8; }
.pagination button:disabled { background: #f8f9fa; border-color: #eef1f5; color: #c0c8d0; }
.pagination span { font-size: 0.9rem; color: #5a6d80; }
</style>
