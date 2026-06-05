<template>
  <view class="discuss-page">
    <view class="hero-section">
      <image class="hero-bg" src="/static/ui/backgrounds/bg-discuss-hero.png" mode="aspectFill" />
      <view class="hero-overlay"></view>
      <view class="hero-blob hero-blob-left"></view>
      <view class="hero-blob hero-blob-right"></view>
      <image class="hero-decor hero-decor-tl" src="/static/ui/decor/leaf-corner-tl.png" mode="aspectFit" />
      <image class="hero-decor hero-decor-br" src="/static/ui/decor/leaf-corner-br.png" mode="aspectFit" />


      <view class="hero-content">
        <view class="brand-chip">
          <image class="brand-chip-icon" src="/static/ui/icons/ic-community.svg" mode="aspectFit" />
          <text class="brand-chip-text">讨论</text>
        </view>
        <view class="hero-title">农业社区</view>
        <view class="hero-subtitle">交流种植经验，分享识别案例与防治心得</view>
      </view>
    </view>

    <view class="content-wrap">
      <view class="quick-card card">
        <view class="quick-left">
          <view class="quick-icon-wrap">
            <image class="quick-icon" src="/static/ui/icons/ic-post.svg" mode="aspectFit" />
          </view>
          <view class="quick-meta">
            <text class="quick-title">发布农技动态</text>
            <text class="quick-desc">支持图文内容，最多上传 9 张图片</text>
          </view>
        </view>
        <view class="quick-btn" @tap="openPostSheet">发帖</view>
      </view>

      <view class="feed-card card">
        <view class="section-head section-head-between">
          <view class="section-head-left">
            <view class="section-mark"></view>
            <text class="section-title">社区动态</text>
          </view>
          <text class="section-link" @tap="refreshPosts">刷新</text>
        </view>

        <template v-if="loading && posts.length === 0">
          <view class="state-box">
            <text class="state-text">正在加载社区内容...</text>
          </view>
        </template>

        <template v-else-if="posts.length === 0">
          <view class="empty-box">
            <image class="empty-image" src="/static/ui/empty/empty-posts.png" mode="aspectFit" />
            <text class="empty-title">社区还没有帖子</text>
            <text class="empty-desc">发布第一条图文内容，分享你的作物管理经验</text>
          </view>
        </template>

        <view class="post-list" v-else>
          <view class="post-card" v-for="post in posts" :key="post.post_id">
            <view class="post-head">
              <view class="avatar">{{ getInitial(post.username) }}</view>
              <view class="post-user">
                <view class="post-name-row">
                  <text class="post-name">{{ post.username || '农友' }}</text>
                  <text class="post-status">交流中</text>
                </view>
                <text class="post-time">{{ post.create_time }}</text>
              </view>
            </view>

            <view class="post-content" v-if="post.content">
              <text class="post-text" :class="{ collapsed: !post.expanded && post.content.length > 80 }">{{ post.content }}</text>
              <text class="expand-link" v-if="post.content.length > 80" @tap="toggleExpand(post)">{{ post.expanded ? '收起' : '展开全文' }}</text>
            </view>

            <view class="post-images" v-if="post.images && post.images.length">
              <image
                class="post-image"
                v-for="(img, index) in post.images"
                :key="index"
                :src="fullImageUrl(img)"
                mode="aspectFill"
                @tap="previewPostImages(post.images, index)"
              />
            </view>

            <view class="post-actions">
              <view class="action-item" :class="{ liked: post.is_liked }" @tap="toggleLike(post)">
                <image class="action-icon" src="/static/ui/icons/ic-like.svg" mode="aspectFit" />
                <text>{{ post.like_count || 0 }}</text>
              </view>
              <view class="action-item" @tap="openComments(post)">
                <image class="action-icon" src="/static/ui/icons/ic-comment.svg" mode="aspectFit" />
                <text>{{ post.comment_count || 0 }}</text>
              </view>
            </view>

            <view class="comment-preview" v-if="post.comment_count">
              <text class="comment-preview-text" @tap="openComments(post)">查看全部 {{ post.comment_count }} 条评论</text>
            </view>
          </view>
        </view>

        <view class="load-more" v-if="posts.length">
          <text v-if="loadingMore">加载中...</text>
          <text v-else-if="hasMore" @tap="loadMore">加载更多</text>
          <text v-else>— 已加载全部 —</text>
        </view>
      </view>
    </view>

    <view class="float-btn" @tap="openPostSheet">
      <image class="float-icon" src="/static/ui/icons/ic-post.svg" mode="aspectFit" />
    </view>

    <view class="sheet-mask" v-if="postSheetVisible" @tap="closePostSheet"></view>
    <view class="post-sheet" v-if="postSheetVisible">
      <view class="sheet-handle"></view>
      <view class="sheet-head">
        <view>
          <text class="sheet-title">发布新帖子</text>
          <text class="sheet-subtitle">分享作物问题、识别案例或防治经验</text>
        </view>
        <text class="sheet-close" @tap="closePostSheet">关闭</text>
      </view>

      <scroll-view class="sheet-scroll" scroll-y>
        <view class="editor-card">
          <textarea
            class="post-textarea"
            v-model.trim="postForm.content"
            maxlength="500"
            placeholder="说点什么，例如病害现象、处理经验、用药建议..."
            placeholder-class="textarea-placeholder"
          />
          <view class="counter-row">
            <text>{{ postForm.content.length }}/500</text>
          </view>
        </view>

        <view class="image-editor-card">
          <view class="image-editor-head">
            <text class="image-editor-title">图片</text>
            <text class="image-editor-tip">{{ postForm.images.length }}/9</text>
          </view>
          <view class="selected-grid">
            <view class="selected-img-wrap" v-for="(img, index) in postForm.images" :key="index">
              <image class="selected-img" :src="img" mode="aspectFill" @tap="previewLocalImages(index)" />
              <view class="remove-img" @tap.stop="removeLocalImage(index)">×</view>
            </view>
            <view class="add-img" v-if="postForm.images.length < 9" @tap="choosePostImages">
              <image class="add-img-icon" src="/static/ui/icons/ic-upload.svg" mode="aspectFit" />
              <text>添加图片</text>
            </view>
          </view>
        </view>
      </scroll-view>

      <view class="sheet-footer">
        <button class="submit-btn" :loading="publishing" :disabled="publishing" @tap="submitPost">
          <text class="submit-btn-text">{{ publishing ? '发布中...' : '发布帖子' }}</text>
        </button>
      </view>
    </view>

    <view class="sheet-mask" v-if="commentSheetVisible" @tap="closeComments"></view>
    <view class="comment-sheet" v-if="commentSheetVisible">
      <view class="sheet-handle"></view>
      <view class="sheet-head compact">
        <view>
          <text class="sheet-title">评论</text>
          <text class="sheet-subtitle">{{ activePost ? activePost.comment_count || 0 : 0 }} 条讨论</text>
        </view>
        <text class="sheet-close" @tap="closeComments">关闭</text>
      </view>

      <scroll-view class="comment-scroll" scroll-y>
        <view class="comment-source" v-if="activePost">
          <view class="comment-source-head">
            <view class="mini-avatar">{{ getInitial(activePost.username) }}</view>
            <text class="comment-source-name">{{ activePost.username || '农友' }}</text>
          </view>
          <text class="comment-source-text">{{ activePost.content || '图片分享' }}</text>
        </view>

        <template v-if="commentsLoading">
          <view class="state-box compact-state">
            <text class="state-text">正在加载评论...</text>
          </view>
        </template>

        <template v-else-if="comments.length === 0">
          <view class="empty-box comment-empty">
            <image class="empty-image small" src="/static/ui/empty/empty-posts.png" mode="aspectFit" />
            <text class="empty-title">暂无评论</text>
            <text class="empty-desc">留下你的建议或经验，帮助更多农友</text>
          </view>
        </template>

        <view class="comment-list" v-else>
          <view class="comment-item" v-for="comment in comments" :key="comment.comment_id">
            <view class="mini-avatar">{{ getInitial(comment.username) }}</view>
            <view class="comment-body">
              <view class="comment-meta">
                <text class="comment-name">{{ comment.username || '农友' }}</text>
                <text class="comment-time">{{ comment.create_time }}</text>
              </view>
              <text class="comment-text">{{ comment.content }}</text>
            </view>
          </view>
        </view>
      </scroll-view>

      <view class="comment-input-bar">
        <input
          class="comment-input"
          v-model.trim="commentText"
          placeholder="说点什么..."
          placeholder-class="comment-placeholder"
          confirm-type="send"
          @confirm="submitComment"
        />
        <view class="send-btn" @tap="submitComment">
          <image class="send-icon" src="/static/ui/icons/ic-comment.svg" mode="aspectFit" />
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
      userInfo: null,
      posts: [],
      page: 1,
      pageSize: 10,
      hasMore: true,
      loading: false,
      loadingMore: false,
      postSheetVisible: false,
      publishing: false,
      postForm: {
        content: '',
        images: []
      },
      commentSheetVisible: false,
      activePost: null,
      comments: [],
      commentsLoading: false,
      commentText: ''
    }
  },
  onShow() {
    this.loadUserInfo()
    this.refreshPosts()
  },
  onPullDownRefresh() {
    this.refreshPosts().finally(() => {
      uni.stopPullDownRefresh()
    })
  },
  onReachBottom() {
    this.loadMore()
  },
  methods: {
    loadUserInfo() {
      const userInfo = uni.getStorageSync('userInfo')
      this.userInfo = userInfo && userInfo.userId ? userInfo : null
    },
    async refreshPosts() {
      this.page = 1
      this.hasMore = true
      this.loading = true
      try {
        const posts = await this.fetchPosts(1)
        this.posts = posts
        this.hasMore = posts.length >= this.pageSize
      } catch (error) {
        console.error('refresh posts error:', error)
        this.toast('社区内容加载失败')
      } finally {
        this.loading = false
      }
    },
    async loadMore() {
      if (this.loading || this.loadingMore || !this.hasMore) return
      this.loadingMore = true
      try {
        const nextPage = this.page + 1
        const posts = await this.fetchPosts(nextPage)
        this.posts = this.posts.concat(posts)
        this.page = nextPage
        this.hasMore = posts.length >= this.pageSize
      } catch (error) {
        console.error('load more posts error:', error)
        this.toast('加载更多失败')
      } finally {
        this.loadingMore = false
      }
    },
    fetchPosts(page) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: config.baseUrl + '/api/posts',
          method: 'GET',
          data: {
            page,
            page_size: this.pageSize,
            user_id: this.userInfo ? this.userInfo.userId : undefined
          },
          success: ({ data }) => {
            if (data && data.success) {
              const posts = (data.posts || []).map(item => ({
                ...item,
                expanded: false
              }))
              resolve(posts)
              return
            }
            reject(new Error((data && data.message) || '获取失败'))
          },
          fail: reject
        })
      })
    },
    openPostSheet() {
      if (!this.ensureLogin()) return
      this.postSheetVisible = true
    },
    closePostSheet() {
      if (this.publishing) return
      this.postSheetVisible = false
    },
    choosePostImages() {
      const remain = 9 - this.postForm.images.length
      if (remain <= 0) return
      uni.chooseImage({
        count: remain,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: ({ tempFilePaths }) => {
          this.postForm.images = this.postForm.images.concat(tempFilePaths || []).slice(0, 9)
        }
      })
    },
    removeLocalImage(index) {
      this.postForm.images.splice(index, 1)
    },
    previewLocalImages(index) {
      uni.previewImage({
        current: this.postForm.images[index],
        urls: this.postForm.images
      })
    },
    async submitPost() {
      if (!this.ensureLogin()) return
      if (!this.postForm.content && this.postForm.images.length === 0) {
        this.toast('请输入内容或选择图片')
        return
      }
      if (this.publishing) return

      this.publishing = true
      try {
        const imagePaths = []
        for (const filePath of this.postForm.images) {
          const uploadedPath = await this.uploadPostImage(filePath)
          if (uploadedPath) imagePaths.push(uploadedPath)
        }

        await this.createPost(imagePaths)
        uni.showToast({ title: '发布成功', icon: 'success' })
        this.postForm = { content: '', images: [] }
        this.postSheetVisible = false
        this.refreshPosts()
      } catch (error) {
        console.error('submit post error:', error)
        this.toast(error.message || '发布失败')
      } finally {
        this.publishing = false
      }
    },
    uploadPostImage(filePath) {
      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: config.baseUrl + '/api/upload',
          filePath,
          name: 'file',
          success: ({ data }) => {
            try {
              const payload = typeof data === 'string' ? JSON.parse(data) : data
              if (payload && payload.success) {
                resolve(payload.path)
                return
              }
              reject(new Error((payload && payload.message) || '图片上传失败'))
            } catch (error) {
              reject(error)
            }
          },
          fail: reject
        })
      })
    },
    createPost(imagePaths) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: config.baseUrl + '/api/posts',
          method: 'POST',
          data: {
            user_id: this.userInfo.userId,
            content: this.postForm.content,
            images: imagePaths.join(',')
          },
          header: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          success: ({ data }) => {
            if (data && data.success) {
              resolve(data)
              return
            }
            reject(new Error((data && data.message) || '发布失败'))
          },
          fail: reject
        })
      })
    },
    async toggleLike(post) {
      if (!this.ensureLogin()) return
      const oldLiked = !!post.is_liked
      post.is_liked = !oldLiked
      post.like_count = Math.max(0, Number(post.like_count || 0) + (oldLiked ? -1 : 1))

      try {
        await new Promise((resolve, reject) => {
          uni.request({
            url: `${config.baseUrl}/api/posts/${post.post_id}/like`,
            method: 'POST',
            data: {
              user_id: this.userInfo.userId
            },
            header: {
              'Content-Type': 'application/json'
            },
            success: ({ data }) => {
              if (data && data.success) {
                resolve(data)
                return
              }
              reject(new Error((data && data.message) || '操作失败'))
            },
            fail: reject
          })
        })
      } catch (error) {
        post.is_liked = oldLiked
        post.like_count = Math.max(0, Number(post.like_count || 0) + (oldLiked ? 1 : -1))
        console.error('like error:', error)
        this.toast('操作失败')
      }
    },
    async openComments(post) {
      this.activePost = post
      this.commentSheetVisible = true
      this.commentText = ''
      await this.fetchComments(post)
    },
    closeComments() {
      this.commentSheetVisible = false
      this.activePost = null
      this.comments = []
      this.commentText = ''
    },
    fetchComments(post) {
      this.commentsLoading = true
      return new Promise((resolve) => {
        uni.request({
          url: `${config.baseUrl}/api/posts/${post.post_id}/comments`,
          method: 'GET',
          success: ({ data }) => {
            if (data && data.success) {
              this.comments = data.comments || []
            } else {
              this.comments = []
              this.toast((data && data.message) || '评论加载失败')
            }
            resolve()
          },
          fail: () => {
            this.comments = []
            this.toast('评论加载失败')
            resolve()
          },
          complete: () => {
            this.commentsLoading = false
          }
        })
      })
    },
    async submitComment() {
      if (!this.ensureLogin()) return
      if (!this.activePost) return
      if (!this.commentText) {
        this.toast('请输入评论内容')
        return
      }

      const content = this.commentText
      this.commentText = ''
      try {
        await new Promise((resolve, reject) => {
          uni.request({
            url: `${config.baseUrl}/api/posts/${this.activePost.post_id}/comments`,
            method: 'POST',
            data: {
              user_id: this.userInfo.userId,
              content
            },
            header: {
              'Content-Type': 'application/json'
            },
            success: ({ data }) => {
              if (data && data.success) {
                resolve(data)
                return
              }
              reject(new Error((data && data.message) || '评论失败'))
            },
            fail: reject
          })
        })

        this.activePost.comment_count = Number(this.activePost.comment_count || 0) + 1
        await this.fetchComments(this.activePost)
      } catch (error) {
        this.commentText = content
        console.error('comment error:', error)
        this.toast('评论失败')
      }
    },
    toggleExpand(post) {
      post.expanded = !post.expanded
    },
    previewPostImages(images, index) {
      const urls = images.map(img => this.fullImageUrl(img))
      uni.previewImage({
        current: urls[index],
        urls
      })
    },
    fullImageUrl(path) {
      if (!path) return '/static/ui/empty/empty-posts.png'
      if (/^https?:\/\//.test(path)) return path
      if (path.startsWith('/')) return config.baseUrl + path
      return `${config.baseUrl}/${path}`
    },
    getInitial(name) {
      if (!name) return '农'
      return String(name).slice(0, 1)
    },
    ensureLogin() {
      if (this.userInfo && this.userInfo.userId) return true
      uni.showModal({
        title: '请先登录',
        content: '登录后可发布帖子、点赞和评论。',
        confirmText: '去登录',
        success: ({ confirm }) => {
          if (confirm) {
            uni.navigateTo({ url: '/pages/login/login' })
          }
        }
      })
      return false
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

.discuss-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #edf7ed 0%, #f7fbf6 40%, #f4faf4 100%);
  padding-bottom: 150rpx;
}

.hero-section {
  position: relative;
  height: 400rpx;
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
  background: linear-gradient(180deg, rgba(41, 130, 64, 0.18) 0%, rgba(65, 179, 92, 0.34) 50%, rgba(101, 204, 126, 0.64) 100%);
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
  top: 104rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.28) 0%, rgba(255, 255, 255, 0.08) 58%, rgba(255, 255, 255, 0) 100%);
}

