# SMPL Body Models 下载指南

## 步骤 1: 下载 SMPL-H 模型

### 方法 A: 官方网站（推荐）
1. 访问 https://mano.is.tue.mpg.de/download.php
2. 创建账户并登录
3. 下载 **SMPL-H v1.2** (右侧的 Models 部分)
   - 选择 `SMPL+H v1.2 - SMPL-H Model`
   - 下载 ZIP 文件

### 方法 B: 直接下载链接（如果有）
如果上述网站无法访问，也可以尝试通过其他渠道获取 SMPL-H 模型文件。

## 步骤 2: 解压和配置

1. **解压下载的文件**
   ```bash
   unzip models.zip -d /path/to/your/smplh/directory
   ```

2. **目录结构应该如下**
   ```
   /path/to/your/smplh/directory/
   ├── SMPLH_FEMALE.pkl
   ├── SMPLH_MALE.pkl
   └── kid_template.npy  (后续下载)
   ```

## 步骤 3: 下载 kid_template.npy

这个文件需要从 AGORA 项目获取：

1. 访问 AGORA 项目网站
2. 找到 SMIL/SMIL-X 模板下载部分
3. 下载 `smpl_kid_template.npy`
4. 重命名为 `kid_template.npy`
5. 复制到 SMPL 目录

## 步骤 4: 更新配置

编辑 `lib_smpl/const.py`，修改 `SMPL_MODEL_ROOT`：

```python
SMPL_MODEL_ROOT="/path/to/your/smplh/directory"  # 修改为你的实际路径
```

## 最终检查

验证文件结构：
```bash
ls -la /path/to/your/smplh/directory/
# 应该输出:
# -rw-r--r-- SMPLH_FEMALE.pkl
# -rw-r--r-- SMPLH_MALE.pkl
# -rw-r--r-- kid_template.npy
```

## 验证安装

运行以下命令验证 SMPL 模型是否正确加载：
```bash
python -c "from lib_smpl import wrapper_pytorch; print('SMPL models loaded successfully!')"
```
