<template>
  <view class="about-page">
    <view class="hero-section">
      <image class="hero-bg" src="/static/ui/backgrounds/bg-about-hero.png" mode="aspectFill" />
      <view class="hero-overlay"></view>
      <view class="hero-blob hero-blob-left"></view>
      <view class="hero-blob hero-blob-right"></view>
      <image class="hero-decor hero-decor-tl" src="/static/ui/decor/leaf-corner-tl.png" mode="aspectFit" />
      <image class="hero-decor hero-decor-br" src="/static/ui/decor/leaf-corner-br.png" mode="aspectFit" />

      <view class="hero-content">
        <view class="brand-chip">
          <image class="brand-chip-icon" src="/static/ui/icons/ic-knowledge.svg" mode="aspectFit" />
          <text class="brand-chip-text">知识库</text>
        </view>
        <view class="hero-title">关于系统</view>
        <view class="hero-subtitle">智能识别 · 科学防治 · 农技知识沉淀</view>
      </view>
    </view>

    <view class="content-wrap">
      <view class="intro-card card">
        <image class="intro-bg" src="/static/ui/backgrounds/bg-leaf-closeup.png" mode="aspectFill" />
        <view class="intro-mask"></view>
        <view class="intro-content">
          <view class="intro-icon-wrap">
            <image class="intro-icon" src="/static/ui/icons/ic-recognize.svg" mode="aspectFit" />
          </view>
          <view class="intro-text-wrap">
            <text class="intro-title">基于 ResNet50 的病虫害识别及防治预警系统</text>
            <text class="intro-desc">面向农户与种植管理场景，提供作物病害识别、知识查询、历史追踪和社区交流等功能。</text>
          </view>
        </view>
      </view>

      <view class="stats-row">
        <view class="stat-card card">
          <view class="stat-icon-box green">
            <image class="stat-icon" src="/static/ui/icons/ic-knowledge.svg" mode="aspectFit" />
          </view>
          <text class="stat-number">{{ cropTypes.length }}</text>
          <text class="stat-label">作物类型</text>
        </view>
        <view class="stat-card card">
          <view class="stat-icon-box orange">
            <image class="stat-icon" src="/static/ui/icons/ic-warning.svg" mode="aspectFit" />
          </view>
          <text class="stat-number">{{ diseases.length }}</text>
          <text class="stat-label">病害条目</text>
        </view>
      </view>

      <view class="feature-card card">
        <view class="section-head">
          <view class="section-mark"></view>
          <text class="section-title">核心能力</text>
        </view>
        <view class="feature-grid">
          <view class="feature-item">
            <view class="feature-icon-wrap">
              <image class="feature-icon" src="/static/ui/icons/ic-recognize.svg" mode="aspectFit" />
            </view>
            <text class="feature-title">智能识别</text>
            <text class="feature-desc">上传叶片图片，快速返回作物、病害、置信度与严重程度。</text>
          </view>
          <view class="feature-item">
            <view class="feature-icon-wrap">
              <image class="feature-icon" src="/static/ui/icons/ic-solution.svg" mode="aspectFit" />
            </view>
            <text class="feature-title">防治建议</text>
            <text class="feature-desc">结合病害知识库，展示症状特征、用药方案和预防措施。</text>
          </view>
          <view class="feature-item">
            <view class="feature-icon-wrap">
              <image class="feature-icon" src="/static/ui/icons/ic-history.svg" mode="aspectFit" />
            </view>
            <text class="feature-title">历史追踪</text>
            <text class="feature-desc">自动保存识别记录，便于持续观察作物健康变化。</text>
          </view>
          <view class="feature-item">
            <view class="feature-icon-wrap">
              <image class="feature-icon" src="/static/ui/icons/ic-community.svg" mode="aspectFit" />
            </view>
            <text class="feature-title">社区交流</text>
            <text class="feature-desc">支持图文发帖、点赞与评论，沉淀种植经验。</text>
          </view>
        </view>
      </view>

      <view class="knowledge-card card">
        <view class="section-head section-head-between">
          <view class="section-head-left">
            <view class="section-mark"></view>
            <text class="section-title">病害知识库</text>
          </view>
          <text class="section-link" @tap="refreshData">刷新</text>
        </view>

        <view class="search-box">
          <image class="search-icon" src="/static/ui/icons/ic-knowledge.svg" mode="aspectFit" />
          <input
            class="search-input"
            v-model.trim="keyword"
            placeholder="搜索作物或病害名称"
            placeholder-class="search-placeholder"
          />
          <text class="search-clear" v-if="keyword" @tap="keyword = ''">清空</text>
        </view>

        <scroll-view class="crop-scroll" scroll-x>
          <view class="crop-chip-row">
            <view class="crop-chip" :class="{ active: activeCrop === '' }" @tap="selectCrop('')">全部</view>
            <view
              class="crop-chip"
              :class="{ active: activeCrop === crop.name }"
              v-for="crop in cropTypes"
              :key="crop.id"
              @tap="selectCrop(crop.name)"
            >
              {{ crop.name }}
            </view>
          </view>
        </scroll-view>

        <template v-if="loading">
          <view class="state-box">
            <text class="state-text">正在加载知识库...</text>
          </view>
        </template>

        <template v-else-if="filteredGroups.length === 0">
          <view class="empty-box">
            <image class="empty-image" src="/static/ui/empty/empty-knowledge.png" mode="aspectFit" />
            <text class="empty-title">暂无匹配内容</text>
            <text class="empty-desc">可以更换关键词，或切换到全部作物查看知识条目</text>
          </view>
        </template>

        <view class="disease-groups" v-else>
          <view class="disease-group" v-for="group in filteredGroups" :key="group.cropType">
            <view class="group-head" @tap="toggleGroup(group.cropType)">
              <view class="group-title-wrap">
                <view class="group-leaf-dot"></view>
                <text class="group-title">{{ group.cropType || '未分类作物' }}</text>
                <text class="group-count">{{ group.items.length }} 条</text>
              </view>
              <text class="group-arrow">{{ expandedMap[group.cropType] ? '收起' : '展开' }}</text>
            </view>

            <view class="disease-list" v-if="expandedMap[group.cropType]">
              <view class="disease-item" v-for="item in group.items" :key="item.id" @tap="openDiseaseDetail(item)">
                <view class="disease-top">
                  <view class="disease-name-wrap">
                    <text class="disease-name">{{ item.name }}</text>
                    <text class="disease-name-en" v-if="item.nameEn">{{ item.nameEn }}</text>
                  </view>
                  <view class="severity-badge" :class="itemBadgeClassMap[item.id] || ''">{{ normalizeSeverity(item.severityLevel) }}</view>
                </view>

                <view class="disease-desc" v-if="item.description">
                  <text>{{ item.description }}</text>
                </view>

                <view class="disease-actions">
                  <view class="mini-action" v-if="item.solutions" @tap.stop="openDiseaseDetail(item)">
                    <image class="mini-action-icon" src="/static/ui/icons/ic-solution.svg" mode="aspectFit" />
                    <text>防治方案</text>
                  </view>
                  <view class="mini-action" v-if="item.preventionMethods" @tap.stop="openDiseaseDetail(item)">
                    <image class="mini-action-icon" src="/static/ui/icons/ic-warning.svg" mode="aspectFit" />
                    <text>预防措施</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="detail-mask" v-if="detailVisible" @tap="closeDiseaseDetail"></view>
    <view class="detail-sheet" v-if="detailVisible">
      <view class="sheet-handle"></view>
      <view class="sheet-head">
        <view>
          <text class="sheet-title">{{ selectedDisease ? selectedDisease.name : '病害详情' }}</text>
          <text class="sheet-subtitle">{{ selectedDisease ? selectedDisease.cropType : '' }}</text>
        </view>
        <text class="sheet-close" @tap="closeDiseaseDetail">关闭</text>
      </view>

      <scroll-view class="detail-scroll" scroll-y>
        <view class="detail-content" v-if="selectedDisease">
          <view class="detail-summary-card">
            <view class="detail-summary-head">
              <image class="detail-summary-icon" src="/static/ui/icons/ic-knowledge.svg" mode="aspectFit" />
              <view class="detail-summary-text">
                <text class="detail-main-name">{{ selectedDisease.name }}</text>
                <text class="detail-sub-name" v-if="selectedDisease.nameEn">{{ selectedDisease.nameEn }}</text>
              </view>
              <view class="severity-badge" :class="selectedDiseaseBadgeClass">{{ normalizeSeverity(selectedDisease.severityLevel) }}</view>
            </view>
          </view>

          <view class="detail-block" v-if="selectedDisease.description">
            <text class="detail-block-title">症状特征</text>
            <text class="detail-block-text">{{ selectedDisease.description }}</text>
          </view>

          <view class="detail-block" v-if="selectedDisease.solutions">
            <text class="detail-block-title">防治方案</text>
            <text class="detail-block-text">{{ selectedDisease.solutions }}</text>
          </view>

          <view class="detail-block" v-if="selectedDisease.preventionMethods">
            <text class="detail-block-title">预防措施</text>
            <text class="detail-block-text">{{ selectedDisease.preventionMethods }}</text>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
