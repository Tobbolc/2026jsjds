<template>
	<view class="container">
	<view class="content">
			<!-- 主要功能区 -->
			<view class="main">
				<!-- 用户信息卡片 -->
				<view class="user-card">
					<view class="user-info">
						<text class="welcome">欢迎，{{userInfo.username}}</text>
						<text class="logout" @tap="handleLogout">退出登录</text>
					</view>
				</view>
				
				<!-- 识别功能卡片 -->
				<view class="function-card">
					<view class="card-title">病虫害识别</view>
					<view class="upload-section">
						<view class="upload-box" @tap="chooseImage">
							<image v-if="tempFilePath" :src="tempFilePath" mode="aspectFit" class="preview-image"></image>
							<view v-else class="upload-placeholder">
								<uni-icons type="camera-filled" size="40" color="#999"></uni-icons>
								<text class="upload-text">点击上传图片</text>
								<text class="upload-desc">支持jpg、png格式</text>
							</view>
						</view>
					</view>
					<button class="submit-btn" @tap="submitImage" :disabled="!tempFilePath">开始识别</button>
				</view>
				
				<!-- 最近识别卡片 -->
				<view class="history-card">
					<view class="card-title">最近识别</view>
					<scroll-view 
						scroll-y 
						class="history-list" 
						@scrolltolower="loadMore"
						:show-scrollbar="false"
						:style="{ height: '600rpx' }"
						:lower-threshold="50"
					>
						<view class="empty-tip" v-if="!historyList.length">暂无识别记录</view>
						<view v-else>
							<view 
								class="history-item" 
								v-for="(item, index) in historyList" 
								:key="index" 
								@tap="showHistoryDetail(item)"
							>
								<image :src="getImageUrl(item.imagePath)" mode="aspectFill" class="history-image"></image>
								<view class="history-info">
									<text class="disease-name">{{item.diseaseName}}</text>
									<text class="crop-name">作物：{{item.cropName}}</text>
									<text class="confidence">置信度: {{item.confidence}}%</text>
									<text class="time">{{item.createTime}}</text>
								</view>
							</view>
							<!-- 加载更多提示 -->
							<view class="loading-more" v-if="isLoading">
								<text>加载中...</text>
							</view>
							<view class="no-more" v-if="!hasMore && historyList.length">
								<text>没有更多了</text>
							</view>
						</view>
					</scroll-view>
				</view>
				
				<!-- 识别结果弹窗 -->
				<view class="popup-mask" v-if="showResultPopup" @tap="closePopup">
					<view class="popup-content" @tap.stop>
						<view class="popup-header">
							<text class="popup-title">识别结果</text>
							<text class="popup-close" @tap="closePopup">×</text>
						</view>
						
						<view class="popup-body" v-if="recognitionResult">
							<view class="result-item">
								<text class="label">作物类型：</text>
								<text class="value">{{recognitionResult.cropInfo.cropName}}</text>
							</view>
							
							<view class="result-item">
								<text class="label">识别结果：</text>
								<text :class="['value', getDiseaseClass(recognitionResult.diseaseInfo.severityLevel)]">
									{{recognitionResult.diseaseInfo.diseaseName}}
								</text>
							</view>
							
							<view class="result-item">
								<text class="label">置信度：</text>
								<text class="value">{{recognitionResult.diseaseInfo.confidence}}%</text>
							</view>
							
							<view class="result-item">
								<text class="label">严重程度：</text>
								<text :class="['value', getDiseaseClass(recognitionResult.diseaseInfo.severityLevel)]">
									{{recognitionResult.diseaseInfo.severityLevel}}
								</text>
							</view>
							
							<view class="divider"></view>
							
							<view class="solution-section">
								<text class="solution-section-subtitle">症状描述</text>
								<text class="solution-section-content">{{recognitionResult.solution.symptoms || '暂无数据'}}</text>
								
								<text class="solution-section-subtitle">解决方案</text>
								<text class="solution-section-content">{{recognitionResult.solution.solutions || '暂无数据'}}</text>
								
								<text class="solution-section-subtitle">预防措施</text>
								<text class="solution-section-content">{{recognitionResult.solution.preventionMethods || '暂无数据'}}</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import config from '@/config.js'

	export default {
		data() {
			return {
			userInfo: {},
			tempFilePath: '',
			recognitionResult: null,
			showResultPopup: false,
			historyList: [],
			currentPage: 1,
			hasMore: true,
			isLoading: false
			}
		},
		onLoad() {
		// 获取用户信息
		const userInfo = uni.getStorageSync('userInfo')
		if (!userInfo) {
			uni.redirectTo({
				url: '/pages/login/login'
			})
			return
		}
		this.userInfo = userInfo
		
		// 获取历史记录
		this.getHistoryList()
		},
		methods: {
		// 选择图片
		chooseImage() {
			uni.chooseImage({
				count: 1,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.tempFilePath = res.tempFilePaths[0]
				},
				fail: (err) => {
					uni.showToast({
						title: '选择图片失败',
						icon: 'none'
					})
				}
			})
		},
		
		// 提交图片进行识别
		submitImage() {
			if (!this.tempFilePath) return
			
			uni.showLoading({
				title: '识别中...'
			})
			
			uni.uploadFile({
				url: config.baseUrl + '/api/predict',
				filePath: this.tempFilePath,
				name: 'file',
				formData: {
					user_id: this.userInfo.userId
				},
				success: (res) => {
					const result = JSON.parse(res.data)
					if (result.success && result.data) {
						const data = result.data
						if (data.diseaseInfo && data.diseaseInfo.severityLevel) {
							this.recognitionResult = JSON.parse(JSON.stringify(data))
							this.showResultPopup = true
							
							// 刷新历史记录（重置到第一页）
							this.currentPage = 1
							this.hasMore = true
							this.getHistoryList(1)
							
							uni.showToast({
								title: '识别成功',
								icon: 'success'
							})
						} else {
							uni.showToast({
								title: '数据格式错误',
								icon: 'none'
							})
						}
					} else {
						uni.showToast({
							title: result.message || '识别失败',
							icon: 'none'
						})
					}
				},
				fail: (err) => {
					uni.showToast({
						title: '上传失败',
						icon: 'none'
					})
				},
				complete: () => {
					uni.hideLoading()
				}
			})
		},
		
		// 获取严重程度文本
		getSeverityText(level) {
			// 直接访问值而不是响应式对象
			const actualLevel = level && level.toString()
			
			const textMap = {
				'healthy': '健康',
				'general': '一般',
				'serious': '严重'
			}
			
			return textMap[actualLevel] || '未知'
		},
		
		// 获取病害状态的样式类
		getDiseaseClass(level) {
			if (!level) return ''
			
			const classMap = {
				'健康': 'status-healthy',
				'一般': 'status-warning',
				'严重': 'status-danger'
			}
			
			return classMap[level] || ''
		},
		
		// 添加关闭弹窗方法
		closePopup() {
			this.showResultPopup = false
		},
		
		// 获取历史记录
		getHistoryList(page = 1) {
			if (!this.hasMore && page > 1) {
				console.log('没有更多数据了')
				return
			}
			if (this.isLoading) {
				console.log('正在加载中...')
				return
			}
			
			console.log('开始加载第', page, '页数据')
			this.isLoading = true
			
			// 添加loading提示
			if (page > 1) {
				uni.showLoading({
					title: '加载中...'
				})
			}

			uni.request({
				url: config.baseUrl + '/api/history',
				method: 'GET',
				data: {
					user_id: this.userInfo.userId,
					page: page,
					page_size: 5
				},
				success: (res) => {
					console.log('获取数据成功:', res.data)
					if (res.data.success) {
						const newRecords = res.data.records.map(record => ({
							...record,
							confidence: Math.round(record.confidence * 100),
							imagePath: record.imagePath.trim(),
							createTime: record.createTime.replace('T', ' ').split('.')[0]
						}))
						
						if (page === 1) {
							this.historyList = newRecords
						} else {
							this.historyList = [...this.historyList, ...newRecords]
						}
						
						this.hasMore = res.data.hasMore
						this.currentPage = page
						
						console.log('当前页数:', this.currentPage)
						console.log('是否还有更多:', this.hasMore)
						console.log('当前列表长度:', this.historyList.length)
					}
				},
				fail: (err) => {
					console.error('请求失败:', err)
					uni.showToast({
						title: '获取历史记录失败',
						icon: 'none'
					})
				},
				complete: () => {
					this.isLoading = false
					if (page > 1) {
						uni.hideLoading()
					}
				}
			})
		},
		
		// 添加加载更多方法
		loadMore() {
			console.log('触发加载更多')
			// 添加延时，避免频繁触发
			if (this.hasMore && !this.isLoading) {
				setTimeout(() => {
					console.log('开始加载第', this.currentPage + 1, '页')
					this.getHistoryList(this.currentPage + 1)
				}, 100)
			}
		},
		
		// 显示历史记录详情
		showHistoryDetail(item) {
			// 添加调试日志
			console.log('查看记录详情:', item)
			
			uni.request({
				url: config.baseUrl + '/api/record/detail',
				method: 'GET',
				data: {
					record_id: item.recordId
				},
				success: (res) => {
					console.log('详情返回数据:', res.data)
					if (res.data.success) {
						this.recognitionResult = res.data.data
						this.showResultPopup = true
					} else {
						uni.showToast({
							title: '获取详情失败',
							icon: 'none'
						})
					}
				},
				fail: (err) => {
					console.error('请求失败:', err)
					uni.showToast({
						title: '获取详情失败',
						icon: 'none'
					})
				}
			})
		},
		
		// 获取图片URL
		getImageUrl(path) {
			if (!path) return ''
			// 添加调试日志
			console.log('原始路径:', path)
			const url = config.baseUrl + '/' + path.replace(/^\/+/, '')
			console.log('完整URL:', url)
			return url
		},
		
		// 添加退出登录方法
		handleLogout() {
			uni.showModal({
				title: '提示',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						// 清除本地存储的用户信息
						uni.removeStorageSync('userInfo')
						// 跳转到登录页
						uni.reLaunch({
							url: '/pages/login/login'
						})
					}
				}
			})
		}
		}
	}
