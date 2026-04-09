# Comfyui-Banana - ComfyUI Gemini Image Generator

![Banana Logo](./logo.jpg)

> 为 ComfyUI 提供 Nano Banana 图像生成能力的自定义节点

## 简介

Banana 是一个强大的 ComfyUI 自定义节点，集成了 Google NanoBanana 的图像生成 API。支持文本到图像、图像到图像等多种生成模式，让你在 ComfyUI 工作流中轻松使用最新的 AI 图像生成技术。

期待能和更多志同道合的设计人、电商人、AI 实践者们交个朋友，一起把 AI 设计玩明白！

## 功能特性

- 🎨 **多模态输入** - 支持纯文本、文本+图像混合提示词
- 🔢 **批量生成** - 一次生成最多 8 张图像
- 📐 **多种比例** - 支持 1:1、16:9、9:16、21:9 等多种宽高比
- 🎲 **种子控制** - 精确控制生成结果的随机性
- 🔄 **智能重试** - 内置指数退避重试机制，提高成功率
- ⚡ **并发处理** - 多线程并发生成，提升效率
- 🎯 **错误提示** - 失败时生成可视化错误提示图像
- 🌈 **彩色日志** - 线程安全的彩色日志系统，支持进度条

> **关于批量/并发抽卡的小提示**  
> 节点支持一次最多生成 8 张图像，方便你快速“抽卡”拿到满意结果。但需要注意：在高并发/大批量（尤其是 8 张）的情况下，Google 官方有一定概率返回 `finishReason=NO_IMAGE` 的响应——即 **API 调用请求成功且会正常计费，但本次响应体中不包含任何图片**。这属于模型/服务端的行为，不是节点丢图。实测经验建议：  
> - 常规使用时将 `batch_size` 控制在 **1-4 张** 以内，兼顾效率与稳定性；  
> - 仅在明确接受“偶尔不返图但仍计费”的情况下再尝试 8 张高并发抽卡。

## 安装

### 方法 1：手动安装
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/AgentOpen/comfyui-banana.git
```

## 配置

### 1. 创建配置文件
在插件目录下手动创建 `config.ini` 文件（或直接编辑提供的 `config.ini` 示例）并填入以下内容：

```ini
[gemini]
# 你的 API Key
api_key = YOUR_API_KEY_HERE

# 最大并发工作线程数（建议 4-8，主要影响本地 CPU 解码/处理并发）
max_workers = 4

# 网络并发上限（同时发起的网络请求数量，范围 1-8）
# - 网络稳定/内网环境：建议 4
# - 网络不稳定/代理/VPN/转发服务商：建议 2-3
network_workers_cap = 4

# Keep-Alive 超时时间（已不再用于连接管理，可忽略）
keepalive_timeout = 30
```

### 2. 填写 API Key
编辑 `config.ini` 文件中的 `api_key` 字段，填入你的实际 API Key。

### 3. 获取 API Key
可以通过[https://aigc.oagi.com.cn](https://aigc.oagi.com.cn) 渠道获取 NanoBanana API Key，具体方式请参考相关文档。

## 使用方法

1. 在 ComfyUI 中添加 "comfyui-Banana" 节点
2. 配置节点参数（见下方参数说明）
3. 连接其他节点并运行工作流

### 基础示例
```text
文本提示词 → Banana → 预览图像 → 保存图像
```

### 图生图示例
```text
加载图像 → Banana → 预览图像
         ↗  (image_1 输入)
文本提示词
```

## 参数说明

### 必需参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| **prompt** | STRING | "Peace and love" | 文本提示词，支持多行输入 |
| **api_key** | STRING | "" | Gemini API Key（留空则从配置文件读取） |
| **model_type** | SELECT | gemini-2.5-flash-image | 固定选项：gemini-2.5-flash-image / gemini-3-pro-image-preview |
| **batch_size** | INT | 1 | 批量生成数量（1-8） |
| **aspect_ratio** | STRING | Auto | 宽高比（Auto/1:1/9:16/16:9/21:9/2:3/3:2/3:4/4:3/4:5/5:4） |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| **seed** | INT | -1 | 随机种子（-1 为随机，0-102400 为固定） |
| **top_p** | FLOAT | 0.95 | 采样参数，控制生成多样性（0.0-1.0） |
| **image_size** | SELECT | 2K | 仅 gemini-3-pro-image* 生效，可选 1K/2K/4K |
| **禁用SSL验证** | BOOLEAN | False | 禁用提高成功率，但流量被第三人劫持状况下可能泄露密钥 |
| **image_1~5** | IMAGE | - | 可选的参考图像输入（最多 5 张） |

> **提示：** 仅在可信的代理/内网环境中才建议打开“禁用SSL验证”，否则存在被中间人窃取 API Key 的风险。

## 输出

节点返回一个包含生成图像的张量（TENSOR），可以连接到：

- 图像预览节点
- 图像保存节点
- 其他图像处理节点

## 高级功能

### 并发控制
在 `config.ini` 中可以配置两类并发相关参数：
- `max_workers`：本地 CPU 侧的解码/处理并发度
  - **低端设备**：2-4
  - **中端设备**：4-8
  - **高端设备**：8+
- `network_workers_cap`：网络并发上限（同时发起的网络请求数量，范围 1-8）
  - 网络稳定/内网服务：建议 4
  - 网络不稳定/代理/VPN/转发服务商：建议 2-3（降低请求雪崩概率）

### 错误处理
当生成失败时，节点会：
1. 自动重试（最多 3 次，指数退避）
2. 如果所有重试都失败，返回包含错误信息的可视化图像
3. 在控制台输出详细的错误日志

## 开发

### 项目结构
```
comfyui-banana/
├── __init__.py                    # 节点注册入口
├── Gemini_Imagen_Generator.py      # 主节点实现
├── api_client.py                   # API 客户端
├── config_manager.py               # 配置管理
├── image_codec.py                  # 图像编解码
├── logger.py                       # 日志系统
├── task_runner.py                  # 任务运行器
├── config.ini                      # 配置文件（需自行创建）
├── pyproject.toml                  # 项目依赖配置
├── LICENSE                          # 开源协议
├── README.md                        # 本文档
```

### 依赖库
- PyTorch
- NumPy
- Pillow
- requests
- configparser

## 注意事项

1. **API Key 安全**：
   - ⚠️ **绝不要**将包含真实 API Key 的 `config.ini` 或含有 apikey 的工作流公开泄露

2. **费用控制**：
   - 每次生成都会消耗 API 额度
   - 建议设置合理的 `batch_size` 避免过度消耗

3. **性能优化**：
   - 批量生成时会使用多线程并发
   - 根据机器性能调整 `max_workers`

## 故障排除

### 问题：无法加载节点
**解决方案**：
- 检查 ComfyUI 日志输出
- 确认所有依赖库已正确安装
- 重启 ComfyUI

### 问题：API 请求失败
**解决方案**：
- 检查 API Key 是否正确
- 验证网络连接
- 检查账户余额是否充足

### 问题：生成速度慢
**解决方案**：
- 降低 `batch_size`
- 调整 `max_workers` 参数
- 检查网络延迟

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 致谢

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - 强大的 Stable Diffusion GUI
- [Github](https://github.com/) - 广大公开代码借鉴项目
- 所有贡献者和使用者

---

⭐ **如果这个项目对你有帮助，请给个 Star！**  