import config from '@/config.js'

export default {
  data() {
    return {
      loading: false,
      cropTypes: [],
      diseases: [],
      keyword: '',
      activeCrop: '',
      expandedMap: {},
      detailVisible: false,
      selectedDisease: null,
      selectedDiseaseBadgeClass: '',
      itemBadgeClassMap: {}
    }
  },
  computed: {
    groupedDiseases() {
      const map = {}
      this.diseases.forEach(item => {
        const cropType = item.cropType || '未分类作物'
        if (!map[cropType]) map[cropType] = []
        map[cropType].push(item)
      })
      return Object.keys(map).map(cropType => ({
        cropType,
        items: map[cropType]
      }))
    },
    filteredGroups() {
      const keyword = this.keyword.toLowerCase()
      return this.groupedDiseases
        .map(group => {
          const cropMatch = !this.activeCrop || group.cropType === this.activeCrop
          if (!cropMatch) return null

          const items = group.items.filter(item => {
            if (!keyword) return true
            return [item.name, item.nameEn, item.cropType, item.description, item.solutions, item.preventionMethods]
              .filter(Boolean)
              .some(value => String(value).toLowerCase().includes(keyword))
          })

          if (!items.length) return null
          return { cropType: group.cropType, items }
        })
        .filter(Boolean)
    }
  },
  onLoad() {
    this.refreshData()
  },
  methods: {
    async refreshData() {
      if (this.loading) return
      this.loading = true
      try {
        const [cropTypes, diseases] = await Promise.all([
          this.fetchCropTypes(),
          this.fetchDiseases()
        ])
        this.diseases = diseases
        this.cropTypes = cropTypes.length ? cropTypes : this.deriveCropTypes(diseases)
        this.initExpandedMap()
        this.buildItemBadgeClassMap()
      } catch (error) {
        console.error('about data error:', error)
        this.toast('知识库加载失败')
      } finally {
        this.loading = false
      }
    },
    fetchCropTypes() {
      return new Promise((resolve, reject) => {
        uni.request({
          url: config.baseUrl + '/api/crop-types',
          method: 'GET',
          success: ({ data }) => {
            if (data && data.success) {
              resolve(data.cropTypes || [])
              return
            }
            reject(new Error((data && data.message) || '作物类型加载失败'))
          },
          fail: reject
        })
      })
    },
    fetchDiseases() {
      return new Promise((resolve, reject) => {
        uni.request({
          url: config.baseUrl + '/api/diseases',
          method: 'GET',
          success: ({ data }) => {
            if (data && data.success) {
              resolve(data.diseases || [])
              return
            }
            reject(new Error((data && data.message) || '病害知识加载失败'))
          },
          fail: reject
        })
      })
    },
    initExpandedMap() {
      const nextMap = {}
      const groups = this.groupedDiseases
      groups.forEach((group, index) => {
        nextMap[group.cropType] = index < 2
      })
      this.expandedMap = nextMap
    },
    buildItemBadgeClassMap() {
      const map = {}
      ;(this.diseases || []).forEach(item => {
        if (item.id != null) {
          map[item.id] = this.severityClass(item.severityLevel)
        }
      })
      this.itemBadgeClassMap = map
    },
    deriveCropTypes(diseases) {
      const names = Array.from(new Set((diseases || []).map(item => item.cropType).filter(Boolean)))
      return names.map((name, index) => ({
        id: index + 1,
        name,
        nameEn: ''
      }))
    },
    selectCrop(cropName) {
      this.activeCrop = cropName
      if (cropName && !this.expandedMap[cropName]) {
        this.expandedMap = {
          ...this.expandedMap,
          [cropName]: true
        }
      }
    },
    toggleGroup(cropType) {
      this.expandedMap = {
        ...this.expandedMap,
        [cropType]: !this.expandedMap[cropType]
      }
    },
    openDiseaseDetail(item) {
      this.selectedDisease = item
      this.selectedDiseaseBadgeClass = this.severityClass(item.severityLevel)
      this.detailVisible = true
    },
    closeDiseaseDetail() {
      this.detailVisible = false
      this.selectedDisease = null
      this.selectedDiseaseBadgeClass = ''
    },
    normalizeSeverity(level) {
      if (!level) return '未知'
      if (level === 'healthy') return '健康'
      if (level === 'general') return '一般'
      if (level === 'serious') return '严重'
      return level
    },
    severityClass(level) {
      const value = this.normalizeSeverity(level)
      if (value === '严重') return 'danger'
      if (value === '一般') return 'warning'
      if (value === '健康') return 'success'
      return ''
    },
    toast(title) {
      uni.showToast({ title, icon: 'none' })
    }
  }
}
</script>

