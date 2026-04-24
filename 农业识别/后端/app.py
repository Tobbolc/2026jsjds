from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import torch
import torchvision
from torch import nn
from torchvision.transforms import transforms
from PIL import Image
from datetime import datetime, timedelta
from config import Config
import pymysql  # 添加这行

# 设置pymysql替代MySQLdb
pymysql.install_as_MySQLdb()  # 添加这行

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

# 修改模型路径为相对路径
MODEL_PATH = "best_model_loss_0.4179_acc_0.8518.pth"  # 直接使用同级目录下的模型文件

# 设置上传文件目录为相对路径
UPLOAD_FOLDER = 'uploads'  # 在当前目录下创建uploads文件夹
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 加载模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 添加disease_classes字典
disease_classes = {
    0: "苹果-健康 (Apple-Healthy)",
    1: "苹果-黑星病一般 (Apple_Scab general)",
    2: "苹果-黑星病严重 (Apple_Scab serious)",
    3: "苹果-灰斑病 (Apple Frogeve Spot)",
    4: "苹果-雪松锈病一般 (Cedar Apple Rust general)",
    5: "苹果-雪松锈病严重 (Cedar Apple Rust serious)",
    6: "樱桃-健康 (Cherry-Healthy)",
    7: "樱桃-白粉病一般 (Cherry_Powdery Midew general)",
    8: "樱桃-白粉病严重 (Cherry_Powdery Midew serious)",
    9: "玉米-健康 (Corn-Healthy)",
    10: "玉米-灰斑病一般 (Cercospora zeaemaydis general)",
    11: "玉米-灰斑病严重 (Cercospora zeaemaydis serious)",
    12: "玉米-锈病一般 (Puccinia polysora general)",
    13: "玉米-锈病严重 (Puccinia polysora serious)",
    14: "玉米-叶斑病一般 (Corn Curvularia leaf spot fungus general)",
    15: "玉米-叶斑病严重 (Corn Curvularia leaf spot fungus serious)",
    16: "玉米-花叶病毒病 (Maize dwarf mosaic virus)",
    17: "葡萄-健康 (Grape-Healthy)",
    18: "葡萄-黑腐病一般 (Grape Black Rot Fungus general)",
    19: "葡萄-黑腐病严重 (Grape Black Rot Fungus serious)",
    20: "葡萄-轮斑病一般 (Grape Black Measles Fungus general)",
    21: "葡萄-轮斑病严重 (Grape Black Measles Fungus serious)",
    22: "葡萄-褐斑病一般 (Grape Leaf Blight Fungus general)",
    23: "葡萄-褐斑病严重 (Grape Leaf Blight Fungus serious)",
    24: "柑桔-健康 (Citrus-Healthy)",
    25: "柑桔-黄龙病一般 (Citrus Greening June general)",
    26: "柑桔-黄龙病严重 (Citrus Greening June serious)",
    27: "桃-健康 (Peach-Healthy)",
    28: "桃-疮痂病一般 (Peach_Bacterial Spot general)",
    29: "桃-疮痂病严重 (Peach_Bacterial Spot serious)",
    30: "辣椒-健康 (Pepper-Healthy)",
    31: "辣椒-疮痂病一般 (Pepper scab general)",
    32: "辣椒-疮痂病严重 (Pepper scab serious)",
    33: "马铃薯-健康 (Potato-Healthy)",
    34: "马铃薯-早疫病一般 (Potato_Early Blight Fungus general)",
    35: "马铃薯-早疫病严重 (Potato_Early Blight Fungus serious)",
    36: "马铃薯-晚疫病一般 (Potato_Late Blight Fungus general)",
    37: "马铃薯-晚疫病严重 (Potato_Late Blight Fungus serious)",
    38: "草莓-健康 (Strawberry-Healthy)",
    39: "草莓-叶枯病一般 (Strawberry_Scorch general)",
    40: "草莓-叶枯病严重 (Strawberry_Scorch serious)",
    41: "番茄-健康 (Tomato-Healthy)",
    42: "番茄-白粉病一般 (Tomato powdery mildew general)",
    43: "番茄-白粉病严重 (Tomato powdery mildew serious)",
    44: "番茄-疮痂病一般 (Tomato Bacterial Spot Bacteria general)",
    45: "番茄-疮痂病严重 (Tomato Bacterial Spot Bacteria serious)",
    46: "番茄-早疫病一般 (Tomato_Early Blight Fungus general)",
    47: "番茄-早疫病严重 (Tomato_Early Blight Fungus serious)",
    48: "番茄-晚疫病一般 (Tomato_Late Blight Water Mold general)",
    49: "番茄-晚疫病严重 (Tomato_Late Blight Water Mold serious)",
    50: "番茄-叶霉病一般 (Tomato_Leaf Mold Fungus general)",
    51: "番茄-叶霉病严重 (Tomato_Leaf Mold Fungus serious)",
    52: "番茄-斑点病一般 (Tomato Target Spot Bacteria general)",
    53: "番茄-斑点病严重 (Tomato Target Spot Bacteria serious)",
    54: "番茄-斑枯病一般 (Tomato_Septoria Leaf Spot Fungus general)",
    55: "番茄-斑枯病严重 (Tomato_Septoria Leaf Spot Fungus serious)",
    56: "番茄-红蜘蛛损伤一般 (Tomato Spider Mite Damage general)",
    57: "番茄-红蜘蛛损伤严重 (Tomato Spider Mite Damage serious)",
    58: "番茄-黄化曲叶病毒病一般 (Tomato YLCV Virus general)",
    59: "番茄-黄化曲叶病毒病严重 (Tomato YLCV Virus serious)",
    60: "番茄-花叶病毒病 (Tomato Tomv)"
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 模型定义和加载
def load_model(model_path, device):
    model = torchvision.models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 61)
    checkpoint = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model

