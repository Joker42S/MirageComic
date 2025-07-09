import numpy as np
from PIL import Image

def create_simple_phantom_tank(hidden_img):
    """
    生成幻影图
    :param hidden_img: 里图（黑底显示图像）路径或PIL图像对象
    :return: 生成的幻影坦克图像（PNG格式带透明通道）
    """
    # 图像预处理
    hidden = Image.open(hidden_img) if isinstance(hidden_img, str) else hidden_img
    hidden = hidden.convert('L')  # 转为灰度
    
    # 转换为numpy数组
    H = np.array(hidden, dtype=np.float32)  # 里图
    S = np.full_like(H, 255.0)             # 表图直接设为纯白（255）
    
    # 核心算法（简化版）
    alpha = 255 - (S - H)                  # 等价于 alpha = H
    phantom = np.clip((255 * H) / alpha, 0, 255).astype(np.uint8)  # 恒等于255
    
    # 合并通道（所有像素RGB值为255，透明度由H决定）
    result = np.dstack([
        np.full_like(phantom, 255),  # R
        np.full_like(phantom, 255),  # G
        np.full_like(phantom, 255),  # B
        alpha.astype(np.uint8)       # A
    ])
    
    return Image.fromarray(result, 'RGBA')

if __name__ == "__main__":
    hidden_img = "hidden.png"  # 只需要提供黑底显示的图
    
    result = create_simple_phantom_tank(hidden_img)
    result.save("simple_phantom.png", format="PNG")
    print("简化版幻影坦克生成完成，已保存为simple_phantom.png")