<style>
page {
  min-height: 100%;
  background: linear-gradient(180deg, #edf7ed 0%, #f7fbf6 40%, #f4faf4 100%);
}

.about-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #edf7ed 0%, #f7fbf6 40%, #f4faf4 100%);
  padding-bottom: 48rpx;
}

.hero-section {
  position: relative;
  height: 410rpx;
  overflow: hidden;
  border-bottom-left-radius: 56rpx;
  border-bottom-right-radius: 56rpx;
}

.hero-bg,
.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.hero-overlay {
  background: linear-gradient(180deg, rgba(43, 130, 64, 0.20) 0%, rgba(65, 179, 92, 0.36) 48%, rgba(101, 204, 126, 0.66) 100%);
}

.hero-blob {
  position: absolute;
  border-radius: 50%;
  z-index: 2;
  filter: blur(8rpx);
}

.hero-blob-left {
  width: 180rpx;
  height: 180rpx;
  left: -52rpx;
  top: 106rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.30) 0%, rgba(255, 255, 255, 0.08) 58%, rgba(255, 255, 255, 0) 100%);
}

.hero-blob-right {
  width: 230rpx;
  height: 230rpx;
  right: -48rpx;
  top: 74rpx;
  background: radial-gradient(circle, rgba(214, 255, 222, 0.30) 0%, rgba(214, 255, 222, 0.08) 60%, rgba(214, 255, 222, 0) 100%);
}