# 图像预测
def predict_image(model, image_path, device):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])
    
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence = probabilities[0][predicted[0]].item()
        
    return predicted.item(), confidence

# 加载模型
model = load_model(MODEL_PATH, device).to(device)

# Users模型 - 简化版，使用明文密码
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)  # 明文密码
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

# 预测接口 - 移除token验证
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': '文件类型不允许'}), 400
            
        # 修改保存的路径格式，确保路径格式一致
        filename = secure_filename(file.filename)  # 确保文件名安全
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        
        # 确保uploads文件夹存在
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        
        # 使用os.path.join确保路径分隔符正确
        file_path = os.path.join('uploads', safe_filename)
        absolute_path = os.path.join(os.getcwd(), file_path)
        
        # 保存文件
        file.save(absolute_path)
        
        # 数据库中存储标准化的路径
        db_file_path = file_path.replace('\\', '/')  # 统一使用正斜杠
        
        # 获取用户ID（如果有的话）
        user_id = request.form.get('user_id')

        # 预测
        predicted_class, confidence = predict_image(model, file_path, device)

        # 获取作物类型和病害名称
        disease_info = disease_classes[predicted_class].split(' (')[0].split('-')
        crop_type = disease_info[0]
        disease_name = disease_info[1] if len(disease_info) > 1 else "健康"

        # 初始化变量 - 使用英文存储，用于数据库
        db_severity = "healthy"  # 数据库使用英文
        display_severity = "健康"  # 显示用中文
        disease_knowledge = None

        if disease_name != "健康":
            disease_knowledge = db.session.execute(
                db.select(DiseaseKnowledge).where(
                    db.and_(
                        DiseaseKnowledge.crop_type == crop_type,
                        DiseaseKnowledge.disease_name == disease_name
                    )
                )
            ).scalar()
            
            if disease_knowledge:
                db_severity = disease_knowledge.severity_level
                # 转换为显示用的中文
                severity_map = {
                    'healthy': '健康',
                    'general': '一般',
                    'serious': '严重'
                }
                display_severity = severity_map.get(db_severity, '未知')
            else:
                # 根据置信度判断
                if confidence > 0.8:
                    db_severity = "serious"
                    display_severity = "严重"
                elif confidence > 0.6:
                    db_severity = "general"
                    display_severity = "一般"
                else:
                    db_severity = "healthy"
                    display_severity = "健康"

        # 打印调试信息
        print(f"Disease Name: {disease_name}")
        print(f"Severity Level: {display_severity}")

        # 查询作物类型
        crop_type_info = db.session.execute(
            db.select(CropTypes).where(CropTypes.crop_name == crop_type)
        ).scalar()

        # 保存识别记录 - 使用英文的 severity
        if user_id:
            record = RecognitionRecords(
                user_id=user_id,
                image_path=db_file_path,
                disease_name=disease_name,
                confidence=confidence,
                severity_level=db_severity,  # 使用英文值
                crop_type_id=crop_type_info.crop_type_id if crop_type_info else None
            )
            db.session.add(record)
            db.session.commit()

        # 返回详细信息 - 使用中文的 severity
        return jsonify({
            'success': True,
            'data': {
                'cropInfo': {
                    'cropName': crop_type,
                    'cropNameEn': crop_type_info.crop_name_en if crop_type_info else None
                },
                'diseaseInfo': {
                    'diseaseName': disease_name,
                    'confidence': round(float(confidence) * 100, 2),
                    'severityLevel': display_severity  # 返回中文显示值
                },
                'solution': {
                    'symptoms': disease_knowledge.symptoms if disease_knowledge else None,
                    'solutions': disease_knowledge.solutions if disease_knowledge else None,
                    'preventionMethods': disease_knowledge.prevention_methods if disease_knowledge else None
                },
                'imagePath': db_file_path
            }
        })

    except Exception as e:
        print('识别错误:', str(e))
        return jsonify({
            'success': False,
            'message': '识别失败: ' + str(e)
        }), 500

