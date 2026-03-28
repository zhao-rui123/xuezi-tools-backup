"""
数据验证器测试
"""

import unittest


class TestDataValidator(unittest.TestCase):
    """测试数据验证器"""
    
    def setUp(self):
        """测试前准备"""
        try:
            from openclaw.utils.validator import DataValidator, ValidationRule
            self.DataValidator = DataValidator
            self.ValidationRule = ValidationRule
        except ImportError:
            self.skipTest("数据验证器依赖未安装")
    
    def test_validator_creation(self):
        """测试验证器创建"""
        validator = self.DataValidator()
        self.assertIsNotNone(validator)
    
    def test_email_validation(self):
        """测试邮箱验证"""
        validator = self.DataValidator()
        
        self.assertTrue(validator.validate_email("test@example.com"))
        self.assertTrue(validator.validate_email("user.name@domain.co.uk"))
        self.assertFalse(validator.validate_email("invalid-email"))
        self.assertFalse(validator.validate_email(""))
    
    def test_phone_validation(self):
        """测试手机号验证"""
        validator = self.DataValidator()
        
        self.assertTrue(validator.validate_phone_cn("13800138000"))
        self.assertFalse(validator.validate_phone_cn("1380013800"))
        self.assertFalse(validator.validate_phone_cn("invalid"))
    
    def test_url_validation(self):
        """测试URL验证"""
        validator = self.DataValidator()
        
        self.assertTrue(validator.validate_url("https://www.example.com"))
        self.assertTrue(validator.validate_url("http://example.com/path"))
        self.assertFalse(validator.validate_url("not-a-url"))
    
    def test_ipv4_validation(self):
        """测试IPv4验证"""
        validator = self.DataValidator()
        
        self.assertTrue(validator.validate_ipv4("192.168.1.1"))
        self.assertTrue(validator.validate_ipv4("10.0.0.1"))
        self.assertFalse(validator.validate_ipv4("256.1.1.1"))
        self.assertFalse(validator.validate_ipv4("not-an-ip"))


class TestValidationRule(unittest.TestCase):
    """测试验证规则"""
    
    def test_rule_creation(self):
        """测试规则对象创建"""
        try:
            from openclaw.utils.validator import ValidationRule
        except ImportError:
            self.skipTest("数据验证器依赖未安装")
        
        rule = ValidationRule(
            field="email",
            rule_type="format",
            params={"format": "email"},
        )
        
        self.assertEqual(rule.field, "email")
        self.assertEqual(rule.rule_type, "format")


if __name__ == "__main__":
    unittest.main()