.hero-decor{
  position: absolute;
  z-index: 2;
  pointer-events: none;
}

.hero-decor-tl {
  width: 520rpx;
  height: 520rpx;
  left: -8rpx;
  top: -6rpx;
  opacity: 0.82;
}

.hero-decor-br {
  width: 520rpx;
  height: 520rpx;
  right: -24rpx;
  bottom: -22rpx;
  opacity: 0.55;
}


.hero-content {
  position: relative;
  z-index: 3;
  padding: 72rpx 40rpx 0;
  color: #ffffff;
}

.brand-chip {
  height: 56rpx;
  padding: 0 20rpx 0 12rpx;
  display: inline-flex;
  align-items: center;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 8rpx 20rpx rgba(34, 91, 45, 0.10);
}

.brand-chip-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 10rpx;
}

.brand-chip-text {
  font-size: 24rpx;
}

.hero-title {
  color:#DD5710;
  margin-top: 28rpx;
  font-size: 62rpx;
  line-height: 1.08;
  font-weight: 700;
  letter-spacing: 2rpx;
  text-shadow: 0 8rpx 18rpx rgba(29, 85, 40, 0.16);
}

.hero-subtitle {
  margin-top: 18rpx;
  width: 560rpx;
  max-width: 100%;
  font-size: 28rpx;
  font-weight: bold;
  line-height: 1.6;
  color:#F5AB58;
}

.content-wrap {
  position: relative;
  z-index: 5;
  margin-top: -72rpx;
  padding: 0 24rpx 42rpx;
}

.card {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 32rpx;
  box-shadow: 0 20rpx 54rpx rgba(31, 101, 46, 0.10);
  border: 2rpx solid rgba(255, 255, 255, 0.7);
}

.intro-card {
  position: relative;
  min-height: 220rpx;
  padding: 28rpx;
  overflow: hidden;
}

.intro-bg,
.intro-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.intro-bg {
  opacity: 0.22;
}

.intro-mask {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.90) 58%, rgba(255, 255, 255, 0.78) 100%);
}

.intro-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
}

.intro-icon-wrap {
  width: auto;
  height: auto;
  border-radius: 0;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-shrink: 0;
}

