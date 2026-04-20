<template>
	<view class="container">
		<!-- 发布按钮 -->
		<view class="publish-btn" @tap="showPublishPopup">
			<text class="plus-icon">+</text>
		</view>
		
		<!-- 帖子列表 -->
		<scroll-view 
			scroll-y 
			class="post-list" 
			@scrolltolower="loadMore"
			refresher-enabled
			:refresher-triggered="isRefreshing"
			@refresherrefresh="onRefresh"
		>
			<view class="post-item" v-for="(post, index) in posts" :key="post.post_id">
				<!-- 用户信息栏 -->
				<view class="post-header">
					<view class="user-info">
						<view class="avatar">{{post.username[0]}}</view>
						<view class="user-meta">
							<text class="username">{{post.username}}</text>
							<text class="time">{{post.create_time}}</text>
						</view>
					</view>
					<view class="more-btn">
						<uni-icons type="more-filled" size="20" color="#999"></uni-icons>
					</view>
				</view>
				
				<!-- 帖子内容 -->
				<view class="post-content">
					<text class="content-text" :class="{'content-expanded': post.isExpanded}" @tap="toggleContent(post)">
						{{post.content}}
					</text>
					<text class="expand-btn" v-if="post.content.length > 100 && !post.isExpanded" @tap="toggleContent(post)">
						展开
					</text>
					
					<!-- 图片网格优化 -->
					<view class="image-grid" v-if="post.images && post.images.length">
						<view 
							class="image-item" 
							v-for="(image, imgIndex) in post.images" 
							:key="imgIndex"
							@tap="previewImage(post.images, imgIndex)"
						>
							<image :src="getImageUrl(image)" mode="aspectFill"></image>
						</view>
					</view>
				</view>
				
				<!-- 互动栏优化 -->
				<view class="post-footer">
					<view class="action-btn like-btn" :class="{'liked': post.is_liked}" @tap.stop="toggleLike(post)">
						<view class="action-icon">
							<uni-icons 
								:type="post.is_liked ? 'heart-filled' : 'heart'" 
								size="22" 
								:color="post.is_liked ? '#ff4444' : '#666'"
								:class="{'heart-beat': post.isLiking}"
							></uni-icons>
							<text class="count-text" :class="{'liked': post.is_liked}">
								{{post.like_count || '点赞'}}
							</text>
						</view>
					</view>
				</view>

				<!-- 添加评论区 -->
				<view class="comments-section">
					<!-- 评论输入框 -->
					<view class="comment-input-wrapper">
						<input 
							class="comment-input" 
							v-model="post.newComment"
							placeholder="说点什么..."
							@confirm="submitComment(post)"
						/>
						<button 
							class="send-btn" 
							:disabled="!post.newComment"
							@tap="submitComment(post)"
						>发送</button>
					</view>

					<!-- 评论列表 -->
					<view class="comments-list" v-if="post.comments && post.comments.length">
						<view class="comment-item" v-for="comment in post.comments" :key="comment.comment_id">
							<view class="comment-user">
								<text class="comment-username">{{comment.username}}</text>
								<text class="comment-time">{{comment.create_time}}</text>
							</view>
							<text class="comment-content">{{comment.content}}</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 加载更多 -->
			<view class="loading-more" v-if="isLoading">加载中...</view>
			<view class="no-more" v-if="!hasMore && posts.length">没有更多了</view>
			<view class="empty-tip" v-if="!posts.length && !isLoading">暂无帖子</view>
		</scroll-view>
		
		<!-- 发布弹窗 -->
		<view class="popup-mask" v-if="showPublish" @tap="closePublishPopup">
			<view class="popup-content publish-popup" @tap.stop>
				<view class="popup-header">
					<text class="cancel-btn" @tap="closePublishPopup">取消</text>
					<text class="popup-title">发布帖子</text>
					<button 
						class="publish-btn-small" 
						:disabled="!newPost.content && !newPost.images.length"
						@tap="submitPost"
					>发布</button>
				</view>
				
				<view class="popup-body">
					<textarea 
						class="post-textarea" 
						v-model="newPost.content"
						placeholder="分享你的农作物种植经验..."
						maxlength="500"
						auto-height
					></textarea>
					
					<!-- 图片上传区域 -->
					<view class="upload-section">
						<view class="image-grid">
							<view 
								class="image-item" 
								v-for="(image, index) in newPost.images" 
								:key="index"
							>
								<image :src="image" mode="aspectFill"></image>
								<view class="delete-btn" @tap.stop="deleteImage(index)">×</view>
							</view>
							<view 
								class="upload-btn" 
								@tap="chooseImage" 
								v-if="newPost.images.length < 9"
							>
								<text class="camera-icon">+</text>
								<text class="upload-text">{{newPost.images.length}}/9</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 评论弹窗 -->
		<view class="popup-mask" v-if="showCommentPopup" @tap="closeCommentPopup">
			<view class="popup-content" @tap.stop>
				<view class="popup-header">
					<text class="popup-title">评论</text>
					<text class="popup-close" @tap="closeCommentPopup">×</text>
				</view>
				
				<view class="popup-body">
					<scroll-view scroll-y class="comments-list">
						<view 
							class="comment-item" 
							v-for="comment in comments" 
							:key="comment.comment_id"
						>
							<view class="comment-header">
								<text class="username">{{comment.username}}</text>
								<text class="time">{{comment.create_time}}</text>
							</view>
							<text class="comment-content">{{comment.content}}</text>
						</view>
						<view class="empty-tip" v-if="!comments.length">暂无评论</view>
					</scroll-view>
					
					<view class="comment-input-section">
						<input 
							class="comment-input" 
							v-model="newComment"
							placeholder="说点什么..."
							@confirm="submitComment"
						/>
						<button 
							class="comment-btn" 
							:disabled="!newComment"
							@tap="submitComment"
						>发送</button>
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
			posts: [],
			comments: [],
			currentPage: 1,
			pageSize: 10,
			hasMore: true,
			isLoading: false,
			isRefreshing: false,
			showPublish: false,
			showCommentPopup: false,
			currentPost: null,
			newPost: {
				content: '',
				images: []
			},
			newComment: '',
			userInfo: null
		}
	},
	onLoad() {
		this.userInfo = uni.getStorageSync('userInfo')
		if (!this.userInfo) {
			uni.redirectTo({
				url: '/pages/login/login'
			})
			return
		}
		this.getPosts()
	},
	methods: {
		// 显示发布弹窗
		showPublishPopup() {
			this.showPublish = true
		},
		
		// 关闭发布弹窗
		closePublishPopup() {
			this.showPublish = false
			this.newPost = {
				content: '',
				images: []
			}
		},
		
		// 选择图片
		chooseImage() {
			const maxCount = 9 - this.newPost.images.length
			if (maxCount <= 0) {
				uni.showToast({
					title: '最多上传9张图片',
					icon: 'none'
				})
				return
			}
			
			uni.chooseImage({
				count: maxCount,
				success: (res) => {
					this.newPost.images = [...this.newPost.images, ...res.tempFilePaths]
				}
			})
		},
		
		// 删除图片
		deleteImage(index) {
			this.newPost.images.splice(index, 1)
		},
		
		// 提交帖子
		async submitPost() {
			if (!this.newPost.content && !this.newPost.images.length) {
				return
			}
			
			try {
				// 先上传图片
				const uploadedImages = []
				for (const image of this.newPost.images) {
					try {
						const uploadRes = await uni.uploadFile({
							url: config.baseUrl + '/api/upload',
							filePath: image,
							name: 'file',
							header: {
								'content-type': 'multipart/form-data'
							},
							formData: {
								user_id: this.userInfo.userId
							}
						})
						
						const result = JSON.parse(uploadRes.data)
						if (result.success) {
							uploadedImages.push(result.path)
						}
					} catch (e) {
						console.error('图片上传失败:', e)
					}
				}
				
				// 发布帖子
				const formData = {
					user_id: this.userInfo.userId,
					content: this.newPost.content || '',
					images: uploadedImages.length ? uploadedImages.join(',') : ''
				}
				
				console.log('发布帖子数据:', formData)
				
				const res = await uni.request({
					url: config.baseUrl + '/api/posts',
					method: 'POST',
					header: {
						'content-type': 'application/x-www-form-urlencoded'
					},
					data: formData
				})
				
				if (res.data.success) {
					uni.showToast({
						title: '发布成功',
						icon: 'success'
					})
					this.closePublishPopup()
					this.refreshPosts()
				} else {
					throw new Error(res.data.message || '发布失败')
				}
			} catch (e) {
				uni.showToast({
					title: e.message || '发布失败',
					icon: 'none'
				})
				console.error('发布失败:', e)
			}
		},
		
		// 获取帖子列表
		async getPosts() {
			try {
				const res = await uni.request({
					url: `${config.baseUrl}/api/posts`,
					method: 'GET',
					data: {
						page: this.currentPage,
						page_size: this.pageSize,
						user_id: this.userInfo.userId
					}
				})
				
				if (res.data.success) {
					const posts = res.data.posts.map(post => ({
						...post,
						newComment: '',
						comments: [],
						isExpanded: false
					}))
					
					// 如果是刷新或第一页，直接替换数据
					if (this.currentPage === 1) {
						this.posts = posts
					} else {
						// 否则追加数据
						this.posts = [...this.posts, ...posts]
					}
					
					// 判断是否还有更多数据
					this.hasMore = posts.length === this.pageSize
					
					// 获取每个帖子的评论
					for (const post of posts) {
						await this.getComments(post)
					}
				}
			} catch (e) {
				console.error('获取帖子列表失败:', e)
				uni.showToast({
					title: '获取帖子失败',
					icon: 'none'
				})
				
				// 加载失败时恢复页码
				if (this.currentPage > 1) {
					this.currentPage--
				}
			} finally {
				this.isLoading = false
				this.isRefreshing = false
			}
		},
		
		// 刷新帖子列表
		refreshPosts() {
			this.currentPage = 1
			this.hasMore = true
			this.getPosts()
		},
		
		// 加载更多
		async loadMore() {
			// 如果正在加载、刷新或没有更多数据，则不执行
			if (this.isLoading || this.isRefreshing || !this.hasMore) {
				return
			}
			
			this.isLoading = true
			this.currentPage++
			await this.getPosts()
		},
		
		// 下拉刷新
		async onRefresh() {
			this.isRefreshing = true
			this.currentPage = 1
			this.hasMore = true
			await this.getPosts()
		},
		
		// 切换内容展开状态
		toggleContent(post) {
			this.$set(post, 'isExpanded', !post.isExpanded)
		},
		
		// 修改点赞方法，添加动画效果
		async toggleLike(post) {
			if (post.isLiking) return // 防止重复点击
			
			try {
				post.isLiking = true
				const res = await uni.request({
					url: `${config.baseUrl}/api/posts/${post.post_id}/like`,
					method: 'POST',
					header: {
						'content-type': 'application/json'
					},
					data: {
						user_id: this.userInfo.userId
					}
				})
				
				if (res.data.success) {
					post.is_liked = !post.is_liked
					post.like_count += post.is_liked ? 1 : -1
					
					// 只在点赞时显示动画
					if (post.is_liked) {
						setTimeout(() => {
							post.isLiking = false
						}, 800) // 动画持续时间
					} else {
						post.isLiking = false
					}
				}
			} catch (e) {
				console.error('点赞失败:', e)
				uni.showToast({
					title: '操作失败',
					icon: 'none'
				})
				post.isLiking = false
			}
		},
		
		// 显示评论
		async showComments(post) {
			this.currentPost = post
			this.showCommentPopup = true
			this.getComments(post.post_id)
		},
		
		// 关闭评论弹窗
		closeCommentPopup() {
			this.showCommentPopup = false
			this.currentPost = null
			this.newComment = ''
			this.comments = []
		},
		
		// 获取评论列表
		async getComments(post) {
			try {
				const res = await uni.request({
					url: `${config.baseUrl}/api/posts/${post.post_id}/comments`,
					method: 'GET'
				})
				
				if (res.data.success) {
					this.$set(post, 'comments', res.data.comments)
				}
			} catch (e) {
				console.error('获取评论失败:', e)
			}
		},
		
		// 修改提交评论方法
		async submitComment(post) {
			if (!post.newComment) return
			
			try {
				const res = await uni.request({
					url: `${config.baseUrl}/api/posts/${post.post_id}/comments`,
					method: 'POST',
					header: {
						'content-type': 'application/json'
					},
					data: {
						user_id: this.userInfo.userId,
						content: post.newComment
					}
				})
				
				if (res.data.success) {
					// 清空输入框
					post.newComment = ''
					// 重新获取评论
					await this.getComments(post)
					// 更新评论数
					post.comment_count++
					
					uni.showToast({
						title: '评论成功',
						icon: 'success'
					})
				}
			} catch (e) {
				console.error('评论失败:', e)
				uni.showToast({
					title: '评论失败',
					icon: 'none'
				})
			}
		},
		
		// 获取图片URL
		getImageUrl(path) {
			return config.baseUrl + '/' + path
		},
		
		// 预览图片
		previewImage(images, current) {
			uni.previewImage({
				urls: images.map(img => this.getImageUrl(img)),
				current
			})
		}
	}
}
</script>

