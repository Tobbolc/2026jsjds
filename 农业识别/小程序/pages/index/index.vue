<template>
  <view class="index-page">
    <view class="hero-section">
      <image class="hero-bg" src="/static/ui/backgrounds/bg-index-hero.png" mode="aspectFill" />
      <view class="hero-overlay"></view>
      <view class="hero-blob hero-blob-left"></view>
      <view class="hero-blob hero-blob-right"></view>
      <image class="hero-decor hero-decor-tl" src="/static/ui/decor/leaf-corner-tl.png" mode="aspectFit" />
      <image class="hero-decor hero-decor-br" src="/static/ui/decor/leaf-corner-br.png" mode="aspectFit" />

      <view class="hero-content">
        <view class="brand-chip">
          <image class="brand-chip-icon" src="/static/ui/decor/leaf-mini-badge.png" mode="aspectFit" />
          <text class="brand-chip-text">慧农之眼</text>
        </view>
        <view class="hero-title">识别中心</view>
        <view class="hero-subtitle">上传叶片图片，快速完成病虫害识别</view>
      </view>
    </view>

    <view class="content-wrap">
      <view class="welcome-card card">
        <view class="welcome-left">
          <view class="avatar-badge">{{ userInitial }}</view>
          <view class="welcome-meta">
            <text class="welcome-title">{{ userInfo ? `欢迎回来，${userInfo.username}` : '欢迎使用慧农之眼' }}</text>
            <view class="welcome-tags">
              <text class="welcome-tag">智能识别</text>
              <text class="welcome-tag">科学防治</text>
            </view>
          </view>
        </view>
        <view class="welcome-action" @tap="handleAuthAction">
          <text>{{ userInfo ? '退出' : '登录' }}</text>
        </view>
      </view>

      <view class="card section-card recognize-card">
        <view class="section-head">
          <view class="section-mark"></view>
          <text class="section-title">病虫害识别</text>
        </view>

        <view class="upload-box" @tap="chooseImage">
          <template v-if="selectedImage">
            <image class="upload-preview" :src="selectedImage" mode="aspectFill" />
            <view class="upload-mask">
              <view class="upload-mask-btn">重新选择</view>
            </view>
          </template>
          <template v-else>
            <image class="upload-empty" src="/static/ui/empty/empty-upload.png" mode="aspectFit" />
            <text class="upload-title">点击上传图片</text>
            <text class="upload-desc">支持 JPG、PNG 格式，建议上传清晰叶片图像</text>
          </template>
        </view>

        <button class="primary-btn" :loading="submitting" :disabled="submitting" @tap="handleRecognize">
          <text class="primary-btn-text">{{ submitting ? '识别中...' : '开始识别' }}</text>
        </button>
      </view>

      <view class="card section-card result-card" v-if="resultData && resultData.diseaseInfo">
        <view class="section-head section-head-between">
          <view class="section-head-left">
            <view class="section-mark"></view>
            <text class="section-title">识别结果</text>
          </view>
          <view class="severity-badge" :class="severityBadgeClass">
            {{ normalizeSeverity(resultData.diseaseInfo && resultData.diseaseInfo.severityLevel) }}
          </view>
        </view>

        <view class="result-summary">
          <view class="summary-item">
            <text class="summary-label">作物类型</text>
            <text class="summary-value">{{ resultData.cropInfo && resultData.cropInfo.cropName || '未知' }}</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">病害名称</text>
            <text class="summary-value highlight">{{ resultData.diseaseInfo && resultData.diseaseInfo.diseaseName || '未知' }}</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">识别置信度</text>
            <text class="summary-value">{{ formatDisplayConfidence(resultData.diseaseInfo && resultData.diseaseInfo.confidence) }}</text>
          </view>
        </view>

        <view class="result-panel" v-if="resultData.solution">
          <view class="result-block" v-if="resultData.solution.symptoms">
            <text class="result-block-title">症状特征</text>
            <text class="result-block-text">{{ resultData.solution.symptoms }}</text>
          </view>
          <view class="result-block" v-if="resultData.solution.solutions">
            <text class="result-block-title">防治建议</text>
            <text class="result-block-text">{{ resultData.solution.solutions }}</text>
          </view>
          <view class="result-block" v-if="resultData.solution.preventionMethods">
            <text class="result-block-title">预防措施</text>
            <text class="result-block-text">{{ resultData.solution.preventionMethods }}</text>
          </view>
        </view>
      </view>

      <view class="card section-card recent-card">
        <view class="section-head section-head-between">
          <view class="section-head-left">
            <view class="section-mark"></view>
            <text class="section-title">最近识别</text>
          </view>
          <text class="section-link" @tap="refreshHistory">刷新</text>
        </view>

        <template v-if="!userInfo">
          <view class="empty-box small-empty">
            <image class="empty-image" src="/static/ui/empty/empty-history.png" mode="aspectFit" />
            <text class="empty-title">登录后可查看识别历史</text>
            <text class="empty-desc">系统会自动保存你的识别记录与结果摘要</text>
          </view>
        </template>

        <template v-else-if="historyLoading">
          <view class="loading-box">
            <text class="loading-text">正在加载历史记录...</text>
          </view>
        </template>

        <template v-else-if="recentRecords.length === 0">
          <view class="empty-box small-empty">
            <image class="empty-image" src="/static/ui/empty/empty-history.png" mode="aspectFit" />
            <text class="empty-title">还没有识别记录</text>
            <text class="empty-desc">完成一次图片识别后，记录会自动保存在这里</text>
          </view>
        </template>

        <view class="record-list" v-else>
          <view class="record-item" v-for="item in recentRecords" :key="item.recordId" @tap="openRecordDetail(item)">
            <image class="record-thumb" :src="fullImageUrl(item.imagePath)" mode="aspectFill" />
            <view class="record-body">
              <view class="record-top">
                <text class="record-name">{{ item.diseaseName || '未知病害' }}</text>
                <text class="record-time">{{ item.createTime }}</text>
              </view>
              <view class="record-meta-row">
                <text class="record-chip">{{ item.cropName || '未知作物' }}</text>
                <text class="record-chip soft">{{ formatHistoryConfidence(item.confidence) }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="detail-mask" v-if="detailVisible" @tap="closeDetail"></view>
    <view class="detail-sheet" v-if="detailVisible">
      <view class="detail-handle"></view>
      <view class="detail-head">
        <text class="detail-title">识别详情</text>
        <text class="detail-close" @tap="closeDetail">关闭</text>
      </view>
      <scroll-view class="detail-scroll" scroll-y>
        <view class="detail-card" v-if="detailData">
          <image class="detail-image" :src="fullImageUrl(detailData.imagePath)" mode="aspectFill" />
          <view class="detail-summary">
            <view class="detail-row">
              <text class="detail-label">作物</text>
              <text class="detail-value">{{ detailData.cropInfo && detailData.cropInfo.cropName || '未知' }}</text>
            </view>
            <view class="detail-row">
              <text class="detail-label">病害</text>
              <text class="detail-value highlight">{{ detailData.diseaseInfo && detailData.diseaseInfo.diseaseName || '未知' }}</text>
            </view>
            <view class="detail-row">
              <text class="detail-label">严重程度</text>
              <text class="detail-value">{{ normalizeSeverity(detailData.diseaseInfo && detailData.diseaseInfo.severityLevel) }}</text>
            </view>
            <view class="detail-row">
              <text class="detail-label">置信度</text>
              <text class="detail-value">{{ formatDisplayConfidence(detailData.diseaseInfo && detailData.diseaseInfo.confidence) }}</text>
            </view>
          </view>
          <view class="detail-block" v-if="detailData.solution && detailData.solution.symptoms">
            <text class="detail-block-title">症状特征</text>
            <text class="detail-block-text">{{ detailData.solution.symptoms }}</text>
          </view>
          <view class="detail-block" v-if="detailData.solution && detailData.solution.solutions">
            <text class="detail-block-title">防治建议</text>
            <text class="detail-block-text">{{ detailData.solution.solutions }}</text>
          </view>
          <view class="detail-block" v-if="detailData.solution && detailData.solution.preventionMethods">
            <text class="detail-block-title">预防措施</text>
            <text class="detail-block-text">{{ detailData.solution.preventionMethods }}</text>
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
      userInfo: null,
      selectedImage: '',
      submitting: false,
      historyLoading: false,
      recentRecords: [],
      resultData: {},
      detailVisible: false,
      detailData: null,
      severityBadgeClass: ''
    }
  },
  computed: {
    userInitial() {
      if (!this.userInfo || !this.userInfo.username) return '农'
      return String(this.userInfo.username).slice(0, 1)
    }
  },
  onShow() {
    this.loadUserInfo()
    this.refreshHistory()
  },
  methods: {
    loadUserInfo() {
      const userInfo = uni.getStorageSync('userInfo')
      this.userInfo = userInfo && userInfo.userId ? userInfo : null
    },
    handleAuthAction() {
      if (this.userInfo) {
        uni.showModal({
          title: '提示',
          content: '确定退出当前账号吗？',
          success: ({ confirm }) => {
            if (!confirm) return
            uni.removeStorageSync('userInfo')
            this.userInfo = null
            this.resultData = null
            this.severityBadgeClass = ''
            this.recentRecords = []
            uni.showToast({ title: '已退出', icon: 'none' })
          }
        })
        return
      }
      uni.navigateTo({ url: '/pages/login/login' })
    },
    chooseImage() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: ({ tempFilePaths }) => {
          if (!tempFilePaths || !tempFilePaths.length) return
          this.selectedImage = tempFilePaths[0]
        }
      })
    },
    async handleRecognize() {
      if (!this.selectedImage) {
        this.toast('请先选择图片')
        return
      }

      if (this.submitting) return
      this.submitting = true

      try {
        const uploadRes = await this.uploadImage()
        const payload = typeof uploadRes.data === 'string' ? JSON.parse(uploadRes.data) : uploadRes.data
        if (!payload || !payload.success) {
          throw new Error((payload && payload.message) || '识别失败')
        }
        this.resultData = payload.data
        this.severityBadgeClass = this.severityClass(payload.data.diseaseInfo && payload.data.diseaseInfo.severityLevel)
        uni.showToast({ title: '识别成功', icon: 'success' })
        this.loadDiseaseDetail(payload.data.diseaseInfo && payload.data.diseaseInfo.diseaseName)
        this.refreshHistory()
      } catch (error) {
        console.error('recognize error:', error)
        this.toast(error.message || '识别失败，请稍后重试')
      } finally {
        this.submitting = false
      }
    },
    uploadImage() {
      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: config.baseUrl + '/api/predict',
          filePath: this.selectedImage,
          name: 'file',
          formData: this.userInfo ? { user_id: this.userInfo.userId } : {},
          success: resolve,
          fail: reject
        })
      })
    },
    async loadDiseaseDetail(diseaseName) {
      if (!diseaseName || diseaseName === '未知' || diseaseName === '健康') {
        this.resultData.solution = null
        return
      }

      try {
        const response = await uni.request({
          url: config.baseUrl + '/api/diseases',
          method: 'GET'
        })
        const { statusCode, data } = response
        if (statusCode === 200 && data && data.success && data.diseases) {
          const disease = data.diseases.find(d => d.name === diseaseName)
          if (disease) {
            this.resultData.solution = {
              symptoms: disease.description || disease.symptoms || '',
              solutions: disease.solutions || '',
              preventionMethods: disease.preventionMethods || ''
            }
          } else {
            this.resultData.solution = null
          }
        }
      } catch (error) {
        console.error('load disease detail error:', error)
        this.resultData.solution = null
      }
    },
    async refreshHistory() {
      if (!this.userInfo || !this.userInfo.userId) {
        this.recentRecords = []
        return
      }

      this.historyLoading = true
      try {
        const response = await uni.request({
          url: config.baseUrl + '/api/history',
          method: 'GET',
          data: {
            user_id: this.userInfo.userId,
            page: 1,
            page_size: 5
          }
        })
        const { statusCode, data } = response
        if (statusCode === 200 && data && data.success) {
          this.recentRecords = data.records || []
          return
        }
        this.recentRecords = []
      } catch (error) {
        console.error('history error:', error)
        this.recentRecords = []
      } finally {
        this.historyLoading = false
      }
    },
    async openRecordDetail(item) {
      try {
        const response = await uni.request({
          url: config.baseUrl + '/api/record/detail',
          method: 'GET',
          data: { record_id: item.recordId }
        })
        const { statusCode, data } = response
        if (statusCode === 200 && data && data.success) {
          this.detailData = data.data
          this.detailVisible = true
          return
        }
      } catch (error) {
        console.error('detail error:', error)
      }
    },
    closeDetail() {
      this.detailVisible = false
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
    formatDisplayConfidence(value) {
      if (value === undefined || value === null || value === '') return '--'
      const num = Number(value)
      if (Number.isNaN(num)) return '--'
      return `${num.toFixed(2)}%`
    },
    formatHistoryConfidence(value) {
      if (value === undefined || value === null || value === '') return '--'
      const num = Number(value)
      if (Number.isNaN(num)) return '--'
      const percent = num <= 1 ? num * 100 : num
      return `置信度 ${percent.toFixed(1)}%`
    },
    fullImageUrl(path) {
      if (!path) return '/static/ui/empty/empty-upload.png'
      if (/^https?:\/\//.test(path)) return path
      if (path.startsWith('/')) return config.baseUrl + path
      return `${config.baseUrl}/${path}`
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

.index-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #edf7ed 0%, #f7fbf6 40%, #f4faf4 100%);
}

.hero-section {
  position: relative;
  height: 420rpx;
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
  background: linear-gradient(180deg, rgba(47, 139, 72, 0.22) 0%, rgba(73, 183, 95, 0.34) 48%, rgba(101, 204, 126, 0.62) 100%);
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
  left: -50rpx;
  top: 90rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.28) 0%, rgba(255, 255, 255, 0.08) 58%, rgba(255, 255, 255, 0) 100%);
}