</script>

<style>
.container {
	min-height: 100vh;
	background: linear-gradient(180deg, #eef7ef 0%, #f8fbf8 40%, #f5f5f5 100%);
	padding-bottom: 100rpx; /* 为底部tabBar留出空间 */
}

	.content {
	/* 移除 padding-top */
	min-height: 100vh;
	display: flex;
	flex-direction: column;
}

.main {
	flex: 1;
	padding: 20rpx;  /* 减小整体内边距 */
	display: flex;
	flex-direction: column;
	gap: 20rpx;  /* 减小卡片之间的间距 */
}

.user-card {
	background: rgba(255, 255, 255, 0.95);
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 8rpx 24rpx rgba(28, 74, 39, 0.08);
	margin-bottom: 20rpx;  /* 减小底部间距 */
}

.user-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.welcome {
	font-size: 32rpx;
	font-weight: 500;
	color: #333;
}

.logout {
	font-size: 28rpx;
	color: #fff;
	padding: 10rpx 20rpx;
	background: linear-gradient(135deg, #2C8A43, #3CA55C);
	border-radius: 30rpx;
}

.function-card, .history-card {
	background: rgba(255, 255, 255, 0.96);
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 8rpx 24rpx rgba(28, 74, 39, 0.08);
}

.card-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 30rpx;
	padding-left: 16rpx;
	border-left: 8rpx solid #2C8A43;
}

.upload-section {
	padding: 20rpx 0;
}

.upload-box {
	width: 100%;
	height: 400rpx;
	background: #f7fbf7;
	border-radius: 16rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	border: 2rpx dashed #b7d9bf;
}

.preview-image {
	width: 100%;
	height: 100%;
	border-radius: 16rpx;
}

.upload-placeholder {
	text-align: center;
}

.upload-text {
	font-size: 32rpx;
	color: #666;
	margin-bottom: 10rpx;
	display: block;
}

.upload-desc {
	font-size: 24rpx;
	color: #999;
}

.submit-btn {
	width: 100%;
	height: 88rpx;
	line-height: 88rpx;
	background: linear-gradient(135deg, #2C8A43, #3CA55C);
	color: #fff;
	font-size: 32rpx;
	border-radius: 44rpx;
	margin-top: 30rpx;
}

.submit-btn[disabled] {
	background: #ccc;
	color: #fff;
}

.history-card {
	margin: 0;
	height: auto;
	min-height: 400rpx;
	display: flex;
	flex-direction: column;
	/* 添加固定高度 */
	height: 700rpx;
}

.history-list {
	flex: 1;
	/* 确保高度正确 */
	height: 600rpx !important;
	overflow-y: scroll;
	-webkit-overflow-scrolling: touch;
}

.history-item {
	display: flex;
	align-items: center;
	padding: 20rpx;
	border-bottom: 2rpx solid #edf4ee;
	background: transparent;
	/* 确保每个项目有固定高度 */
	min-height: 120rpx;
}

.history-item:last-child {
	border-bottom: none;
}

.history-image {
	width: 120rpx;
	height: 120rpx;
	border-radius: 12rpx;
	margin-right: 20rpx;
	object-fit: cover;
	flex-shrink: 0;
}

.history-info {
	flex: 1;
	overflow: hidden;
}

.disease-name {
	font-size: 28rpx;
	color: #333;
	margin-bottom: 6rpx;
	display: block;
	font-weight: 500;
}

.crop-name {
	font-size: 24rpx;
	color: #666;
	margin-bottom: 6rpx;
	display: block;
}

.confidence {
	font-size: 24rpx;
	color: #1f7a34;
	margin-bottom: 6rpx;
	display: block;
}

.time {
	font-size: 24rpx;
	color: #999;
	display: block;
}

.empty-tip {
	text-align: center;
	color: #999;
	font-size: 28rpx;
	padding: 40rpx 0;
}

.popup-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0,0,0,0.6);
	z-index: 999;
		display: flex;
	align-items: center;
		justify-content: center;
	}