<style>
.container {
	min-height: 100vh;
	background: linear-gradient(180deg, #eef7ef 0%, #f7faf7 35%, #f5f5f5 100%);
	padding-bottom: 100rpx;
}

/* 发布按钮 */
.publish-btn {
	position: fixed;
	right: 30rpx;
	bottom: 140rpx;
	width: 100rpx;
	height: 100rpx;
	background: linear-gradient(135deg, #2C8A43, #3CA55C);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 4rpx 16rpx rgba(44,138,67,0.3);
	z-index: 100;
}

.plus-icon {
	color: #fff;
	font-size: 50rpx;
	font-weight: bold;
	line-height: 1;
}

/* 帖子列表 */
.post-list {
	height: 100vh;
	box-sizing: border-box;
}

.post-item {
	background: rgba(255,255,255,0.97);
	margin: 20rpx;
	border-radius: 20rpx;
	padding: 24rpx;
	box-shadow: 0 8rpx 24rpx rgba(28,74,39,0.08);
}

.post-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.user-info {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.avatar {
	width: 80rpx;
	height: 80rpx;
	background: linear-gradient(135deg, #2C8A43, #3CA55C);
	color: #fff;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	font-weight: bold;
}

.user-meta {
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.username {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.time {
	font-size: 24rpx;
	color: #999;
}

.post-content {
	margin-bottom: 20rpx;
}

.content-text {
	font-size: 28rpx;
	color: #333;
	line-height: 1.6;
	margin-bottom: 16rpx;
	display: -webkit-box;
	-webkit-box-orient: vertical;
	-webkit-line-clamp: 3;
	overflow: hidden;
}

.content-expanded {
	-webkit-line-clamp: unset;
}

.expand-btn {
	font-size: 26rpx;
	color: #2C8A43;
	padding: 10rpx 0;
}

/* 图片网格优化 */
.image-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 8rpx;
	margin: 16rpx 0;
}

.image-item {
	position: relative;
	width: 100%;
	padding-bottom: 100%;
	overflow: hidden;
	background: #f8f8f8;
	border-radius: 8rpx;
}

.image-item image {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	object-fit: cover;
}

/* 互动栏优化 */
.post-footer {
	display: flex;
	gap: 32rpx;
	padding: 24rpx;
	border-top: 1rpx solid #f5f5f5;
	border-bottom: 1rpx solid #f5f5f5;
}

.action-btn {
	display: flex;
	align-items: center;
	padding: 12rpx 24rpx;
	border-radius: 40rpx;
	transition: all 0.3s ease;
	position: relative;
	overflow: hidden;
}

.like-btn {
	background: #f8f8f8;
}

.like-btn::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(255,68,68,0.1);
	transform: scale(0);
	border-radius: 40rpx;
	transition: transform 0.3s ease;
}

.like-btn.liked::before {
	transform: scale(1);
}

.action-icon {
	display: flex;
	align-items: center;
	gap: 8rpx;
	position: relative;
	z-index: 1;
}

.count-text {
	font-size: 26rpx;
	color: #666;
	margin-left: 8rpx;
	transition: all 0.3s ease;
}

.count-text.liked {
	color: #ff4444;
	font-weight: 500;
}

/* 添加点赞动画 */
@keyframes heartBeat {
	0% {
		transform: scale(1);
	}
	25% {
		transform: scale(1.3);
	}
	50% {
		transform: scale(1);
	}
	75% {
		transform: scale(1.3);
	}
	100% {
		transform: scale(1);
	}
}

.heart-beat {
	animation: heartBeat 0.8s ease-in-out;
}

/* 弹窗样式 */
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
}

/* 发布弹窗 */
.publish-popup {
	position: fixed;
	left: 0;
	right: 0;
	bottom: 0;
	width: 100%;
	max-height: 90vh;
	border-radius: 24rpx 24rpx 0 0;
	animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
	from {
		transform: translateY(100%);
	}
	to {
		transform: translateY(0);
	}
}

.popup-header {
	padding: 20rpx 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-bottom: 1rpx solid #f0f0f0;
}

.cancel-btn {
	font-size: 28rpx;
	color: #666;
	padding: 10rpx;
}

.publish-btn-small {
	font-size: 28rpx;
	color: #fff;
	background: linear-gradient(135deg, #2C8A43, #3CA55C);
	padding: 10rpx 30rpx;
	border-radius: 30rpx;
	border: none;
	margin: 0;
}

.publish-btn-small[disabled] {
	background: #ccc;
}

.post-textarea {
	width: 100%;
	min-height: 200rpx;
	padding: 20rpx;
	box-sizing: border-box;
	font-size: 28rpx;
	line-height: 1.5;
	background: #fff;
	border: none;
}

.upload-section {
	padding: 20rpx;
	background: #fff;
}

.upload-section .image-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 15rpx;
}

.upload-section .image-item {
	position: relative;
	width: 100%;
	padding-bottom: 100%;
	border-radius: 12rpx;
	overflow: hidden;
}

.upload-section .image-item image {
	position: absolute;
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.delete-btn {
	position: absolute;
	top: 6rpx;
	right: 6rpx;
	width: 40rpx;
	height: 40rpx;
	background: rgba(0,0,0,0.6);
	color: #fff;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	font-weight: bold;
	z-index: 1;
}

.upload-btn {
	position: relative;
	width: 100%;
	padding-bottom: 100%;
	background: #f8f8f8;
	border-radius: 12rpx;
	border: 2rpx dashed #ddd;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.camera-icon {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	font-size: 60rpx;
	color: #999;
	font-weight: 300;
}

.upload-text {
	position: absolute;
	bottom: 20rpx;
	left: 0;
	right: 0;
	text-align: center;
	font-size: 24rpx;
	color: #999;
}

/* 评论弹窗 */
.comments-list {
	max-height: 60vh;
	margin-bottom: 20rpx;
}

.comment-item {
	padding: 20rpx 0;
	border-bottom: 2rpx solid #f5f5f5;
}

.comment-header {
	display: flex;
	justify-content: space-between;
	margin-bottom: 10rpx;
}

.comment-content {
	font-size: 28rpx;
	color: #333;
	line-height: 1.5;
}

.comment-input-section {
	display: flex;
	gap: 20rpx;
	padding-top: 20rpx;
	border-top: 2rpx solid #f5f5f5;
}

.comment-input {
	flex: 1;
	height: 70rpx;
	background: #f8f8f8;
	border-radius: 35rpx;
	padding: 0 30rpx;
	font-size: 28rpx;
}

.comment-btn {
	width: 120rpx;
	height: 70rpx;
	line-height: 70rpx;
	background: linear-gradient(135deg, #2C8A43, #3CA55C);
	color: #fff;
	font-size: 28rpx;
	border-radius: 35rpx;
	padding: 0;
}

.comment-btn[disabled] {
	background: #ccc;
}

/* 加载更多和空状态 */
.loading-more, .no-more, .empty-tip {
	text-align: center;
	padding: 30rpx;
	color: #999;
	font-size: 26rpx;
}

/* 评论区样式 */
.comments-section {
	padding: 20rpx 0;
}

.comment-input-wrapper {
	display: flex;
	gap: 16rpx;
	padding: 16rpx 0;
	align-items: center;
}

.comment-input {
	flex: 1;
	height: 70rpx;
	background: #f8f8f8;
	border-radius: 35rpx;
	padding: 0 30rpx;
	font-size: 28rpx;
}

.send-btn {
	width: 120rpx;
	height: 70rpx;
	line-height: 70rpx;
	background: linear-gradient(135deg, #2C8A43, #3CA55C);
	color: #fff;
	font-size: 28rpx;
	border-radius: 35rpx;
	padding: 0;
}

.send-btn[disabled] {
	background: #ccc;
}

.comments-list {
	margin-top: 20rpx;
}

.comment-item {
	padding: 16rpx 0;
	border-bottom: 1rpx solid #f5f5f5;
}

.comment-user {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8rpx;
}

.comment-username {
	font-size: 26rpx;
	color: #2C8A43;
	font-weight: 500;
}

.comment-time {
	font-size: 24rpx;
	color: #999;
}

.comment-content {
	font-size: 28rpx;
	color: #333;
	line-height: 1.5;
}
</style> 
