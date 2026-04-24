class Config:
    # 数据库配置 - 使用pymysql驱动
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Xdj20060318%40@localhost:3306/crop_disease_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上传文件大小为16MB 