.popup-content {
	width: 90%;
	max-height: 90vh;
	background: #fff;
	border-radius: 20rpx;
	overflow: hidden;
}

.popup-header {
	padding: 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-bottom: 2rpx solid #f5f5f5;
}

.popup-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.popup-close {
	font-size: 40rpx;
	color: #999;
	padding: 0 20rpx;
}

.popup-body {
	padding: 30rpx;
	max-height: calc(90vh - 100rpx);
	overflow-y: auto;
}

.result-item {
	display: flex;
	margin-bottom: 20rpx;
}

.label {
	color: #666;
	width: 160rpx;
}

.value {
	color: #333;
	flex: 1;
	font-weight: 500;
}

.divider {
	height: 2rpx;
	background: #f5f5f5;
	margin: 30rpx 0;
}

/* 完全展开的样式，移除嵌套 */
.solution-section {
	padding: 20rpx 0;
}

.solution-section-subtitle {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	margin: 20rpx 0;
	display: block;
}

.solution-section-content {
	font-size: 26rpx;
	color: #666;
	line-height: 1.6;
	margin-bottom: 30rpx;
	display: block;
}

.status-healthy {
	color: #2C8A43 !important;
}

.status-warning {
	color: #d98307 !important;
}

.status-danger {
	color: #d64545 !important;
}

.loading-more, .no-more {
	text-align: center;
	padding: 20rpx 0;
	color: #999;
	font-size: 24rpx;
}

/* 添加滚动条样式 */
::-webkit-scrollbar {
	width: 0;
	height: 0;
	color: transparent;
	}
</style>
