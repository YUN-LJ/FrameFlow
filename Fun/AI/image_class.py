import os
import json
import numpy as np
from PIL import Image
import torch
from torchvision import transforms, models
import joblib

# ----------------------
# 1. 加载保存的模型组件
# ----------------------
# 定义保存目录（与训练时的save_dir一致）
save_dir = "saved_models"

# 加载设备（CPU/GPU）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1.1 加载特征提取器（ResNet50的卷积部分）
model = models.resnet50(pretrained=False)  # 不加载预训练权重，用我们保存的
feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])  # 去除最后一层全连接
# 加载保存的权重
feature_extractor.load_state_dict(
    torch.load(os.path.join(save_dir, "feature_extractor_weights.pth"), map_location=device)
)
feature_extractor = feature_extractor.to(device)
feature_extractor.eval()  # 进入推理模式，固定权重

# 1.2 加载特征标准化器
scaler = joblib.load(os.path.join(save_dir, "feature_scaler.pkl"))

# 1.3 加载SVM分类器
clf = joblib.load(os.path.join(save_dir, "svm_classifier.pkl"))

# 1.4 加载标签映射（数字标签→类别名称）
with open(os.path.join(save_dir, "label_mapping.json"), "r") as f:
    label_dict_inv = json.load(f)
# JSON加载后键是字符串，转为整数（如"0"→0）
label_dict_inv = {int(k): v for k, v in label_dict_inv.items()}


# ----------------------
# 2. 定义预测函数
# ----------------------
def predict_new_image(image_path):
    """
    预测单张新照片的类别
    image_path: 新照片的路径（如"test_photo.jpg"）
    return: 预测的类别名称和概率
    """
    # 2.1 图像预处理（必须与训练时完全一致！）
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # 缩放为224x224
        transforms.ToTensor(),  # 转为Tensor（0-1）
        transforms.Normalize(  # 用ImageNet的均值和标准差标准化
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # 2.2 加载并处理图像
    try:
        # 打开图像并转为RGB（避免灰度图或其他模式导致的维度问题）
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return f"图像加载失败：{str(e)}", 0.0

    # 应用预处理，并增加批次维度（模型要求输入是[batch_size, 3, 224, 224]）
    image_tensor = transform(image).unsqueeze(0)  # 形状变为(1, 3, 224, 224)
    image_tensor = image_tensor.to(device)  # 移到对应设备

    # 2.3 提取特征
    with torch.no_grad():  # 关闭梯度计算，加速推理
        # 特征提取器输出形状：(1, 2048, 1, 1)
        features = feature_extractor(image_tensor)
        # 展平为一维向量：(1, 2048)
        features_flat = features.view(features.size(0), -1)
        # 转为numpy数组（移到CPU）
        features_np = features_flat.cpu().numpy()

    # 2.4 特征标准化（用训练时的scaler）
    features_scaled = scaler.transform(features_np)

    # 2.5 分类器预测
    pred_label = clf.predict(features_scaled)[0]  # 预测的数字标签
    pred_prob = clf.predict_proba(features_scaled)[0][pred_label]  # 预测概率
    pred_class = label_dict_inv[pred_label]  # 转换为类别名称

    return pred_class, pred_prob


# ----------------------
# 3. 预测新照片示例
# ----------------------
if __name__ == "__main__":
    from Fun.Norm import file
    path = 'test/无分类'
    images_path = file.get_files_path(path,only_file=True)
    count = 0
    for new_image_path in images_path:
        # 替换为你的新照片路径
        # new_image_path = r"test\无分类\Sally Dorasnow 2025-05-13\横屏\9oxpkd.jpg"  # 例如：一张猫的照片

        # 预测
        class_name, probability = predict_new_image(new_image_path)

        # 输出结果
        print(f"照片路径：{new_image_path}")
        print(f"预测类别：{class_name}")
        if class_name == '限制级':
            count += 1
        # print(f"预测概率：{probability:.2f}（{probability * 100:.1f}%）")

    # print(f'准确度:{count/len(images_path):.2f}')