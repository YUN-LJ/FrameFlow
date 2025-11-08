import os
import numpy as np
from PIL import Image, ImageFile
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import torch
from torchvision import transforms, models
from torch.utils.data import Dataset, DataLoader
import joblib  # 用于保存sklearn模型

# 允许加载截断的图片文件
ImageFile.LOAD_TRUNCATED_IMAGES = True


# ----------------------
# 1. 定义数据集加载类
# ----------------------
class CustomImageDataset(Dataset):
    def __init__(self, image_dir, label_dict, transform=None):
        self.image_dir = image_dir
        self.label_dict = label_dict
        self.transform = transform
        self.images = []
        self.labels = []

        for class_name, label in label_dict.items():
            class_dir = os.path.join(image_dir, class_name)
            for img_name in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_name)
                self.images.append(img_path)
                self.labels.append(label)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label


# ----------------------
# 2. 配置参数与数据加载
# ----------------------
# 数据集路径与类别（根据实际情况修改）
image_dir = "data"  # 数据集根目录（子文件夹为类别）
label_dict = {"正常级": 0, "粗略级": 1, "限制级": 2}  # 类别到数字标签的映射
label_dict_inv = {v: k for k, v in label_dict.items()}  # 数字标签到类别的反向映射

# 图像预处理（与预训练模型要求一致）
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 加载数据集并划分训练/测试集
dataset = CustomImageDataset(image_dir, label_dict, transform)
train_dataset, test_dataset = train_test_split(
    dataset, test_size=0.2, random_state=42, stratify=dataset.labels
)

# 数据加载器
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# ----------------------
# 3. 加载预训练CNN作为特征提取器
# ----------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet50(pretrained=True)
feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])  # 去除最后一层全连接
feature_extractor = feature_extractor.to(device)
feature_extractor.eval()  # 冻结权重，仅用于特征提取


# ----------------------
# 4. 提取图像特征
# ----------------------
def extract_features(data_loader, feature_extractor, device):
    features = []
    labels = []
    with torch.no_grad():
        for images, lbls in data_loader:
            images = images.to(device)
            feat = feature_extractor(images)
            feat = feat.view(feat.size(0), -1)  # 展平为一维向量
            features.append(feat.cpu().numpy())
            labels.append(lbls.numpy())
    return np.concatenate(features, axis=0), np.concatenate(labels, axis=0)


# 提取训练集和测试集特征
X_train, y_train = extract_features(train_loader, feature_extractor, device)
X_test, y_test = extract_features(test_loader, feature_extractor, device)

# ----------------------
# 5. 训练sklearn分类器（SVM）
# ----------------------
# 特征标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 训练SVM分类器
clf = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
clf.fit(X_train_scaled, y_train)

# 评估模型
y_pred = clf.predict(X_test_scaled)
print(f"测试集准确率：{accuracy_score(y_test, y_pred):.4f}")

# ----------------------
# 6. 模型保存（核心新增部分）
# ----------------------
# 创建保存目录（若不存在）
save_dir = "saved_models"
os.makedirs(save_dir, exist_ok=True)

# 保存特征提取器权重（PyTorch模型）
torch.save(
    feature_extractor.state_dict(),
    os.path.join(save_dir, "feature_extractor_weights.pth")
)

# 保存标准化器（sklearn的scaler）
joblib.dump(
    scaler,
    os.path.join(save_dir, "feature_scaler.pkl")
)

# 保存分类器（sklearn的SVM）
joblib.dump(
    clf,
    os.path.join(save_dir, "svm_classifier.pkl")
)

# 可选：保存标签映射（方便后续预测时使用）
import json

with open(os.path.join(save_dir, "label_mapping.json"), "w") as f:
    json.dump(label_dict_inv, f)  # 保存{数字标签:类别名称}的映射

print(f"模型已保存至 {save_dir} 目录")
