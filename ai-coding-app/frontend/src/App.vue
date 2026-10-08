<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  AlertTriangle,
  BookOpen,
  Bug,
  CheckCircle2,
  Code2,
  DatabaseZap,
  FlaskConical,
  Loader2,
  MessageSquareText,
  Play,
  RefreshCw,
  Sparkles,
} from '@lucide/vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const modes = [
  { id: 'chat', label: '课程答疑', endpoint: '/api/chat', icon: BookOpen },
  { id: 'generate', label: '代码生成', endpoint: '/api/code/generate', icon: Code2 },
  { id: 'explain', label: '代码解释', endpoint: '/api/code/explain', icon: MessageSquareText },
  { id: 'debug', label: 'Bug 修复', endpoint: '/api/code/debug', icon: Bug },
  { id: 'testcase', label: '测试生成', endpoint: '/api/testcase/generate', icon: FlaskConical },
  { id: 'kb', label: '知识扩充', endpoint: '/api/kb/add', icon: DatabaseZap },
]

const activeMode = ref('chat')
const loading = ref(false)
const healthLoading = ref(false)
const error = ref('')
const health = ref(null)
const result = ref(null)

const form = reactive({
  question: '二叉树的层序遍历怎么写？',
  code: '',
  language: 'python',
  top_k: 10,
  top_n: 5,
})

const kbForm = reactive({
  corpus: 'code',
  filename: 'demo_note.md',
  content: '# 示例知识\n\n这里写入一段新的课程或算法知识，提交后会通过 MCP 调用 add_to_kb 并重建索引。',
})

const currentMode = computed(() => modes.find((item) => item.id === activeMode.value))
const references = computed(() => result.value?.references || [])
const diagnostics = computed(() => result.value?.diagnostics || [])
const testCases = computed(() => result.value?.test_cases || [])
const generatedCode = computed(() => result.value?.generated_code || '')

function setMode(id) {
  activeMode.value = id
  error.value = ''
  if (id === 'generate') {
    form.question = '用 Python 实现二分查找，并说明复杂度'
  } else if (id === 'debug') {
    form.question = '下面的二分查找为什么找不到最后一个元素？'
    form.code = `def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1`
  } else if (id === 'testcase') {
    form.question = '给快速排序生成测试用例'
  } else if (id === 'explain') {
    form.question = '解释这段快速排序代码'
    form.code = `def quick_sort(nums):
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    left = [x for x in nums if x < pivot]
    mid = [x for x in nums if x == pivot]
    right = [x for x in nums if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)`
  }
}

async function refreshHealth() {
  healthLoading.value = true
  try {
    const response = await fetch(`${API_BASE}/api/health`)
    health.value = await response.json()
  } catch (err) {
    health.value = { ok: false, mcp: { error: err.message } }
  } finally {
    healthLoading.value = false
  }
}

