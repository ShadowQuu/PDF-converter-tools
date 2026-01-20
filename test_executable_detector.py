#!/usr/bin/env python3
"""
可执行文件检测器单元测试
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from executable_detector import (
    ExecutableDetector,
    detect_executable,
    get_executable_path,
    set_executable_path,
    clear_executable_path,
    get_all_executable_paths
)

class TestExecutableDetector(unittest.TestCase):
    """
    可执行文件检测器单元测试类
    """
    
    def setUp(self):
        """
        测试前设置，创建临时配置文件
        """
        self.temp_config = tempfile.mktemp(suffix='.json')
        self.detector = ExecutableDetector(config_file=self.temp_config)
    
    def tearDown(self):
        """
        测试后清理，删除临时配置文件
        """
        if os.path.exists(self.temp_config):
            os.remove(self.temp_config)
    
    def test_load_config(self):
        """
        测试加载配置文件
        """
        # 创建测试配置文件
        test_config = {'test_executable': '/usr/bin/test'}
        with open(self.temp_config, 'w') as f:
            json.dump(test_config, f)
        
        # 创建新的检测器实例，应该加载配置
        detector = ExecutableDetector(config_file=self.temp_config)
        self.assertEqual(detector.get_path('test_executable'), '/usr/bin/test')
    
    def test_save_config(self):
        """
        测试保存配置文件
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 设置路径
            self.detector.set_path('test_executable', '/usr/bin/test')
        
        # 检查配置文件是否保存
        with open(self.temp_config, 'r') as f:
            config = json.load(f)
        
        self.assertEqual(config, {'test_executable': '/usr/bin/test'})
    
    def test_get_platform_paths(self):
        """
        测试获取平台特定路径
        """
        paths = self.detector._get_platform_paths()
        
        # 检查是否包含PATH环境变量
        if 'PATH' in os.environ:
            for path in os.environ['PATH'].split(os.pathsep):
                self.assertIn(path, paths)
        
        # 检查是否包含平台特定路径
        system = os.name
        if system == 'nt':  # Windows
            self.assertIn(r'C:\Program Files\wkhtmltopdf\bin', paths)
        else:  # Unix-like
            self.assertIn('/usr/local/bin', paths)
            self.assertIn('/usr/bin', paths)
    
    @patch('subprocess.run')
    def test_detect_executable_in_path(self, mock_run):
        """
        测试检测在PATH中的可执行文件
        """
        # 模拟subprocess.run返回成功
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b'1.0.0\n'
        mock_run.return_value = mock_result
        
        # 模拟which/where命令返回路径
        which_result = MagicMock()
        which_result.returncode = 0
        which_result.stdout = b'/usr/bin/python\n'
        mock_run.side_effect = [mock_result, which_result]
        
        # 检测python可执行文件
        path = self.detector.detect('python')
        
        self.assertEqual(path, '/usr/bin/python')
        self.assertEqual(self.detector.get_path('python'), '/usr/bin/python')
    
    def test_detect_nonexistent_executable(self):
        """
        测试检测不存在的可执行文件
        """
        # 检测一个不存在的可执行文件
        path = self.detector.detect('nonexistent_executable_12345')
        
        self.assertIsNone(path)
    
    def test_set_and_get_path(self):
        """
        测试设置和获取路径
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 设置路径
            result = self.detector.set_path('test_executable', '/usr/bin/test')
            self.assertTrue(result)
        
        # 获取路径
        path = self.detector.get_path('test_executable')
        self.assertEqual(path, '/usr/bin/test')
    
    def test_set_invalid_path(self):
        """
        测试设置无效路径
        """
        # 设置一个不存在的路径
        result = self.detector.set_path('test_executable', '/nonexistent/path')
        self.assertFalse(result)
        
        # 检查路径是否未被设置
        path = self.detector.get_path('test_executable')
        self.assertIsNone(path)
    
    def test_clear_path(self):
        """
        测试清除路径
        """
        # 设置路径
        self.detector.set_path('test_executable', '/usr/bin/test')
        
        # 清除路径
        self.detector.clear_path('test_executable')
        
        # 检查路径是否已清除
        path = self.detector.get_path('test_executable')
        self.assertIsNone(path)
    
    def test_get_all_paths(self):
        """
        测试获取所有路径
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 设置多个路径
            self.detector.set_path('exec1', '/usr/bin/exec1')
            self.detector.set_path('exec2', '/usr/bin/exec2')
        
        # 获取所有路径
        all_paths = self.detector.get_all_paths()
        
        self.assertEqual(all_paths, {
            'exec1': '/usr/bin/exec1',
            'exec2': '/usr/bin/exec2'
        })
    
    def test_force_detection(self):
        """
        测试强制重新检测
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 先设置一个路径
            self.detector.set_path('test_executable', '/usr/bin/test')
        
        # 模拟检测到不同的路径
        with patch.object(self.detector, '_check_executable_version', return_value=True):
            with patch.object(self.detector, '_get_platform_paths', return_value=['/usr/local/bin']):
                with patch('os.path.exists', side_effect=[True, False]):
                    # 强制重新检测
                    path = self.detector.detect('test_executable', force=True)
                    
                    # 根据平台检查返回的路径
                    if os.name == 'nt':
                        # Windows系统，预期带.exe扩展名和反斜杠
                        expected_path = '/usr/local/bin\\test_executable.exe'
                    else:
                        # Unix-like系统，预期不带扩展名和正斜杠
                        expected_path = '/usr/local/bin/test_executable'
                    
                    # 检查是否返回了新检测到的路径
                    self.assertEqual(path, expected_path)
    
    def test_check_executable_version(self):
        """
        测试检查可执行文件版本
        """
        # 模拟成功的版本检查
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = self.detector._check_executable_version('/usr/bin/python')
            self.assertTrue(result)
        
        # 模拟失败的版本检查
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result
            
            result = self.detector._check_executable_version('/usr/bin/python')
            self.assertFalse(result)
        
        # 模拟文件不存在
        result = self.detector._check_executable_version('/nonexistent/path')
        self.assertFalse(result)

class TestGlobalFunctions(unittest.TestCase):
    """
    测试全局函数
    """
    
    def setUp(self):
        """
        测试前设置，保存原始配置文件路径
        """
        self.original_config = os.path.join(os.path.dirname(__file__), 'executable_paths.json')
        self.temp_config = tempfile.mktemp(suffix='.json')
        
        # 如果原始配置文件存在，备份它
        if os.path.exists(self.original_config):
            import shutil
            shutil.copy2(self.original_config, self.temp_config)
            os.remove(self.original_config)
    
    def tearDown(self):
        """
        测试后清理，恢复原始配置文件
        """
        # 删除测试生成的配置文件
        if os.path.exists(self.original_config):
            os.remove(self.original_config)
        
        # 恢复原始配置文件
        if os.path.exists(self.temp_config):
            import shutil
            shutil.copy2(self.temp_config, self.original_config)
            os.remove(self.temp_config)
    
    def test_global_detect_executable(self):
        """
        测试全局detect_executable函数
        """
        # 检测python可执行文件（应该存在）
        path = detect_executable('python')
        self.assertIsInstance(path, str)
        self.assertTrue(os.path.exists(path))
    
    def test_global_get_executable_path(self):
        """
        测试全局get_executable_path函数
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 先设置一个路径
            set_executable_path('test_executable', '/usr/bin/test')
        
        # 使用全局函数获取路径
        path = get_executable_path('test_executable')
        self.assertEqual(path, '/usr/bin/test')
    
    def test_global_set_executable_path(self):
        """
        测试全局set_executable_path函数
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 使用全局函数设置路径
            result = set_executable_path('test_executable', '/usr/bin/test')
            self.assertTrue(result)
        
        # 检查路径是否被设置
        path = get_executable_path('test_executable')
        self.assertEqual(path, '/usr/bin/test')
    
    def test_global_clear_executable_path(self):
        """
        测试全局clear_executable_path函数
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 先设置一个路径
            set_executable_path('test_executable', '/usr/bin/test')
        
        # 使用全局函数清除路径
        clear_executable_path('test_executable')
        
        # 检查路径是否被清除
        path = get_executable_path('test_executable')
        self.assertIsNone(path)
    
    def test_global_get_all_executable_paths(self):
        """
        测试全局get_all_executable_paths函数
        """
        # 模拟路径存在
        with patch('os.path.exists', return_value=True):
            # 先设置一些路径
            set_executable_path('exec1', '/usr/bin/exec1')
            set_executable_path('exec2', '/usr/bin/exec2')
        
        # 使用全局函数获取所有路径
        all_paths = get_all_executable_paths()
        
        self.assertIn('exec1', all_paths)
        self.assertIn('exec2', all_paths)
        self.assertEqual(all_paths['exec1'], '/usr/bin/exec1')
        self.assertEqual(all_paths['exec2'], '/usr/bin/exec2')

if __name__ == '__main__':
    """
    运行单元测试
    """
    unittest.main()
