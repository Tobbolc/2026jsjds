<template>
	<view class="container">
		<view class="status-ambience"></view>
		<view class="leaf-corner leaf-left"></view>
		<view class="leaf-corner leaf-right"></view>
		<view class="header">
			<text class="title">关于我们</text>
			<text class="header-subtitle">智慧农业 · 病虫害识别与预警系统</text>
		</view>
		
		<view class="content">
			<view class="section">
				<view class="section-header">
					<uni-icons type="info-filled" size="20" color="#2C8A43"></uni-icons>
					<text class="section-title">软件介绍</text>
				</view>
				<text class="section-content">
					本软件是一款基于深度学习的农作物病虫害智能识别系统，通过拍照或上传图片即可快速识别农作物的健康状况，并提供专业的防治建议。
				</text>
			</view>
			
			<view class="section">
				<view class="section-header">
					<uni-icons type="star-filled" size="20" color="#2C8A43"></uni-icons>
					<text class="section-title">可识别的作物类型</text>
				</view>
				<view class="crop-list">
					<view class="crop-item" v-for="(crop, index) in cropTypes" :key="index">
						<uni-icons type="leaf" size="16" color="#2C8A43"></uni-icons>
						<text class="crop-name">{{crop.name}}</text>
					</view>
				</view>
			</view>
			
			<view class="section">
				<view class="section-header">
					<uni-icons type="help-filled" size="20" color="#2C8A43"></uni-icons>
					<text class="section-title">可识别的病害类型</text>
				</view>
				<!-- 折叠面板列表 -->
				<view class="collapse-list">
					<view 
						class="collapse-item" 
						v-for="(crop, cropIndex) in groupedDiseases" 
						:key="cropIndex"
					>
						<view 
							class="collapse-header" 
							@tap="toggleCollapse(cropIndex)"
						>
							<text class="crop-name">{{crop.cropName}}</text>
							<uni-icons 
								:type="crop.isOpen ? 'arrow-up' : 'arrow-down'" 
								size="16" 
								color="#666"
							></uni-icons>
						</view>
						<view class="collapse-content" v-show="crop.isOpen">
							<view 
								class="disease-item" 
								v-for="(disease, diseaseIndex) in crop.diseases" 
								:key="diseaseIndex"
							>
								<text class="disease-name">{{disease.name}}</text>
								<text class="disease-desc">{{disease.description}}</text>
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
			cropTypes: [],
			diseases: [],
			groupedDiseases: []
		}
	},
	onLoad() {
		this.getCropTypes()
		this.getDiseases()
	},
	methods: {
		getCropTypes() {
			uni.request({
				url: config.baseUrl + '/api/crop-types',
				method: 'GET',
				success: (res) => {
					if (res.data.success) {
						this.cropTypes = res.data.cropTypes
					}
				}
			})
		},
		getDiseases() {
			uni.request({
				url: config.baseUrl + '/api/diseases',
				method: 'GET',
				success: (res) => {
					if (res.data.success) {
						this.diseases = res.data.diseases
						this.groupDiseases()
					}
				}
			})
		},
		// 将病害按作物类型分组
		groupDiseases() {
			const groups = {}
			this.diseases.forEach(disease => {
				if (!groups[disease.cropType]) {
					groups[disease.cropType] = {
						cropName: disease.cropType,
						isOpen: false,
						diseases: []
					}
				}
				groups[disease.cropType].diseases.push(disease)
			})
			this.groupedDiseases = Object.values(groups)
		},
		// 切换折叠面板
		toggleCollapse(index) {
			this.groupedDiseases[index].isOpen = !this.groupedDiseases[index].isOpen
		}
	}
}
</script>

<style>
.container {
	min-height: 100vh;
	background: linear-gradient(180deg, #dceaf2 0%, #edf6f0 28%, #eaf3ea 100%);
}

.status-ambience {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	height: 138rpx;
	background: linear-gradient(90deg, rgba(53, 156, 74, 0.84), rgba(68, 170, 88, 0.65));
	z-index: 0;
}

.leaf-corner {
	position: absolute;
	width: 180rpx;
	height: 180rpx;
	border-radius: 50%;
	z-index: 1;
	background:
		radial-gradient(circle at 40% 35%, rgba(78, 178, 98, 0.35), transparent 56%),
		radial-gradient(circle at 70% 65%, rgba(57, 161, 77, 0.2), transparent 60%);
}

.leaf-left {
	left: -80rpx;
	top: 110rpx;
}

.leaf-right {
	right: -70rpx;
	bottom: 80rpx;
}

.header {
	background: transparent;
	padding: 36rpx 30rpx 8rpx;
	color: #1f5e2f;
}

.title {
	font-size: 36rpx;
	font-weight: bold;
	display: block;
}

.header-subtitle {
	margin-top: 10rpx;
	font-size: 24rpx;
	color: #4f6f55;
	display: block;
}

.content {
	padding: 30rpx;
}

.section {
	background: rgba(255,255,255,0.86);
	border-radius: 28rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 12rpx 28rpx rgba(45,96,51,0.09);
	border: 2rpx solid rgba(255,255,255,0.66);
}

.section-header {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.section-header .section-title {
	margin-left: 10rpx;
	margin-bottom: 0;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
}

.section-content {
	font-size: 28rpx;
	color: #666;
	line-height: 1.6;
}

.crop-list {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
}

.crop-item {
	display: flex;
	align-items: center;
	gap: 10rpx;
}

.crop-name {
	font-size: 26rpx;
	color: #333;
}

.collapse-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.collapse-item {
	background: #fbfdfb;
	border-radius: 16rpx;
	overflow: hidden;
	border: 2rpx solid #e7f0e7;
}

.collapse-header {
	padding: 24rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: #f2f8f2;
}

.crop-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
}

.collapse-content {
	padding: 20rpx;
}

.disease-item {
	padding: 16rpx;
	border-bottom: 2rpx solid #f5f5f5;
}

.disease-item:last-child {
	border-bottom: none;
}

.disease-name {
	font-size: 26rpx;
	color: #333;
	margin-bottom: 8rpx;
	display: block;
}

.disease-desc {
	font-size: 24rpx;
	color: #666;
	line-height: 1.5;
}
</style> 