async function submitTask() {
  loading.value = true
  error.value = ''
  try {
    const mode = currentMode.value
    const payload = activeMode.value === 'kb'
      ? { ...kbForm }
      : {
          question: form.question,
          code: form.code,
          language: form.language,
          top_k: Number(form.top_k),
          top_n: Number(form.top_n),
        }
    const response = await fetch(`${API_BASE}${mode.endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || '请求失败')
    }
    result.value = activeMode.value === 'kb'
      ? {
          mode: 'kb',
          answer: data.message,
          generated_code: '',
          test_cases: [],
          diagnostics: [],
          references: data.references || [],
          provider: 'mcp-add_to_kb',
        }
      : data
    await refreshHealth()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(refreshHealth)
</script>

<template>
  <main class="app-shell">
    <aside class="sidebar" aria-label="任务模式">
      <div class="brand">
        <Sparkles :size="24" aria-hidden="true" />
        <div>
          <h1>校园代码智能助手</h1>
          <p>MCP RAG Workbench</p>
        </div>
      </div>

      <nav class="mode-list">
        <button
          v-for="mode in modes"
          :key="mode.id"
          type="button"
          class="mode-button"
          :class="{ active: activeMode === mode.id }"
          @click="setMode(mode.id)"
          :title="mode.label"
        >
          <component :is="mode.icon" :size="18" aria-hidden="true" />
          <span>{{ mode.label }}</span>
        </button>
      </nav>

      <section class="status-panel">
        <div class="status-head">
          <span>服务状态</span>
          <button type="button" class="icon-button" title="刷新状态" @click="refreshHealth">
            <Loader2 v-if="healthLoading" class="spin" :size="16" aria-hidden="true" />
            <RefreshCw v-else :size="16" aria-hidden="true" />
          </button>
        </div>
        <div class="status-row" :class="{ ok: health?.ok, bad: health && !health.ok }">
          <CheckCircle2 v-if="health?.ok" :size="16" aria-hidden="true" />
          <AlertTriangle v-else :size="16" aria-hidden="true" />
          <span>{{ health?.ok ? 'MCP 已连接' : 'MCP 未连接' }}</span>
        </div>
        <p class="status-detail">{{ health?.mcp?.url || 'http://127.0.0.1:8765/mcp' }}</p>
      </section>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">{{ currentMode.label }}</p>
          <h2>{{ activeMode === 'kb' ? '知识库扩充' : '智能辅助工作台' }}</h2>
        </div>
        <button type="button" class="run-button" @click="submitTask" :disabled="loading">
          <Loader2 v-if="loading" class="spin" :size="18" aria-hidden="true" />
          <Play v-else :size="18" aria-hidden="true" />
          <span>{{ loading ? '处理中' : '运行' }}</span>
        </button>
      </header>

      <div v-if="error" class="error-banner">
        <AlertTriangle :size="18" aria-hidden="true" />
        <span>{{ error }}</span>
      </div>

      <div class="work-grid">
        <section class="input-pane">
          <template v-if="activeMode !== 'kb'">
            <label class="field">
              <span>问题</span>
              <textarea v-model="form.question" rows="5" />
            </label>
            <label class="field">
              <span>代码片段</span>
              <textarea v-model="form.code" rows="10" spellcheck="false" />
            </label>
            <div class="control-row">
              <label class="compact-field">
                <span>语言</span>
                <select v-model="form.language">
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="java">Java</option>
                  <option value="cpp">C++</option>
                </select>
              </label>
              <label class="compact-field">
                <span>top_k</span>
                <input v-model.number="form.top_k" type="number" min="1" max="50" />
              </label>
              <label class="compact-field">
                <span>top_n</span>
                <input v-model.number="form.top_n" type="number" min="1" max="50" />
              </label>
            </div>
          </template>

          <template v-else>
            <div class="control-row">
              <label class="compact-field">
                <span>知识库</span>
                <select v-model="kbForm.corpus">
                  <option value="code">code</option>
                  <option value="course">course</option>
                </select>
              </label>
              <label class="compact-field grow">
                <span>文件名</span>
                <input v-model="kbForm.filename" type="text" />
              </label>
            </div>
            <label class="field">
              <span>内容</span>
              <textarea v-model="kbForm.content" rows="18" />
            </label>
          </template>
        </section>

        <section class="output-pane">
          <article class="answer-block">
            <div class="block-title">
              <MessageSquareText :size="18" aria-hidden="true" />
              <span>回答</span>
              <small v-if="result?.provider">{{ result.provider }}</small>
            </div>
            <p v-if="result?.answer" class="answer-text">{{ result.answer }}</p>
            <p v-else class="empty-text">等待运行结果</p>
          </article>

          <article v-if="generatedCode" class="answer-block">
            <div class="block-title">
              <Code2 :size="18" aria-hidden="true" />
              <span>代码</span>
            </div>
            <pre><code>{{ generatedCode }}</code></pre>
          </article>

          <article v-if="diagnostics.length" class="answer-block">
            <div class="block-title">
              <Bug :size="18" aria-hidden="true" />
              <span>修复建议</span>
            </div>
            <ul class="plain-list">
              <li v-for="item in diagnostics" :key="item">{{ item }}</li>
            </ul>
          </article>

          <article v-if="testCases.length" class="answer-block">
            <div class="block-title">
              <FlaskConical :size="18" aria-hidden="true" />
              <span>测试用例</span>
            </div>
            <ul class="plain-list">
              <li v-for="item in testCases" :key="item">{{ item }}</li>
            </ul>
          </article>
        </section>
      </div>
    </section>

    <aside class="references" aria-label="RAG 引用">
      <div class="references-head">
        <DatabaseZap :size="20" aria-hidden="true" />
        <div>
          <h2>知识库命中</h2>
          <p>{{ references.length }} 条引用</p>
        </div>
      </div>
      <div class="reference-list">
        <article v-for="ref in references" :key="`${ref.source}-${ref.chunk_index}-${ref.rank}`" class="reference-card">
          <div class="reference-meta">
            <strong>{{ ref.source }}</strong>
            <span>chunk {{ ref.chunk_index }} · {{ Number(ref.score).toFixed(4) }}</span>
          </div>
          <p>{{ ref.text }}</p>
        </article>
        <p v-if="!references.length" class="empty-text">暂无引用</p>
      </div>
    </aside>
  </main>
</template>