# 数据库模型
class CropTypes(db.Model):
    crop_type_id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(50), unique=True, nullable=False)
    crop_name_en = db.Column(db.String(100))

class DiseaseKnowledge(db.Model):
    disease_id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # 禁用自增
    disease_name = db.Column(db.String(100), nullable=False)
    disease_name_en = db.Column(db.String(255))
    crop_type = db.Column(db.String(50))
    crop_type_id = db.Column(db.Integer, db.ForeignKey('crop_types.crop_type_id'))
    severity_level = db.Column(db.Enum('healthy', 'general', 'serious'), default='general')
    symptoms = db.Column(db.Text)
    solutions = db.Column(db.Text)
    prevention_methods = db.Column(db.Text)

class RecognitionRecords(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    image_path = db.Column(db.String(255), nullable=False)
    disease_name = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    severity_level = db.Column(db.Enum('healthy', 'general', 'serious'))
    crop_type_id = db.Column(db.Integer, db.ForeignKey('crop_types.crop_type_id'))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 直接查询用户名和明文密码
        user = db.session.execute(
            db.select(Users).where(
                db.and_(
                    Users.username == username,
                    Users.password == password
                )
            )
        ).scalar()
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        return jsonify({
            'success': True,
            'userInfo': {
                'userId': user.user_id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        
        # 检查用户名是否已存在
        existing_user = db.session.execute(
            db.select(Users).where(Users.username == username)
        ).scalar()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400
        
        # 创建新用户 - 使用明文密码
        new_user = Users(
            username=username,
            password=password,  # 直接存储明文密码
            email=email,
            phone=phone
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '注册成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# 获取历史记录接口
@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        user_id = request.args.get('user_id', type=int)
        page = request.args.get('page', 1, type=int)  # 获取页码，默认第1页
        page_size = request.args.get('page_size', 5, type=int)  # 每页数量，默认5条
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '缺少用户ID'
            }), 400
            
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询总记录数
        total = RecognitionRecords.query.filter_by(user_id=user_id).count()
        
        # 分页查询记录
        records = RecognitionRecords.query.filter_by(user_id=user_id)\
            .order_by(RecognitionRecords.create_time.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()
            
        records_list = [{
            'recordId': record.record_id,
            'imagePath': record.image_path.replace('\\', '/'),
            'diseaseName': record.disease_name,
            'confidence': record.confidence,
            'cropName': db.session.execute(
                db.select(CropTypes.crop_name).where(
                    CropTypes.crop_type_id == record.crop_type_id
                )
            ).scalar(),
            'createTime': (record.create_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        } for record in records]
        
        return jsonify({
            'success': True,
            'records': records_list,
            'total': total,
            'hasMore': offset + len(records_list) < total  # 是否还有更多数据
        })
        
    except Exception as e:
        print('获取历史记录错误:', str(e))
        return jsonify({
            'success': False,
            'message': '服务器错误'
        }), 500

# 添加静态文件访问路由
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/api/record/detail', methods=['GET'])
def get_record_detail():
    try:
        record_id = request.args.get('record_id', type=int)
        if not record_id:
            return jsonify({
                'success': False,
                'message': '缺少记录ID'
            }), 400
            
        # 查询记录详情
        record = db.session.execute(
            db.select(RecognitionRecords).where(RecognitionRecords.record_id == record_id)
        ).scalar()
        
        if not record:
            return jsonify({
                'success': False,
                'message': '记录不存在'
            }), 404
            
        # 查询作物类型
        crop_type_info = db.session.execute(
            db.select(CropTypes).where(CropTypes.crop_type_id == record.crop_type_id)
        ).scalar()
        
        # 查询病害知识
        disease_knowledge = db.session.execute(
            db.select(DiseaseKnowledge).where(
                db.and_(
                    DiseaseKnowledge.crop_type == crop_type_info.crop_name,
                    DiseaseKnowledge.disease_name == record.disease_name
                )
            )
        ).scalar()
        
        # 返回与识别结果相同格式的数据
        return jsonify({
            'success': True,
            'data': {
                'cropInfo': {
                    'cropName': crop_type_info.crop_name,
                    'cropNameEn': crop_type_info.crop_name_en
                },
                'diseaseInfo': {
                    'diseaseName': record.disease_name,
                    'confidence': round(float(record.confidence) * 100, 2),
                    'severityLevel': record.severity_level
                },
                'solution': {
                    'symptoms': disease_knowledge.symptoms if disease_knowledge else None,
                    'solutions': disease_knowledge.solutions if disease_knowledge else None,
                    'preventionMethods': disease_knowledge.prevention_methods if disease_knowledge else None
                },
                'imagePath': record.image_path
            }
        })
        
    except Exception as e:
        print('获取记录详情错误:', str(e))
        return jsonify({
            'success': False,
            'message': '服务器错误'
        }), 500

# 添加获取作物类型接口
@app.route('/api/crop-types', methods=['GET'])
def get_crop_types():
    try:
        # 查询所有作物类型
        crop_types = db.session.execute(db.select(CropTypes)).scalars().all()
        
        # 转换为列表
        crop_types_list = [{
            'id': crop.crop_type_id,
            'name': crop.crop_name,
            'nameEn': crop.crop_name_en
        } for crop in crop_types]
        
        return jsonify({
            'success': True,
            'cropTypes': crop_types_list
        })
        
    except Exception as e:
        print('获取作物类型错误:', str(e))
        return jsonify({
            'success': False,
            'message': '服务器错误'
        }), 500

# 添加获取病害类型接口
@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    try:
        # 查询所有病害知识
        diseases = db.session.execute(db.select(DiseaseKnowledge)).scalars().all()
        
        # 转换为列表
        diseases_list = [{
            'id': disease.disease_id,
            'name': disease.disease_name,
            'nameEn': disease.disease_name_en,
            'cropType': disease.crop_type,
            'severityLevel': disease.severity_level,
            'description': disease.symptoms,  # 使用症状作为描述
            'solutions': disease.solutions,
            'preventionMethods': disease.prevention_methods
        } for disease in diseases]
        
        return jsonify({
            'success': True,
            'diseases': diseases_list
        })
        
    except Exception as e:
        print('获取病害类型错误:', str(e))
        return jsonify({
            'success': False,
            'message': '服务器错误'
        }), 500

# 添加新的数据库模型
class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PostImages(db.Model):
    image_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.comment_id', ondelete='CASCADE'))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

class Likes(db.Model):
    like_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_like'),)

# 发布帖子接口
@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        # 从表单数据中获取参数
        user_id = request.form.get('user_id')
        content = request.form.get('content', '')  # 设置默认值为空字符串
        images = request.form.get('images', '').split(',') if request.form.get('images') else []  # 处理空值
        
        print('接收到的数据:', {  # 调试用
            'user_id': user_id,
            'content': content,
            'images': images
        })
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
            
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'message': '用户ID无效'
            }), 400
            
        # 创建帖子
        post = Posts(
            user_id=user_id,
            content=content
        )
        db.session.add(post)
        db.session.flush()  # 获取post_id
        
        # 处理图片路径
        image_paths = []
        for image_path in images:
            if image_path:  # 只处理非空路径
                # 保存图片记录
                post_image = PostImages(
                    post_id=post.post_id,
                    image_path=image_path
                )
                db.session.add(post_image)
                image_paths.append(image_path)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '发布成功',
            'data': {
                'post_id': post.post_id,
                'image_paths': image_paths
            }
        })
        
    except Exception as e:
        print('发布帖子错误:', str(e))
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# 获取帖子列表接口
@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        user_id = request.args.get('user_id', type=int)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询帖子
        posts = db.session.execute(
            db.select(Posts, Users.username)
            .join(Users, Posts.user_id == Users.user_id)
            .order_by(Posts.create_time.desc())
            .offset(offset)
            .limit(page_size)
        ).all()
        
        # 转换为列表
        posts_list = []
        for post, username in posts:
            # 获取帖子的图片
            images = db.session.execute(
                db.select(PostImages.image_path)
                .where(PostImages.post_id == post.post_id)
            ).scalars().all()
            
            # 检查当前用户是否点赞
            is_liked = False
            if user_id:
                is_liked = db.session.execute(
                    db.select(Likes)
                    .where(db.and_(
                        Likes.post_id == post.post_id,
                        Likes.user_id == user_id
                    ))
                ).first() is not None
            
            posts_list.append({
                'post_id': post.post_id,
                'user_id': post.user_id,
                'username': username,
                'content': post.content,
                'images': images,
                'like_count': post.like_count,
                'comment_count': post.comment_count,
                'is_liked': is_liked,
                'create_time': (post.create_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'posts': posts_list
        })
        
    except Exception as e:
        print('获取帖子列表错误:', str(e))
        return jsonify({
            'success': False,
            'message': '获取失败'
        }), 500

# 点赞/取消点赞接口
@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        # 查询是否已点赞
        existing_like = db.session.execute(
            db.select(Likes)
            .where(db.and_(
                Likes.post_id == post_id,
                Likes.user_id == user_id
            ))
        ).scalar()
        
        if existing_like:
            # 取消点赞
            db.session.delete(existing_like)
            db.session.execute(
                db.update(Posts)
                .where(Posts.post_id == post_id)
                .values(like_count=Posts.like_count - 1)
            )
            action = '取消点赞'
        else:
            # 添加点赞
            new_like = Likes(post_id=post_id, user_id=user_id)
            db.session.add(new_like)
            db.session.execute(
                db.update(Posts)
                .where(Posts.post_id == post_id)
                .values(like_count=Posts.like_count + 1)
            )
            action = '点赞'
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{action}成功'
        })
        
    except Exception as e:
        print('点赞操作错误:', str(e))
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '操作失败'
        }), 500

