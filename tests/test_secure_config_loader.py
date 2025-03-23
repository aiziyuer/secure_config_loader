import unittest
from unittest.mock import patch, mock_open
from src.secure_config_loader.core import SecureConfigLoader, AnsibleVaultError


class TestSecureConfigLoader(unittest.TestCase):

    def setUp(self):
        self.vault_password = "Changeme_123"
        self.loader = SecureConfigLoader(vault_password=self.vault_password)

    @patch("secure_config_loader.core.VaultLib")
    def test_value(self, mock_vault_lib):
        input = "test_value"
        ouput = self.loader.decrypt_value(self.loader.encrypt_value(input))

        self.assertEqual(
            input,
            ouput,
        )

    @patch("secure_config_loader.core.VaultLib")
    def test_decrypt_value(self, mock_vault_lib):
        mock_vault_instance = mock_vault_lib.return_value
        mock_vault_instance.decrypt.return_value = b"test_value"
        decrypted_value = self.loader.decrypt_value("$ANSIBLE_VAULT123")
        self.assertEqual(decrypted_value, "test_value")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='mysql:\n  password: "$ANSIBLE_VAULT123"',
    )
    @patch("secure_config_loader.core.VaultLib")
    def test_load(self, mock_vault_lib, mock_file):
        mock_vault_instance = mock_vault_lib.return_value
        mock_vault_instance.decrypt.return_value = b"test_password"
        config = self.loader.load("env_dev.yaml")
        self.assertEqual(config.mysql.password, "test_password")


if __name__ == "__main__":
    unittest.main()
