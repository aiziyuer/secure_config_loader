# Secure Config Loader

## 功能特性
- ✅ 多格式支持：YAML
- ✅ Ansible Vault 自动解密
- 🔒 密码加载优先级策略
- 📦 点分语法访问配置

## 安装
```bash
pip install secure-config-loader
```

## 快速开始
```python
from secure_config_loader import SecureConfigLoader

loader = SecureConfigLoader()
config = loader.load("config.yaml")

print(config.database.host)
```

## 配置优先级
1. 构造函数参数
2. 环境变量 `ANSIBLE_VAULT_PASSWORD`
3. 密码文件 `ANSIBLE_VAULT_PASSWORD_FILE`
4. 默认文件 `~/.vault_pass`