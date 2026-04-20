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
  background: linear-gradient(160deg, #2C8A43 0%, #3CA55C 55%, #7BC96F 100%);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
  padding: 80rpx 40rpx 40rpx;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 100%;
}

.header {
  margin-bottom: 80rpx;
  color: #fff;
  text-align: center;
}

.title {
  font-size: 56rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  letter-spacing: 4rpx;
}

.subtitle {
  font-size: 32rpx;
  opacity: 0.9;
  letter-spacing: 2rpx;
}

.card {
  background: rgba(255,255,255,0.96);
  border-radius: 32rpx;
  padding: 50rpx 40rpx;
  box-shadow: 0 16rpx 50rpx rgba(0,0,0,0.12);
  backdrop-filter: blur(8rpx);
}

.switch-mode {
  display: flex;
  margin-bottom: 60rpx;
  border-radius: 18rpx;
  background: #eef4ef;
  padding: 8rpx;
}

.mode-btn {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  font-size: 32rpx;
  color: #666;
  border-radius: 12rpx;
  font-weight: 500;
}

.mode-btn.active {
  background: linear-gradient(135deg, #2C8A43, #3CA55C);
  color: #fff;
  box-shadow: 0 6rpx 16rpx rgba(44,138,67,0.35);
}

.input-group {
  margin-bottom: 40rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  margin-left: 20rpx;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 100rpx;
  background: #f6faf6;
  border-radius: 50rpx;
  padding: 0 40rpx;
  font-size: 30rpx;
  color: #333;
  border: 2rpx solid #e8efe8;
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
  margin-top: 80rpx;
  width: 100%;
  height: 100rpx;
  line-height: 100rpx;
  background: linear-gradient(135deg, #2C8A43, #3CA55C);
  color: #fff;
  font-size: 34rpx;
  border-radius: 50rpx;
  text-align: center;
  box-shadow: 0 12rpx 28rpx rgba(44,138,67,0.36);
  border: none;
  font-weight: bold;
  letter-spacing: 2rpx;
}

.submit-btn:active {
  opacity: 0.9;
}

.footer-text {
  margin-top: 40rpx;
  text-align: center;
  font-size: 26rpx;
  color: rgba(255,255,255,0.8);
  padding-bottom: 40rpx;
}
</style> 
