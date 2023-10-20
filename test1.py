# import torch.nn as nn

# # 创建一个 nn.Conv1d 的实例
# conv1d_layer = nn.Conv1d(in_channels=4, out_channels=128, kernel_size=5)

# # 假设有一个形状为 (batch_size, in_channels, sequence_length) 的输入
# # batch_size = 16, in_channels = 4, sequence_length = 100
# # 输入数据的形状应该与 in_channels 匹配


# input_data = torch.randn(4, 4,5)  # 创建一个随机张量来模拟输入数据


# output_data = conv1d_layer(input_data)  # 通过卷积层传递输入数据
# print(output_data.shape)

# import torch.nn as nn
# import torch

# flatten_layer = nn.Flatten()

# # 假设 x 是一个形状为 [batch_size, channels, height, width] 的张量
# x = torch.randn(2, 1, 1)

# print(x)
# # 执行 flatten 操作
# x_flatten = flatten_layer(x)
# print(x_flatten)


import torch
import torch.nn as nn
import torch.nn.functional as F

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=3, out_channels=128, kernel_size=5)
        self.fc1 = nn.Linear(128 * 6, 64)  # 假设输入序列长度为100，经过卷积层后，序列长度变为96
        self.fc2 = nn.Linear(64, 10)  # 假设我们有10个类别

    def forward(self, x):
        x = F.relu(self.conv1(x))
        
        x = x.view(x.size(0), -1)  # 执行 flatten 操作
        print(x .shape)
        # print(x.shape)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 创建网络实例
model = SimpleCNN()

# 假设输入数据形状为 (batch_size, in_channels, sequence_length)
# batch_size = 16, in_channels = 4, sequence_length = 100
input_data = torch.randn(1, 3, 10)

print(input_data)
# 将输入数据传递通过网络
output_data = model(input_data)


