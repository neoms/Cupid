<template>
  <div class="page">
    <h2>📝 创建/更新资料</h2>

    <div class="form">
      <div class="grid">
        <div><label>昵称 *</label><input v-model="form.nickname" placeholder="1-30字" /></div>
        <div><label>性别 *</label><select v-model="form.gender"><option value="">请选择</option><option value="男">男</option><option value="女">女</option></select></div>
        <div><label>出生日期 *</label><input type="date" v-model="form.birth_date" /></div>
        <div><label>身高 (cm) *</label><input type="number" v-model.number="form.height" min="140" max="220" /></div>
        <div><label>体重 (kg)</label><input type="number" v-model.number="form.weight" min="30" max="200" placeholder="选填" /></div>
        <div><label>省份 *</label><input v-model="form.province" placeholder="如 广东" /></div>
        <div><label>城市 *</label><input v-model="form.city" placeholder="如 深圳" /></div>
        <div><label>学历 *</label><select v-model="form.education"><option value="">请选择</option><option value="高中">高中</option><option value="大专">大专</option><option value="本科">本科</option><option value="硕士">硕士</option><option value="博士">博士</option></select></div>
        <div><label>毕业院校</label><input v-model="form.school" placeholder="选填" /></div>
        <div><label>职业 *</label><input v-model="form.occupation" placeholder="如 程序员" /></div>
        <div><label>行业</label><input v-model="form.industry" placeholder="如 互联网" /></div>
        <div><label>年收入</label><select v-model="form.income_range"><option value="">请选择</option><option value="10万以下">10万以下</option><option value="10-20万">10-20万</option><option value="20-50万">20-50万</option><option value="50-100万">50-100万</option><option value="100万以上">100万以上</option></select></div>
        <div><label>体型</label><select v-model="form.body_type"><option value="">请选择</option><option value="偏瘦">偏瘦</option><option value="匀称">匀称</option><option value="运动型">运动型</option><option value="丰满">丰满</option></select></div>
        <div><label>婚姻状况</label><select v-model="form.marriage_status"><option value="未婚">未婚</option><option value="离异">离异</option><option value="丧偶">丧偶</option></select></div>
        <div><label>子女</label><select v-model="form.has_children"><option :value="false">无</option><option :value="true">有</option></select></div>
        <div><label>生育意愿</label><select v-model="form.want_children"><option :value="null">未表态</option><option :value="true">想要</option><option :value="false">不想要</option></select></div>
        <div><label>吸烟</label><select v-model="form.smoking"><option :value="null">未知</option><option :value="false">不吸</option><option :value="true">吸烟</option></select></div>
        <div><label>饮酒</label><select v-model="form.drinking"><option :value="null">未知</option><option :value="false">不喝</option><option :value="true">饮酒</option></select></div>
      </div>

      <div class="full-width"><label>兴趣爱好（逗号分隔）</label><input v-model="interestsText" placeholder="跑步, 电影, 旅行" /></div>
      <div class="full-width"><label>自我介绍</label><textarea v-model="form.self_intro" rows="3" placeholder="最多500字"></textarea></div>

      <details class="pref">
        <summary>择偶偏好（选填）</summary>
        <div class="grid">
          <div><label>期望性别</label><select v-model="pref.gender"><option value="">不限</option><option value="男">男</option><option value="女">女</option></select></div>
          <div><label>最小年龄</label><input type="number" v-model.number="pref.age_min" /></div>
          <div><label>最大年龄</label><input type="number" v-model.number="pref.age_max" /></div>
          <div><label>最低身高</label><input type="number" v-model.number="pref.height_min" /></div>
          <div><label>最高身高</label><input type="number" v-model.number="pref.height_max" /></div>
          <div><label>学历</label><select v-model="pref.education"><option value="">不限</option><option value="高中">高中</option><option value="大专">大专</option><option value="本科">本科</option><option value="硕士">硕士</option><option value="博士">博士</option></select></div>
          <div><label>省份</label><input v-model="pref.province" /></div>
          <div><label>城市</label><input v-model="pref.city" /></div>
          <div><label>婚姻状况</label><select v-model="pref.marriage_status"><option value="">不限</option><option value="未婚">未婚</option><option value="离异">离异</option><option value="丧偶">丧偶</option></select></div>
        </div>
      </details>

      <button @click="submit" :disabled="submitting">提交资料</button>
    </div>

    <div v-if="error" class="toast error">{{ error }}</div>
    <div v-if="success" class="toast success">{{ success }}</div>
    <div v-if="result" class="result-card">
      <p><strong>{{ result.nickname }}</strong> · {{ result.gender }} · {{ result.age }}岁</p>
      <p>{{ result.province }} {{ result.city }} · {{ result.occupation }}</p>
      <p class="small">user_id: {{ result.user_id }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { createProfile } from '../api'
import type { Profile, ProfileCreate, PartnerPreference } from '../types/api'

const interestsText = ref('')
const form = reactive<ProfileCreate>({
  nickname: '', gender: '' as any, birth_date: '', height: 0, weight: undefined,
  province: '', city: '', education: '' as any, school: '', occupation: '', industry: '',
  income_range: undefined, body_type: undefined, marriage_status: '未婚',
  has_children: false, want_children: null, smoking: null, drinking: null, self_intro: '',
})
const pref = reactive<PartnerPreference>({
  gender: undefined, age_min: 20, age_max: 40,
  height_min: undefined, height_max: undefined,
  education: undefined, province: '', city: '', marriage_status: undefined,
})
const submitting = ref(false)
const error = ref('')
const success = ref('')
const result = ref<Profile | null>(null)

async function submit() {
  submitting.value = true; error.value = ''; success.value = ''; result.value = null
  try {
    const body = { ...form }
    body.interests = interestsText.value ? interestsText.value.split(/[,，]/).map(s => s.trim()).filter(Boolean) : []
    body.preference = pref
    if (!body.preference.gender) delete body.preference.gender
    if (!body.preference.education) delete body.preference.education
    if (!body.preference.marriage_status) delete body.preference.marriage_status
    const { data } = await createProfile(body)
    result.value = data; success.value = '资料提交成功！'
  } catch (e: any) {
    error.value = '提交失败：' + (e.response?.data?.detail || e.message)
  } finally { submitting.value = false }
}
</script>

<style scoped>
.page { max-width: 760px; margin: 0 auto; padding: 40px 24px; }
h2 { font-size: 1.3rem; font-weight: 700; margin-bottom: 20px; color: #2c3e50; }
.form { background: #fff; border: 1px solid #eef1f5; padding: 28px; border-radius: 12px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.full-width { margin-top: 16px; }
label { display: block; margin-bottom: 4px; font-weight: 600; font-size: 0.8rem; color: #5a6d80; text-transform: uppercase; letter-spacing: 0.3px; }
input, select, textarea {
  width: 100%; padding: 9px 11px; border: 1px solid #dde0e5; border-radius: 8px;
  font-size: 0.88rem; font-family: inherit; box-sizing: border-box;
  background: #fafbfc; color: #2c3e50; transition: border-color 0.15s, background 0.15s;
}
input:focus, select:focus, textarea:focus { outline: none; border-color: #e0526e; background: #fff; }
textarea { resize: vertical; }
.pref { margin-top: 18px; }
.pref summary { cursor: pointer; color: #e0526e; font-size: 0.9rem; font-weight: 600; margin-bottom: 12px; }
button {
  width: 100%; padding: 11px; margin-top: 20px; border: none; border-radius: 8px;
  font-size: 0.9rem; font-weight: 600; cursor: pointer;
  background: #e0526e; color: #fff; transition: background 0.15s;
}
button:hover { background: #cc3d58; }
button:disabled { background: #dde0e5; color: #9ba8b4; cursor: not-allowed; }
.toast { padding: 12px 16px; border-radius: 8px; margin-top: 16px; font-size: 0.9rem; }
.toast.error { background: #fff0f0; border: 1px solid #fdd; color: #c62828; }
.toast.success { background: #f0faf0; border: 1px solid #d4edda; color: #2d6a4f; }
.result-card { margin-top: 16px; background: #fff; border: 1px solid #eef1f5; padding: 16px; border-radius: 10px; }
.result-card p { margin: 4px 0; }
.small { font-size: 0.8rem; color: #9ba8b4; }
</style>
