<template>
  <view class="login-page">
    <view class="hero-section">
      <image class="hero-bg" src="static/ui/backgrounds/bg-login-hero.png" mode="aspectFill" />
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
        <view class="hero-title">慧农之眼</view>
        <view class="hero-subtitle">病虫害智能识别与预警系统</view>
        <view class="hero-desc">上传叶片图像，快速识别病害并获取科学防治建议</view>
      </view>
    </view>

    <view class="card-wrap">
      <view class="auth-card">
        <view class="tab-bar">
          <view class="tab-item" :class="{ active: isLogin }" @tap="switchMode(true)">
            <text class="tab-text">登录</text>
            <view class="tab-line"></view>
          </view>
          <view class="tab-item" :class="{ active: !isLogin }" @tap="switchMode(false)">
            <text class="tab-text">注册</text>
            <view class="tab-line"></view>
          </view>
        </view>

        <view class="form-area">
          <view class="field-group">
            <text class="field-label">用户名</text>
            <view class="field-box">
              <view class="field-icon field-icon-user"></view>
              <input
                class="field-input"
                v-model.trim="formData.username"
                placeholder="请输入用户名"
                placeholder-class="field-placeholder"
                confirm-type="next"
              />
              <image class="field-watermark" src="D:/1_code_study/projects/2026jsjds/农业识别/小程序/static/ui/decor/leaf-watermark.png" mode="aspectFit" />
            </view>
          </view>

          <view class="field-group">
            <text class="field-label">密码</text>
            <view class="field-box">
              <view class="field-icon field-icon-lock"></view>
              <input
                class="field-input"
                v-model.trim="formData.password"
                :password="!showPassword"
                placeholder="请输入密码"
                placeholder-class="field-placeholder"
                confirm-type="done"
              />
              <text class="field-action" @tap="togglePassword">{{ showPassword ? '隐藏' : '显示' }}</text>
            </view>
          </view>

          <template v-if="!isLogin">
            <view class="field-group">
              <text class="field-label">确认密码</text>
              <view class="field-box">
                <view class="field-icon field-icon-check"></view>
                <input
                  class="field-input"
                  v-model.trim="formData.confirmPassword"
                  :password="!showConfirmPassword"
                  placeholder="请再次输入密码"
                  placeholder-class="field-placeholder"
                />
                <text class="field-action" @tap="toggleConfirmPassword">{{ showConfirmPassword ? '隐藏' : '显示' }}</text>
              </view>
            </view>

            <view class="field-group">
              <text class="field-label">邮箱</text>
              <view class="field-box">
                <view class="field-icon field-icon-mail"></view>
                <input
                  class="field-input"
                  v-model.trim="formData.email"
                  placeholder="请输入邮箱（选填）"
                  placeholder-class="field-placeholder"
                />
              </view>
            </view>

            <view class="field-group">
              <text class="field-label">手机号</text>
              <view class="field-box">
                <view class="field-icon field-icon-phone"></view>
                <input
                  class="field-input"
                  v-model.trim="formData.phone"
                  type="number"
                  placeholder="请输入手机号（选填）"
                  placeholder-class="field-placeholder"
                />
              </view>
            </view>
          </template>

          <view class="submit-area">
            <button class="submit-btn" :loading="submitting" :disabled="submitting" @tap="handleSubmit">
              <text class="submit-btn-text">{{ submitting ? (isLogin ? '登录中...' : '注册中...') : (isLogin ? '登 录' : '注 册') }}</text>
            </button>
          </view>
        </view>
      </view>

      <view class="agreement-text">
        {{ isLogin ? '登录' : '注册' }}即代表同意
        <text class="agreement-link">《用户协议》</text>
        和
        <text class="agreement-link">《隐私政策》</text>
      </view>
    </view>

    <view class="page-glow page-glow-left"></view>
    <view class="page-glow page-glow-right"></view>
  </view>
</template>

<script>
import config from '@/config.js'

const createFormData = (username = '') => ({
  username,
  password: '',
  confirmPassword: '',
  email: '',
  phone: ''
})