.hero-blob-right {
  width: 220rpx;
  height: 220rpx;
  right: -40rpx;
  top: 70rpx;
  background: radial-gradient(circle, rgba(214, 255, 222, 0.28) 0%, rgba(214, 255, 222, 0.08) 60%, rgba(214, 255, 222, 0) 100%);
}

.hero-decor {
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
  color:#F5AB58;
  margin-top: 18rpx;
  width: 560rpx;
  max-width: 100%;
  font-size: 28rpx;
  font-weight: bold;
  line-height: 1.6;
}

.content-wrap {
  position: relative;
  z-index: 5;
  margin-top: -74rpx;
  padding: 0 24rpx 42rpx;
}

.card {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 32rpx;
  box-shadow: 0 20rpx 54rpx rgba(31, 101, 46, 0.10);
  border: 2rpx solid rgba(255, 255, 255, 0.7);
}

.welcome-card {
  padding: 26rpx 28rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.welcome-left {
  display: flex;
  align-items: center;
  min-width: 0;
}

.avatar-badge {
  width: 94rpx;
  height: 94rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #2ea14d 0%, #48bf63 100%);
  color: #ffffff;
  font-size: 40rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 26rpx rgba(57, 169, 75, 0.24);
}

.welcome-meta {
  margin-left: 20rpx;
  min-width: 0;
}

.welcome-title {
  display: block;
  font-size: 38rpx;
  font-weight: 700;
  color: #243126;
  line-height: 1.3;
}

.welcome-tags {
  margin-top: 10rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.welcome-tag {
  padding: 6rpx 18rpx;
  border-radius: 999rpx;
  background: #edf8ef;
  color: #39a94b;
  font-size: 22rpx;
  font-weight: 600;
}

.welcome-action {
  min-width: 94rpx;
  height: 54rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: #fff2f2;
  color: #e16a6a;
  font-size: 26rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-card {
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

.upload-box {
  margin-top: 24rpx;
  position: relative;
  height: 360rpx;
  border-radius: 28rpx;
  border: 2rpx dashed #cfe3d0;
  background: linear-gradient(180deg, #f8fcf8 0%, #f3faf3 100%);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-empty {
  width: 210rpx;
  height: 160rpx;
  opacity: 0.95;
}

.upload-title {
  margin-top: 16rpx;
  font-size: 40rpx;
  font-weight: 700;
  color: #445448;
}

.upload-desc {
  margin-top: 12rpx;
  width: 520rpx;
  max-width: 100%;
  font-size: 24rpx;
  line-height: 1.7;
  color: #8c9b8f;
  text-align: center;
}

.upload-preview,
.upload-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.upload-mask {
  background: linear-gradient(180deg, rgba(36, 49, 38, 0.05) 0%, rgba(36, 49, 38, 0.22) 100%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 28rpx;
}

.upload-mask-btn {
  min-width: 176rpx;
  height: 58rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.9);
  color: #2e7d32;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.primary-btn {
  margin-top: 24rpx;
  width: 100%;
  height: 94rpx;
  line-height: 94rpx;
  border-radius: 999rpx;
  border: none;
  background: linear-gradient(90deg, #31b35d 0%, #2ea14d 52%, #42bb65 100%);
  box-shadow: 0 16rpx 32rpx rgba(57, 169, 75, 0.24);
}

.primary-btn::after {
  border: none;
}

.primary-btn-text {
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
}

.result-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(245,250,245,0.97) 100%);
}

.severity-badge {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #5d6e60;
  background: #eef3ef;
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

.result-summary {
  margin-top: 22rpx;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.summary-item {
  padding: 22rpx 20rpx;
  border-radius: 24rpx;
  background: #f7faf7;
  border: 2rpx solid #edf2ed;
}

.summary-item:last-child {
  grid-column: 1 / -1;
}

.summary-label {
  display: block;
  font-size: 22rpx;
  color: #8da08f;
}

.summary-value {
  display: block;
  margin-top: 10rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #243126;
  line-height: 1.4;
}

.summary-value.highlight {
  color: #2e7d32;
}

.result-panel {
  margin-top: 20rpx;
}

.result-block {
  margin-top: 18rpx;
  padding: 24rpx;
  border-radius: 24rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
}

.result-block-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #243126;
}

.result-block-text {
  display: block;
  margin-top: 12rpx;
  font-size: 25rpx;
  line-height: 1.8;
  color: #5f6f63;
}

.loading-box,
.empty-box {
  padding: 34rpx 12rpx 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.small-empty {
  padding-top: 22rpx;
}

.loading-text,
.empty-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #516154;
}

.empty-image {
  width: 220rpx;
  height: 150rpx;
  opacity: 0.96;
}

.empty-title {
  margin-top: 14rpx;
}

.empty-desc {
  margin-top: 10rpx;
  width: 500rpx;
  max-width: 100%;
  font-size: 24rpx;
  line-height: 1.7;
  color: #90a090;
  text-align: center;
}

.record-list {
  margin-top: 12rpx;
}

.record-item {
  display: flex;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 2rpx solid #eff4ef;
}

.record-item:last-child {
  border-bottom: none;
}

.record-thumb {
  width: 128rpx;
  height: 128rpx;
  border-radius: 22rpx;
  background: #f1f6f1;
  flex-shrink: 0;
}

.record-body {
  flex: 1;
  min-width: 0;
  margin-left: 18rpx;
}

.record-top {
  display: flex;
  flex-direction: column;
}

.record-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #243126;
  line-height: 1.5;
}

.record-time {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #95a595;
}

.record-meta-row {
  margin-top: 12rpx;
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.record-chip {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #edf8ef;
  color: #2e7d32;
  font-size: 22rpx;
  font-weight: 600;
}

.record-chip.soft {
  background: #f2f5f2;
  color: #708072;
}

.detail-mask {
  position: fixed;
  inset: 0;
  background: rgba(22, 32, 24, 0.32);
  z-index: 30;
}

.detail-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 31;
  height: 78vh;
  background: #ffffff;
  border-top-left-radius: 34rpx;
  border-top-right-radius: 34rpx;
  box-shadow: 0 -16rpx 48rpx rgba(31, 101, 46, 0.12);
  overflow: hidden;
}

.detail-handle {
  width: 92rpx;
  height: 8rpx;
  border-radius: 999rpx;
  background: #dbe6dc;
  margin: 18rpx auto 0;
}

.detail-head {
  padding: 22rpx 28rpx 18rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.detail-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #243126;
}

.detail-close {
  font-size: 24rpx;
  color: #39a94b;
  font-weight: 600;
}

.detail-scroll {
  height: calc(78vh - 90rpx);
}

.detail-card {
  padding: 0 28rpx 40rpx;
}

.detail-image {
  width: 100%;
  height: 320rpx;
  border-radius: 28rpx;
  background: #f1f6f1;
}

.detail-summary {
  margin-top: 20rpx;
  padding: 20rpx 22rpx;
  border-radius: 24rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
}

.detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 0;
  gap: 18rpx;
}

.detail-label {
  font-size: 24rpx;
  color: #8ca08e;
}

.detail-value {
  flex: 1;
  text-align: right;
  font-size: 28rpx;
  font-weight: 700;
  color: #243126;
}

.detail-value.highlight {
  color: #2e7d32;
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
