import os
import yaml
from pathlib import Path
from ansible.constants import DEFAULT_VAULT_ID_MATCH, DEFAULT_VAULT_PASSWORD_FILE
from ansible.parsing.vault import VaultLib, VaultSecret, AnsibleVaultError
from typing import Any, Optional
from box import Box


class SecureConfigLoader:
    # 在 SecureConfigLoader 类中添加以下方法
    def _register_yaml_constructors(self):
        """注册 Ansible Vault 的 YAML 标签处理器"""
        yaml.add_constructor(
            "!vault", self._vault_yaml_constructor, Loader=yaml.SafeLoader
        )

    def _vault_yaml_constructor(self, loader: yaml.Loader, node: yaml.Node) -> str:
        """处理 !vault 标签"""
        value = loader.construct_scalar(node)
        return value  # 保持加密字符串原样返回，后续解密流程会处理

    def __init__(self, vault_password: Optional[str] = None):
        """
        Ansible 密码加载优先级（遵循官方逻辑）：
        1. 显式传入的 vault_password 参数
        2. ANSIBLE_VAULT_PASSWORD 环境变量
        3. ANSIBLE_VAULT_PASSWORD_FILE 环境变量指定的文件
        4. ansible.cfg 中定义的默认密码文件（通常 ~/.vault_pass）
        """
        self._register_yaml_constructors()  # 新增此行
        self.vault_password = self._resolve_password(vault_password)
        self.vault = VaultLib(
            [(DEFAULT_VAULT_ID_MATCH, VaultSecret(self.vault_password.encode()))]
        )

    def _resolve_password(self, password: Optional[str]) -> str:
        # 层级1：显式传入的密码
        if password:
            return password

        # 层级2：环境变量直接密码
        env_password = os.getenv("ANSIBLE_VAULT_PASSWORD")
        if env_password:
            return env_password

        # 层级3：环境变量密码文件
        password_file = os.getenv("ANSIBLE_VAULT_PASSWORD_FILE", "~/.vault_pass")
        if password_file:
            return self._read_password_file(password_file)

        raise ValueError(
            "未找到有效的 Vault 密码，请通过以下方式之一提供：\n"
            "1. 构造函数参数 vault_password\n"
            "2. ANSIBLE_VAULT_PASSWORD 环境变量\n"
            "3. ANSIBLE_VAULT_PASSWORD_FILE 环境变量\n"
            f"4. 默认密码文件 {DEFAULT_VAULT_PASSWORD_FILE}"
        )

    def _read_password_file(self, path: str) -> str:
        """安全读取密码文件"""
        try:
            with open(os.path.expanduser(path), "r") as f:
                password = f.read().strip()
                if not password:
                    raise ValueError(f"密码文件 {path} 内容为空")
                return password
        except FileNotFoundError:
            raise FileNotFoundError(f"密码文件 {path} 不存在")
        except PermissionError:
            raise PermissionError(f"无权限读取密码文件 {path}")

    def _get_loader(self, suffix: str):
        """获取对应文件格式的加载器"""
        return {
            ".yaml": self._load_yaml,
            ".yml": self._load_yaml,
        }.get(suffix.lower(), self._unsupported_format)

    def _load_yaml(self, file_obj) -> dict:
        """加载YAML文件"""
        try:
            return yaml.safe_load(file_obj) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析错误: {str(e)}") from e

    def _unsupported_format(self, _):
        raise ValueError("不支持的配置文件格式")

    def _decrypt_value(self, value: Any) -> Any:
        """递归解密并转换为 Box 对象"""
        if isinstance(value, dict):
            return Box(
                {k: self._decrypt_value(v) for k, v in value.items()},
                box_dots=True,  # 启用点分语法
            )
        elif isinstance(value, list):
            return [self._decrypt_value(item) for item in value]
        elif isinstance(value, str) and value.startswith("$ANSIBLE_VAULT"):
            try:
                return self.vault.decrypt(value).decode("utf-8")
            except AnsibleVaultError as e:
                raise ValueError(f"解密失败: {str(e)}") from e
        return value

    def load(self, file_path: str) -> Box:  # 修改返回类型
        config_file = Path(file_path)

        if not config_file.exists():
            raise FileNotFoundError(f"配置文件 {file_path} 不存在")

        # 根据扩展名选择加载器
        loader = self._get_loader(config_file.suffix)
        with config_file.open() as f:
            raw_config = loader(f)

        return self._decrypt_value(raw_config)


if __name__ == "__main__":

    # 或硬编码密码（仅用于测试）
    loader = SecureConfigLoader()

    config = loader.load("env_dev.yaml")
    print("数据库配置:", config.get("mysql.password", 123))