.hero-blob-right {
  width: 220rpx;
  height: 220rpx;
  right: -48rpx;
  top: 74rpx;
  background: radial-gradient(circle, rgba(214, 255, 222, 0.28) 0%, rgba(214, 255, 222, 0.08) 60%, rgba(214, 255, 222, 0) 100%);
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
  margin-top: -70rpx;
  padding: 0 24rpx 42rpx;
}

.card {
  background: rgba(255, 255, 255, 0.96);
  border-radius: 32rpx;
  box-shadow: 0 20rpx 54rpx rgba(31, 101, 46, 0.10);
  border: 2rpx solid rgba(255, 255, 255, 0.7);
}

.quick-card {
  padding: 26rpx 28rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.quick-left {
  min-width: 0;
  display: flex;
  align-items: center;
}

.quick-icon-wrap {
  width: auto;
  height: auto;
  border-radius: 0;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-shrink: 0;
}

.quick-icon {
  width: 80rpx;
  height: 80rpx;
}

.quick-meta {
  min-width: 0;
  margin-left: 18rpx;
}

.quick-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #243126;
}

.quick-desc {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #8a9a8d;
}

.quick-btn {
  min-width: 106rpx;
  height: 58rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #31b35d 0%, #42bb65 100%);
  color: #ffffff;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 24rpx rgba(57, 169, 75, 0.22);
}

