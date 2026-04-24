<template>
  <view class="login-container">
    <view class="content">
      <!-- 顶部标题区域 -->
      <view class="header">
        <view class="title">智慧农业</view>
        <view class="subtitle">病虫害智能识别与预警系统</view>
      </view>
      
      <!-- 登录/注册切换卡片 -->
      <view class="card">
        <!-- 切换按钮 -->
        <view class="switch-mode">
          <view 
            :class="['mode-btn', isLogin ? 'active' : '']" 
            @tap="switchMode(true)"
          >登录</view>
          <view 
            :class="['mode-btn', !isLogin ? 'active' : '']" 
            @tap="switchMode(false)"
          >注册</view>
        </view>
        
        <!-- 表单区域 -->
        <view class="form-section">
          <view class="input-group">
            <text class="label">账号</text>
            <input 
              class="input" 
              v-model="formData.username" 
              placeholder="请输入用户名" 
            />
          </view>
          
          <view class="input-group">
            <text class="label">密码</text>
            <input 
              class="input" 
              v-model="formData.password" 
              type="password" 
              placeholder="请输入密码" 
            />
          </view>
          
          <!-- 注册时显示的额外字段 -->
          <template v-if="!isLogin">
            <view class="input-group">
              <text class="label">确认密码</text>
              <input 
                class="input" 
                v-model="formData.confirmPassword" 
                type="password" 
                placeholder="请再次输入密码" 
              />
            </view>
            
            <view class="input-group">
              <text class="label">邮箱</text>
              <input 
                class="input" 
                v-model="formData.email" 
                type="text" 
                placeholder="请输入邮箱" 
              />
            </view>
            
            <view class="input-group">
              <text class="label">手机号</text>
              <input 
                class="input" 
                v-model="formData.phone" 
                type="number" 
                placeholder="请输入手机号" 
              />
            </view>
          </template>
        </view>
        
        <!-- 提交按钮 -->
        <button class="submit-btn" @tap="handleSubmit">
          {{ isLogin ? '登 录' : '注 册' }}
        </button>
      </view>
      
      <!-- 底部文字 - 移到content内 -->
      <view class="footer-text">
        登录即代表同意《用户协议》和《隐私政策》
      </view>
    </view>
  </view>
</template>

<script>
import config from '@/config.js'

export default {
  data() {
    return {
      isLogin: true,
      formData: {
        username: '',
        password: '',
        confirmPassword: '',
        email: '',
        phone: ''
      }
    }
  },
  methods: {
    // 切换登录/注册模式
    switchMode(isLogin) {
      this.isLogin = isLogin
      this.formData = {
        username: '',
        password: '',
        confirmPassword: '',
        email: '',
        phone: ''
      }
    },
    
    // 表单验证
    validateForm() {
      if (!this.formData.username || !this.formData.password) {
        uni.showToast({
          title: '请填写用户名和密码',
          icon: 'none'
        })
        return false
      }
      
      if (!this.isLogin) {
        if (this.formData.password !== this.formData.confirmPassword) {
          uni.showToast({
            title: '两次输入的密码不一致',
            icon: 'none'
          })
          return false
        }
      }
      
      return true
    },
    
    // 处理提交
    async handleSubmit() {
      if (!this.validateForm()) return
      
      try {
        const url = this.isLogin ? '/api/login' : '/api/register'
        const response = await uni.request({
          url: config.baseUrl + url,
          method: 'POST',
          data: this.formData,
          header: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.statusCode === 200 && response.data.success) {
          if (this.isLogin) {
            uni.setStorageSync('userInfo', response.data.userInfo)
          }
          
          uni.showToast({
            title: this.isLogin ? '登录成功' : '注册成功',
            icon: 'success'
          })
          
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/index/index'
            })
          }, 1500)
        } else {
          uni.showToast({
            title: response.data.message || '操作失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('请求错误:', error)
        uni.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        })
      }
    }
  }
}
</script>

<style>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #d9eaf3 0%, #edf6f0 34%, #e8f2e8 100%);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.content {
  flex: 1;
  padding: 120rpx 34rpx 50rpx;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 100%;
  z-index: 2;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -180rpx;
  right: -140rpx;
  width: 560rpx;
  height: 560rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(105, 191, 109, 0.48), rgba(105, 191, 109, 0.06) 70%);
}

.login-container::after {
  content: '';
  position: absolute;
  bottom: -220rpx;
  left: -100rpx;
  width: 680rpx;
  height: 380rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(118, 193, 95, 0.33), rgba(118, 193, 95, 0.08));
}

.header {
  margin-bottom: 56rpx;
  color: #185d2a;
  text-align: left;
}

.title {
  font-size: 72rpx;
  font-weight: bold;
  margin-bottom: 14rpx;
  letter-spacing: 2rpx;
}

.subtitle {
  font-size: 40rpx;
  opacity: 0.95;
  letter-spacing: 1rpx;
}

.subtitle::before {
  content: '';
  display: inline-block;
  width: 14rpx;
  height: 14rpx;
  margin-right: 12rpx;
  border-radius: 50%;
  background: #2fa142;
}

.card {
  background: rgba(255,255,255,0.88);
  border-radius: 36rpx;
  padding: 46rpx 34rpx;
  box-shadow: 0 16rpx 40rpx rgba(41,91,45,0.12);
  border: 2rpx solid rgba(255,255,255,0.72);
  backdrop-filter: blur(10rpx);
}

.switch-mode {
  display: flex;
  margin-bottom: 48rpx;
  border-radius: 16rpx;
  background: #f4f7f4;
  padding: 8rpx;
  border-bottom: 2rpx solid #ecf1ec;
}

.mode-btn {
  flex: 1;
  text-align: center;
  padding: 18rpx 0;
  font-size: 32rpx;
  color: #8a8f8b;
  border-radius: 12rpx;
  font-weight: 600;
}

.mode-btn.active {
  background: transparent;
  color: #2f9e42;
  box-shadow: none;
  position: relative;
}

.mode-btn.active::after {
  content: '';
  position: absolute;
  left: 22%;
  right: 22%;
  bottom: -8rpx;
  height: 6rpx;
  border-radius: 99rpx;
  background: #37a949;
}

.input-group {
  margin-bottom: 30rpx;
}

.label {
  display: block;
  font-size: 25rpx;
  color: #8b958e;
  margin-bottom: 12rpx;
  margin-left: 16rpx;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 94rpx;
  background: #f7faf7;
  border-radius: 46rpx;
  padding: 0 34rpx;
  font-size: 30rpx;
  color: #4a544d;
  border: 2rpx solid #e5ece5;
  box-sizing: border-box;
}

.input:focus {
  background: #fff;
  border-color: #2C8A43;
  box-shadow: 0 4rpx 12rpx rgba(44,138,67,0.1);
}

.input::placeholder {
  color: #bbb;
}

.submit-btn {
  margin-top: 56rpx;
  width: 100%;
  height: 96rpx;
  line-height: 96rpx;
  background: linear-gradient(135deg, #2C8A43, #3CA55C);
  color: #fff;
  font-size: 34rpx;
  border-radius: 48rpx;
  text-align: center;
  box-shadow: 0 12rpx 24rpx rgba(44,138,67,0.26);
  border: none;
  font-weight: bold;
  letter-spacing: 2rpx;
}

.submit-btn:active {
  opacity: 0.9;
}

.footer-text {
  margin-top: 44rpx;
  text-align: center;
  font-size: 26rpx;
  color: #8b8f8d;
  padding-bottom: 40rpx;
}
</style> 
