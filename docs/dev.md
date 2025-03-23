### 版本管理

```
# 安装工具
pip install bumpversion

# 配置 .bumpversion.cfg
[bumpversion]
current_version = 0.1.0
commit = True
tag = True

# 升级版本号示例
bumpversion patch  # 0.1.0 → 0.1.1
bumpversion minor  # 0.1.1 → 0.2.0
```

### 打包发布

```
# 安装构建工具
pip install build twine

# 生成发布包
python -m build

# 上传到PyPI测试库
twine upload --repository testpypi dist/*

# 验证无误后上传正式库
twine upload dist/*
```