export default {
  data() {
    return {
      isLogin: true,
      submitting: false,
      showPassword: false,
      showConfirmPassword: false,
      formData: createFormData()
    }
  },
  methods: {
    switchMode(isLogin) {
      if (this.isLogin === isLogin) return
      this.isLogin = isLogin
      this.showPassword = false
      this.showConfirmPassword = false
      this.formData = createFormData(this.formData.username)
    },
    togglePassword() {
      this.showPassword = !this.showPassword
    },
    toggleConfirmPassword() {
      this.showConfirmPassword = !this.showConfirmPassword
    },
    validateForm() {
      const { username, password, confirmPassword, email, phone } = this.formData

      if (!username) {
        this.toast('请输入用户名')
        return false
      }

      if (username.length < 2) {
        this.toast('用户名至少 2 个字符')
        return false
      }

      if (!password) {
        this.toast('请输入密码')
        return false
      }

      if (password.length < 6) {
        this.toast('密码至少 6 位')
        return false
      }

      if (!this.isLogin) {
        if (!confirmPassword) {
          this.toast('请再次输入密码')
          return false
        }

        if (password !== confirmPassword) {
          this.toast('两次输入的密码不一致')
          return false
        }

        if (email && !/^\S+@\S+\.\S+$/.test(email)) {
          this.toast('请输入正确的邮箱地址')
          return false
        }

        if (phone && !/^1\d{10}$/.test(phone)) {
          this.toast('请输入正确的手机号')
          return false
        }
      }

      return true
    },
    toast(title) {
      uni.showToast({
        title,
        icon: 'none'
      })
    },
    async handleSubmit() {
      if (this.submitting || !this.validateForm()) return

      this.submitting = true

      try {
        const url = this.isLogin ? '/api/login' : '/api/register'
        const payload = this.isLogin
          ? {
              username: this.formData.username,
              password: this.formData.password
            }
          : {
              username: this.formData.username,
              password: this.formData.password,
              email: this.formData.email,
              phone: this.formData.phone
            }

        const response = await uni.request({
          url: config.baseUrl + url,
          method: 'POST',
          data: payload,
          header: {
            'Content-Type': 'application/json'
          }
        })

        const { statusCode, data } = response

        if (statusCode === 401) {
          this.toast('用户名或密码错误')
          return
        }

        if (statusCode === 200 && data && data.success) {
          if (this.isLogin) {
            uni.setStorageSync('userInfo', data.userInfo)
            uni.showToast({
              title: '登录成功',
              icon: 'success'
            })
            setTimeout(() => {
              uni.reLaunch({
                url: '/pages/index/index'
              })
            }, 1000)
          } else {
            const username = this.formData.username
            uni.showToast({
              title: '注册成功，请登录',
              icon: 'success'
            })
            this.isLogin = true
            this.showPassword = false
            this.showConfirmPassword = false
            this.formData = createFormData(username)
          }
          return
        }

        this.toast((data && data.message) || '操作失败，请稍后重试')
      } catch (error) {
        console.error('auth request error:', error)
        this.toast('网络错误，请稍后重试')
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style>
page {
  min-height: 100%;
  background: linear-gradient(180deg, #eef7ee 0%, #f7fbf6 38%, #f4faf4 100%);
}

.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #eef7ee 0%, #f7fbf6 38%, #f4faf4 100%);
}

.hero-section {
  position: relative;
  height: 520rpx;
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
  background: linear-gradient(180deg, rgba(47, 139, 72, 0.20) 0%, rgba(73, 183, 95, 0.34) 42%, rgba(103, 202, 123, 0.64) 100%);
}

.hero-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(8rpx);
  z-index: 2;
  pointer-events: none;
}

.hero-blob-left {
  width: 220rpx;
  height: 220rpx;
  left: -60rpx;
  top: 130rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.34) 0%, rgba(255, 255, 255, 0.08) 58%, rgba(255, 255, 255, 0) 100%);
}

.hero-blob-right {
  width: 280rpx;
  height: 280rpx;
  right: -70rpx;
  top: 96rpx;
  background: radial-gradient(circle, rgba(193, 255, 206, 0.34) 0%, rgba(193, 255, 206, 0.10) 56%, rgba(193, 255, 206, 0) 100%);
}

.hero-content {
  position: relative;
  z-index: 3;
  padding: 78rpx 56rpx 0;
  color: #ffffff;
}

.brand-chip {
  height: 60rpx;
  padding: 0 22rpx 0 12rpx;
  display: inline-flex;
  align-items: center;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 10rpx 24rpx rgba(34, 91, 45, 0.10);
}

.brand-chip-icon {
  width: 34rpx;
  height: 34rpx;
  margin-right: 10rpx;
}

.brand-chip-text {
  font-size: 24rpx;
  letter-spacing: 1rpx;
}

.hero-title {
  color:#DD5710;
  margin-top: 34rpx;
  font-size: 68rpx;
  line-height: 1.08;
  font-weight: 700;
  letter-spacing: 2rpx;
  text-shadow: 0 8rpx 20rpx rgba(29, 85, 40, 0.16);
}

.hero-subtitle {
  color:#F5AB58;
  margin-top: 18rpx;
  font-size: 34rpx;
  line-height: 1.4;
  font-weight: 600;
  opacity: 0.98;
}

.hero-desc {
  color:#F5AB58;
  margin-top: 16rpx;
  width: 580rpx;
  max-width: 100%;
  font-size: 26rpx;
  font-weight: bold;
  line-height: 1.7;
}

.hero-decor {
  position: absolute;
  z-index: 2;
  pointer-events: none;
}

.hero-decor-tl {
  width: 520rpx;
  height: 520rpx;
  left: -6rpx;
  top: -6rpx;
  opacity: 0.85;
}

.hero-decor-br {
  width: 520rpx;
  height: 520rpx;
  right: -18rpx;
  bottom: -18rpx;
  opacity: 0.55;
}

.card-wrap {
  position: relative;
  z-index: 5;
  margin-top: -96rpx;
  padding: 0 32rpx 44rpx;
}

.auth-card {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 34rpx;
  padding: 28rpx 28rpx 34rpx;
  box-shadow: 0 22rpx 60rpx rgba(31, 101, 46, 0.12);
  border: 2rpx solid rgba(255, 255, 255, 0.65);
}

.tab-bar {
  display: flex;
  gap: 10rpx;
  padding: 10rpx;
  border-radius: 24rpx;
  background: #f1f6f1;
}

.tab-item {
  flex: 1;
  height: 86rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.tab-text {
  font-size: 32rpx;
  color: #8c9b8f;
  font-weight: 600;
}

.tab-line {
  position: absolute;
  bottom: 12rpx;
  width: 52rpx;
  height: 6rpx;
  border-radius: 999rpx;
  background: transparent;
}

.tab-item.active {
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 10rpx 22rpx rgba(57, 169, 75, 0.12);
}

.tab-item.active .tab-text {
  color: #2e7d32;
}

.tab-item.active .tab-line {
  background: linear-gradient(90deg, #2e7d32 0%, #49b75f 100%);
}

.form-area {
  margin-top: 26rpx;
}

.field-group {
  margin-top: 24rpx;
}

.field-label {
  display: block;
  margin-bottom: 14rpx;
  padding-left: 10rpx;
  color: #314434;
  font-size: 28rpx;
  font-weight: 600;
}

.field-box {
  position: relative;
  min-height: 96rpx;
  display: flex;
  align-items: center;
  border-radius: 24rpx;
  background: #f7faf7;
  border: 2rpx solid #e2ede3;
  box-shadow: inset 0 1rpx 0 rgba(255, 255, 255, 0.88);
}

.field-box:focus-within {
  background: #ffffff;
  border-color: rgba(57, 169, 75, 0.7);
  box-shadow: 0 0 0 8rpx rgba(57, 169, 75, 0.08);
}

.field-icon {
  width: 34rpx;
  height: 34rpx;
  margin-left: 26rpx;
  margin-right: 20rpx;
  position: relative;
  flex-shrink: 0;
}

.field-icon::before,
.field-icon::after {
  content: '';
  position: absolute;
  box-sizing: border-box;
}

.field-icon-user::before {
  width: 18rpx;
  height: 18rpx;
  border: 3rpx solid #39a94b;
  border-radius: 50%;
  left: 8rpx;
  top: 1rpx;
}

.field-icon-user::after {
  width: 28rpx;
  height: 16rpx;
  border: 3rpx solid #39a94b;
  border-top: none;
  border-radius: 0 0 14rpx 14rpx;
  left: 3rpx;
  bottom: 0;
}

.field-icon-lock::before {
  width: 18rpx;
  height: 16rpx;
  border: 3rpx solid #39a94b;
  border-radius: 6rpx;
  left: 8rpx;
  bottom: 3rpx;
}

.field-icon-lock::after {
  width: 14rpx;
  height: 12rpx;
  border: 3rpx solid #39a94b;
  border-bottom: none;
  border-radius: 12rpx 12rpx 0 0;
  left: 10rpx;
  top: 1rpx;
}

.field-icon-check::before {
  width: 24rpx;
  height: 24rpx;
  border: 3rpx solid #39a94b;
  border-radius: 50%;
  left: 4rpx;
  top: 4rpx;
}

.field-icon-check::after {
  width: 12rpx;
  height: 7rpx;
  border-left: 3rpx solid #39a94b;
  border-bottom: 3rpx solid #39a94b;
  transform: rotate(-45deg);
  left: 11rpx;
  top: 11rpx;
}

.field-icon-mail::before {
  width: 28rpx;
  height: 20rpx;
  border: 3rpx solid #39a94b;
  border-radius: 6rpx;
  left: 3rpx;
  top: 6rpx;
}

.field-icon-mail::after {
  width: 18rpx;
  height: 18rpx;
  border-left: 3rpx solid #39a94b;
  border-bottom: 3rpx solid #39a94b;
  transform: rotate(-45deg);
  left: 8rpx;
  top: 4rpx;
}

.field-icon-phone::before {
  width: 18rpx;
  height: 28rpx;
  border: 3rpx solid #39a94b;
  border-radius: 7rpx;
  left: 8rpx;
  top: 2rpx;
}

.field-icon-phone::after {
  width: 6rpx;
  height: 6rpx;
  background: #39a94b;
  border-radius: 50%;
  left: 14rpx;
  bottom: 5rpx;
}

.field-input {
  flex: 1;
  height: 96rpx;
  font-size: 30rpx;
  color: #243126;
  padding-right: 22rpx;
}

.field-placeholder {
  color: #a4b2a6;
}

.field-watermark {
  width: 40rpx;
  height: 40rpx;
  margin-right: 24rpx;
  opacity: 0.42;
  flex-shrink: 0;
}

.field-action {
  padding: 0 24rpx 0 8rpx;
  font-size: 24rpx;
  color: #39a94b;
  font-weight: 600;
  flex-shrink: 0;
}

.submit-area {
  margin-top: 36rpx;
}

.submit-btn {
  width: 100%;
  height: 96rpx;
  line-height: 96rpx;
  border-radius: 999rpx;
  border: none;
  overflow: hidden;
  background: linear-gradient(90deg, #31b35d 0%, #2ea14d 52%, #42bb65 100%);
  box-shadow: 0 16rpx 32rpx rgba(57, 169, 75, 0.26);
}

.submit-btn::after {
  border: none;
}

.submit-btn:active {
  transform: scale(0.985);
  opacity: 0.98;
}

.submit-btn-text {
  color: #ffffff;
  font-size: 34rpx;
  letter-spacing: 8rpx;
  font-weight: 700;
}

.agreement-text {
  margin-top: 28rpx;
  text-align: center;
  font-size: 24rpx;
  color: #8da08f;
  line-height: 1.8;
}

.agreement-link {
  color: #39a94b;
  font-weight: 600;
}

.page-glow {
  position: absolute;
  width: 300rpx;
  height: 300rpx;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(12rpx);
  opacity: 0.24;
}

.page-glow-left {
  left: -96rpx;
  bottom: 260rpx;
  background: radial-gradient(circle, rgba(95, 210, 122, 0.28) 0%, rgba(95, 210, 122, 0.12) 46%, rgba(95, 210, 122, 0) 100%);
}

.page-glow-right {
  right: -90rpx;
  bottom: 96rpx;
  background: radial-gradient(circle, rgba(95, 210, 122, 0.28) 0%, rgba(95, 210, 122, 0.10) 46%, rgba(95, 210, 122, 0) 100%);
}
</style>