.intro-icon {
  width: 100rpx;
  height: 100rpx;
}

.intro-text-wrap {
  min-width: 0;
  margin-left: 22rpx;
}

.intro-title {
  display: block;
  font-size: 34rpx;
  line-height: 1.35;
  font-weight: 700;
  color: #243126;
}

.intro-desc {
  display: block;
  margin-top: 12rpx;
  font-size: 25rpx;
  line-height: 1.7;
  color: #6c7d70;
}

.stats-row {
  margin-top: 24rpx;
  display: flex;
  gap: 20rpx;
}

.stat-card {
  flex: 1;
  min-width: 0;
  padding: 28rpx 24rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.stat-icon-box {
  width: auto;
  height: auto;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.stat-icon-box.green {
  background: transparent;
}

.stat-icon-box.orange {
  background: transparent;
}

.stat-icon {
  width: 80rpx;
  height: 80rpx;
}

.stat-number {
  margin-top: 20rpx;
  font-size: 52rpx;
  line-height: 1;
  font-weight: 800;
  color: #243126;
}

.stat-label {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #8a9a8d;
  font-weight: 600;
}

.feature-card,
.knowledge-card {
  margin-top: 24rpx;
  padding: 28rpx;
}

.section-head {
  display: flex;
  align-items: center;
}

.section-head-between {
  justify-content: space-between;
}

.section-head-left {
  display: flex;
  align-items: center;
}

.section-mark {
  width: 18rpx;
  height: 36rpx;
  border-radius: 999rpx;
  background: linear-gradient(180deg, #39a94b 0%, #72cf7b 100%);
  margin-right: 16rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #243126;
}

.section-link {
  font-size: 24rpx;
  color: #39a94b;
  font-weight: 600;
}

.feature-grid {
  margin-top: 22rpx;
  display: flex;
  flex-wrap: wrap;
}

.feature-item {
  width: calc(50% - 10rpx);
  min-height: 246rpx;
  padding: 24rpx 20rpx;
  box-sizing: border-box;
  border-radius: 26rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
}

.feature-item:nth-child(odd) {
  margin-right: 20rpx;
}

.feature-item:nth-child(1),
.feature-item:nth-child(2) {
  margin-bottom: 18rpx;
}

.feature-icon-wrap {
  width: auto;
  height: auto;
  border-radius: 0;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.feature-icon {
  width: 60rpx;
  height: 60rpx;
}

.feature-title {
  display: block;
  margin-top: 18rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #243126;
}

.feature-desc {
  display: block;
  margin-top: 10rpx;
  font-size: 23rpx;
  line-height: 1.65;
  color: #708072;
}

.search-box {
  margin-top: 24rpx;
  height: 84rpx;
  display: flex;
  align-items: center;
  border-radius: 999rpx;
  background: #f7faf7;
  border: 2rpx solid #e2ede3;
}

.search-icon {
  width: 60rpx;
  height: 60rpx;
  margin-left: 26rpx;
  margin-right: 16rpx;
}

.search-input {
  flex: 1;
  height: 84rpx;
  font-size: 28rpx;
  color: #243126;
}

.search-placeholder {
  color: #a3b0a5;
}

.search-clear {
  padding: 0 24rpx 0 10rpx;
  font-size: 24rpx;
  color: #39a94b;
  font-weight: 600;
}

.crop-scroll {
  margin-top: 22rpx;
  white-space: nowrap;
}

.crop-chip-row {
  display: inline-flex;
  gap: 12rpx;
  padding-bottom: 4rpx;
}

.crop-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 58rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  background: #f2f6f2;
  color: #738074;
  font-size: 24rpx;
  font-weight: 600;
}

.crop-chip.active {
  background: linear-gradient(90deg, #31b35d 0%, #42bb65 100%);
  color: #ffffff;
  box-shadow: 0 10rpx 22rpx rgba(57, 169, 75, 0.20);
}

.state-box,
.empty-box {
  padding: 42rpx 12rpx 28rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.state-text,
.empty-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #516154;
}

.empty-image {
  width: 240rpx;
  height: 170rpx;
  opacity: 0.96;
}

.empty-title {
  margin-top: 14rpx;
}

.empty-desc {
  margin-top: 10rpx;
  width: 520rpx;
  max-width: 100%;
  font-size: 24rpx;
  line-height: 1.7;
  color: #90a090;
  text-align: center;
}

.disease-groups {
  margin-top: 18rpx;
}

.disease-group {
  margin-top: 18rpx;
  border-radius: 26rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
  overflow: hidden;
}

.group-head {
  padding: 24rpx 22rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.group-title-wrap {
  min-width: 0;
  display: flex;
  align-items: center;
}

.group-leaf-dot {
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: #39a94b;
  box-shadow: 0 0 0 8rpx rgba(57, 169, 75, 0.10);
  margin-right: 16rpx;
  flex-shrink: 0;
}

.group-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #243126;
}

.group-count {
  margin-left: 12rpx;
  padding: 5rpx 14rpx;
  border-radius: 999rpx;
  background: #edf8ef;
  color: #39a94b;
  font-size: 20rpx;
  font-weight: 700;
}

.group-arrow {
  color: #39a94b;
  font-size: 24rpx;
  font-weight: 600;
  flex-shrink: 0;
}

.disease-list {
  padding: 0 18rpx 18rpx;
}

.disease-item {
  margin-top: 14rpx;
  padding: 22rpx;
  border-radius: 22rpx;
  background: #ffffff;
  box-shadow: 0 8rpx 22rpx rgba(31, 101, 46, 0.05);
}

.disease-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18rpx;
}

.disease-name-wrap {
  flex: 1;
  min-width: 0;
}

.disease-name {
  display: block;
  font-size: 29rpx;
  line-height: 1.45;
  font-weight: 700;
  color: #243126;
}

.disease-name-en {
  display: block;
  margin-top: 6rpx;
  font-size: 21rpx;
  line-height: 1.45;
  color: #97a698;
}

.severity-badge {
  padding: 9rpx 16rpx;
  border-radius: 999rpx;
  font-size: 21rpx;
  font-weight: 700;
  color: #5d6e60;
  background: #eef3ef;
  flex-shrink: 0;
}

.severity-badge.success {
  color: #2e7d32;
  background: #edf8ef;
}

.severity-badge.warning {
  color: #d5911c;
  background: #fff7e8;
}

.severity-badge.danger {
  color: #d95d5d;
  background: #fff1f1;
}

.disease-desc {
  margin-top: 16rpx;
  font-size: 24rpx;
  line-height: 1.75;
  color: #627366;
  max-height: 126rpx;
  overflow: hidden;
}

.disease-actions {
  margin-top: 18rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.mini-action {
  height: 54rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: #f2f7f2;
  color: #39a94b;
  font-size: 23rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.mini-action-icon {
  width: 26rpx;
  height: 26rpx;
}

.detail-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(22, 32, 24, 0.32);
  z-index: 30;
}

.detail-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 31;
  height: 76vh;
  background: #ffffff;
  border-top-left-radius: 34rpx;
  border-top-right-radius: 34rpx;
  box-shadow: 0 -16rpx 48rpx rgba(31, 101, 46, 0.12);
  overflow: hidden;
}

.sheet-handle {
  width: 92rpx;
  height: 8rpx;
  border-radius: 999rpx;
  background: #dbe6dc;
  margin: 18rpx auto 0;
}

.sheet-head {
  padding: 22rpx 28rpx 18rpx;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.sheet-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #243126;
}

.sheet-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  color: #8b9a8e;
}

.sheet-close {
  font-size: 24rpx;
  color: #39a94b;
  font-weight: 600;
  padding-top: 8rpx;
}

.detail-scroll {
  height: calc(76vh - 102rpx);
}

.detail-content {
  padding: 0 28rpx 42rpx;
}

.detail-summary-card {
  padding: 22rpx;
  border-radius: 26rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
}

.detail-summary-head {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.detail-summary-icon {
  width: 54rpx;
  height: 54rpx;
  flex-shrink: 0;
}

.detail-summary-text {
  flex: 1;
  min-width: 0;
}

.detail-main-name {
  display: block;
  font-size: 30rpx;
  line-height: 1.4;
  font-weight: 700;
  color: #243126;
}

.detail-sub-name {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  line-height: 1.4;
  color: #97a698;
}

.detail-block {
  margin-top: 18rpx;
  padding: 24rpx;
  border-radius: 24rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
}

.detail-block-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #243126;
}

.detail-block-text {
  display: block;
  margin-top: 12rpx;
  font-size: 25rpx;
  line-height: 1.8;
  color: #5f6f63;
}
</style>
