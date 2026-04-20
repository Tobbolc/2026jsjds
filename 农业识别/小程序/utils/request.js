const request = (options) => {
  const token = uni.getStorageSync('token')
  
  return new Promise((resolve, reject) => {
    uni.request({
      ...options,
      header: {
        ...options.header,
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode === 401) {
          // token过期或无效
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.redirectTo({
            url: '/pages/login/login'
          })
          reject(new Error('未登录或登录已过期'))
        } else {
          resolve(res)
        }
      },
      fail: reject
    })
  })
}

export default request 