.feed-card {
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

.empty-image.small {
  width: 190rpx;
  height: 130rpx;
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

.post-list {
  margin-top: 18rpx;
}

.post-card {
  padding: 26rpx 0;
  border-bottom: 2rpx solid #eef4ee;
}

.post-card:last-child {
  border-bottom: none;
}

.post-head {
  display: flex;
  align-items: center;
}

.avatar,
.mini-avatar {
  border-radius: 50%;
  background: linear-gradient(135deg, #2ea14d 0%, #48bf63 100%);
  color: #ffffff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar {
  width: 82rpx;
  height: 82rpx;
  font-size: 34rpx;
  box-shadow: 0 10rpx 22rpx rgba(57, 169, 75, 0.22);
}

.mini-avatar {
  width: 52rpx;
  height: 52rpx;
  font-size: 24rpx;
}

.post-user {
  min-width: 0;
  margin-left: 16rpx;
}

.post-name-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10rpx;
}

.post-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #243126;
}

.post-status {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: #edf8ef;
  color: #39a94b;
  font-size: 20rpx;
  font-weight: 600;
}

.post-time {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #97a698;
}

.post-content {
  margin-top: 22rpx;
}

.post-text {
  display: block;
  font-size: 29rpx;
  line-height: 1.75;
  color: #38483c;
}

.post-text.collapsed {
  max-height: 154rpx;
  overflow: hidden;
}

.expand-link {
  display: inline-block;
  margin-top: 8rpx;
  color: #39a94b;
  font-size: 24rpx;
  font-weight: 600;
}

.post-images {
  margin-top: 18rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.post-image {
  width: 196rpx;
  height: 196rpx;
  border-radius: 22rpx;
  background: #f1f6f1;
}

.post-actions {
  margin-top: 22rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.action-item {
  height: 58rpx;
  padding: 0 20rpx;
  border-radius: 999rpx;
  background: #f3f7f3;
  color: #738074;
  font-size: 24rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.action-item.liked {
  background: #edf8ef;
  color: #39a94b;
}

.action-icon {
  width: 50rpx;
  height: 50rpx;
}

.comment-preview {
  margin-top: 14rpx;
  padding: 16rpx 18rpx;
  border-radius: 18rpx;
  background: #f8fbf8;
}

.comment-preview-text {
  font-size: 24rpx;
  color: #7d8c80;
}

.load-more {
  padding: 28rpx 0 4rpx;
  text-align: center;
  color: #98a798;
  font-size: 24rpx;
}

.float-btn {
  position: fixed;
  right: 34rpx;
  bottom: 154rpx;
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #31b35d 0%, #42bb65 100%);
  box-shadow: 0 16rpx 36rpx rgba(57, 169, 75, 0.28);
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
}

.float-icon {
  width: 44rpx;
  height: 44rpx;
}

.sheet-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(22, 32, 24, 0.32);
  z-index: 30;
}

.post-sheet,
.comment-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 31;
  background: #ffffff;
  border-top-left-radius: 34rpx;
  border-top-right-radius: 34rpx;
  box-shadow: 0 -16rpx 48rpx rgba(31, 101, 46, 0.12);
  overflow: hidden;
}

.post-sheet {
  height: 82vh;
}

.comment-sheet {
  height: 76vh;
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

.sheet-head.compact {
  align-items: center;
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

.sheet-scroll {
  height: calc(82vh - 228rpx);
}

.editor-card,
.image-editor-card {
  margin: 0 28rpx 22rpx;
  padding: 22rpx;
  border-radius: 26rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
}

.post-textarea {
  width: 100%;
  height: 210rpx;
  font-size: 28rpx;
  line-height: 1.7;
  color: #243126;
}

.textarea-placeholder {
  color: #a2b0a4;
}

.counter-row {
  margin-top: 12rpx;
  text-align: right;
  font-size: 22rpx;
  color: #98a798;
}

.image-editor-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.image-editor-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #243126;
}

.image-editor-tip {
  font-size: 23rpx;
  color: #8c9b8f;
}

.selected-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.selected-img-wrap,
.add-img {
  position: relative;
  width: 190rpx;
  height: 190rpx;
  border-radius: 22rpx;
  overflow: hidden;
}

.selected-img {
  width: 100%;
  height: 100%;
}

.remove-img {
  position: absolute;
  right: 8rpx;
  top: 8rpx;
  width: 38rpx;
  height: 38rpx;
  border-radius: 50%;
  background: rgba(36, 49, 38, 0.55);
  color: #ffffff;
  font-size: 28rpx;
  line-height: 36rpx;
  text-align: center;
}

.add-img {
  border: 2rpx dashed #cfe3d0;
  background: #f6fbf6;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #39a94b;
  font-size: 24rpx;
  font-weight: 600;
}

.add-img-icon {
  width: 46rpx;
  height: 46rpx;
  margin-bottom: 10rpx;
}

.sheet-footer {
  padding: 18rpx 28rpx 32rpx;
  background: #ffffff;
}

.submit-btn {
  width: 100%;
  height: 92rpx;
  line-height: 92rpx;
  border-radius: 999rpx;
  border: none;
  background: linear-gradient(90deg, #31b35d 0%, #2ea14d 52%, #42bb65 100%);
  box-shadow: 0 16rpx 32rpx rgba(57, 169, 75, 0.24);
}

.submit-btn::after {
  border: none;
}

.submit-btn-text {
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
}

.comment-scroll {
  height: calc(76vh - 190rpx);
}

.comment-source {
  margin: 0 28rpx 18rpx;
  padding: 22rpx;
  border-radius: 24rpx;
  background: #f8fbf8;
  border: 2rpx solid #edf2ed;
}

.comment-source-head {
  display: flex;
  align-items: center;
}

.comment-source-name {
  margin-left: 14rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #243126;
}

.comment-source-text {
  display: block;
  margin-top: 14rpx;
  font-size: 26rpx;
  line-height: 1.7;
  color: #5d6d61;
}

.compact-state {
  padding-top: 26rpx;
}

.comment-empty {
  padding-top: 28rpx;
}

.comment-list {
  padding: 0 28rpx 24rpx;
}

.comment-item {
  display: flex;
  align-items: flex-start;
  padding: 22rpx 0;
  border-bottom: 2rpx solid #eff4ef;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-body {
  flex: 1;
  min-width: 0;
  margin-left: 14rpx;
}

.comment-meta {
  display: flex;
  flex-direction: column;
}

.comment-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #243126;
}

.comment-time {
  margin-top: 6rpx;
  font-size: 20rpx;
  color: #9aaa9a;
}

.comment-text {
  display: block;
  margin-top: 10rpx;
  font-size: 26rpx;
  line-height: 1.7;
  color: #4d5d50;
}

.comment-input-bar {
  padding: 18rpx 24rpx 28rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #ffffff;
  border-top: 2rpx solid #eff4ef;
}

.comment-input {
  flex: 1;
  height: 78rpx;
  padding: 0 26rpx;
  border-radius: 999rpx;
  background: #f5f9f5;
  font-size: 27rpx;
  color: #243126;
}

.comment-placeholder {
  color: #a3b0a5;
}

.send-btn {
  width: 78rpx;
  height: 78rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #31b35d 0%, #42bb65 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 22rpx rgba(57, 169, 75, 0.22);
}

.send-icon {
  width: 34rpx;
  height: 34rpx;
}
</style>