# 评论接口
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        if not user_id or not content:
            return jsonify({
                'success': False,
                'message': '参数错误'
            }), 400
            
        # 创建评论
        comment = Comments(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id
        )
        db.session.add(comment)
        
        # 更新帖子评论数
        db.session.execute(
            db.update(Posts)
            .where(Posts.post_id == post_id)
            .values(comment_count=Posts.comment_count + 1)
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评论成功'
        })
        
    except Exception as e:
        print('评论错误:', str(e))
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '评论失败'
        }), 500

# 获取评论列表接口
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    try:
        # 查询评论
        comments = db.session.execute(
            db.select(Comments, Users.username)
            .join(Users, Comments.user_id == Users.user_id)
            .where(Comments.post_id == post_id)
            .order_by(Comments.create_time.desc())
        ).all()
        
        comments_list = [{
            'comment_id': comment.comment_id,
            'user_id': comment.user_id,
            'username': username,
            'content': comment.content,
            'parent_id': comment.parent_id,
            'create_time': (comment.create_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        } for comment, username in comments]
        
        return jsonify({
            'success': True,
            'comments': comments_list
        })
        
    except Exception as e:
        print('获取评论列表错误:', str(e))
        return jsonify({
            'success': False,
            'message': '获取失败'
        }), 500

# 添加文件上传接口
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有文件'
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            safe_filename = f"{timestamp}_{filename}"
            file_path = os.path.join('uploads', 'posts', safe_filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存文件
            file.save(file_path)
            
            return jsonify({
                'success': True,
                'path': file_path.replace('\\', '/')
            })
            
    except Exception as e:
        print('文件上传错误:', str(e))
        return jsonify({
            'success': False,
            'message': '上传失败'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)