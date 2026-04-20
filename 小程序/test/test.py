import torch
import torchvision
from torch import nn
from torchvision.transforms import transforms
from PIL import Image
import os

# 定义完整的61个类别映射
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

def load_model(model_path, device):
    """加载训练好的模型"""
    # 创建模型
    model = torchvision.models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 61)  # 修改为61个类别
    
    # 加载模型权重（添加 map_location 参数）
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    return model

def predict_image(model, image_path, device):
    """预测单张图片的疾病类别"""
    # 图像预处理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])
    
    # 加载并处理图片
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # 预测
    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
        
        # 获取预测概率
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence = probabilities[0][predicted[0]].item()
        
    return predicted.item(), confidence

def main():
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # 加载模型
    model_path = r"C:\Users\93368\Desktop\test\wheal-condition-identify-master\models\best_model_loss_0.4179_acc_0.8518.pth"
    
    try:
        print(f"Loading model from: {model_path}")
        model = load_model(model_path, device).to(device)  # 传入 device 参数
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # 修改为新的测试图片目录
    test_image_dir = r"C:\Users\93368\Desktop\test\images"
    
    if not os.path.exists(test_image_dir):
        print(f"Error: Test directory not found: {test_image_dir}")
        return
        
    # 获取前10张图片
    image_files = [f for f in os.listdir(test_image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))][:10]
    print(f"\n预测目录中的前10张图片:")
    print("="*50)
    
    # 记录结果
    results = []
    
    # 预测前10张图片
    for i, image_name in enumerate(image_files, 1):
        image_path = os.path.join(test_image_dir, image_name)
        print(f"\n图片 {i}/10: {image_name}")
        
        try:
            # 预测
            predicted_class, confidence = predict_image(model, image_path, device)
            
            # 输出结果（添加序号）
            print(f"预测序号: {predicted_class}")
            print(f"预测类别: {disease_classes[predicted_class]}")
            print(f"置信度: {confidence*100:.2f}%")
            
            results.append({
                'image': image_name,
                'class_id': predicted_class,  # 添加序号
                'prediction': disease_classes[predicted_class],
                'confidence': confidence
            })
            
        except Exception as e:
            print(f"处理图片出错 {image_name}: {e}")
            continue
    
    # 保存结果到文件
    output_dir = os.path.dirname(model_path)
    result_file = os.path.join(output_dir, 'prediction_results_10.txt')
    
    print(f"\n保存结果到: {result_file}")
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("前10张图片预测结果\n")
        f.write("="*50 + "\n")
        f.write(f"模型路径: {model_path}\n")
        f.write(f"测试图片目录: {test_image_dir}\n\n")
        
        for result in results:
            f.write(f"图片: {result['image']}\n")
            f.write(f"预测序号: {result['class_id']}\n")  # 添加序号
            f.write(f"预测类别: {result['prediction']}\n")
            f.write(f"置信度: {result['confidence']*100:.2f}%\n")
            f.write("-"*30 + "\n")
    
    print("\n预测完成!")
    print(f"结果已保存到: {result_file}")

if __name__ == "__main__":
    main()