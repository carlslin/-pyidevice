"""pytest配置和fixtures"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from pyidevice.core import DeviceManager
from pyidevice.device import Device


@pytest.fixture
def mock_device_udid():
    """模拟设备UDID"""
    return "00008020-0012345678901234"


@pytest.fixture
def mock_device_info():
    """模拟设备信息"""
    return {
        'DeviceName': 'Test iPhone',
        'ProductType': 'iPhone12,1',
        'ProductVersion': '15.0',
        'BatteryLevel': 85,
        'SerialNumber': 'TEST123456789'
    }


@pytest.fixture
def mock_device_manager():
    """模拟设备管理器"""
    with patch.object(DeviceManager, 'get_devices') as mock_get_devices, \
         patch.object(DeviceManager, 'get_device_info') as mock_get_info:
        
        mock_get_devices.return_value = ["00008020-0012345678901234"]
        mock_get_info.return_value = {
            'DeviceName': 'Test iPhone',
            'ProductType': 'iPhone12,1',
            'ProductVersion': '15.0',
            'BatteryLevel': 85
        }
        
        yield DeviceManager()


@pytest.fixture
def mock_device(mock_device_udid, mock_device_info):
    """模拟设备实例"""
    with patch.object(Device, 'info') as mock_info, \
         patch.object(Device, 'install_app') as mock_install, \
         patch.object(Device, 'uninstall_app') as mock_uninstall, \
         patch.object(Device, 'take_screenshot') as mock_screenshot:
        
        mock_info.return_value = mock_device_info
        mock_install.return_value = True
        mock_uninstall.return_value = True
        mock_screenshot.return_value = True
        
        device = Device(mock_device_udid)
        yield device


@pytest.fixture
def temp_dir():
    """临时目录fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_ipa_path(temp_dir):
    """示例IPA文件路径"""
    ipa_path = os.path.join(temp_dir, "test_app.ipa")
    # 创建一个空的IPA文件用于测试
    with open(ipa_path, 'w') as f:
        f.write("fake ipa content")
    return ipa_path


@pytest.fixture(autouse=True)
def mock_subprocess():
    """自动模拟subprocess调用"""
    with patch('subprocess.check_output') as mock_check_output, \
         patch('subprocess.run') as mock_run, \
         patch('subprocess.Popen') as mock_popen:
        
        # 默认成功响应
        mock_check_output.return_value = "success"
        mock_run.return_value = Mock(returncode=0, stdout="success")
        mock_popen.return_value = Mock(
            poll=Mock(return_value=None),
            terminate=Mock(),
            wait=Mock(),
            stdout=Mock(readline=Mock(return_value=""))
        )
        
        yield {
            'check_output': mock_check_output,
            'run': mock_run,
            'popen': mock_popen
        }


@pytest.fixture
def mock_wda_client():
    """模拟WDA客户端"""
    mock_client = Mock()
    mock_session = Mock()
    mock_element = Mock()
    
    # 配置mock对象
    mock_client.session.return_value = mock_session
    mock_client.wait_ready.return_value = True
    mock_session.window_size.return_value = {'width': 375, 'height': 812}
    mock_session.screenshot.return_value.save.return_value = True
    mock_session.bundle_id = "com.test.app"
    mock_session.source = "test source"
    mock_session.contexts = ["NATIVE_APP", "WEBVIEW_com.test.app"]
    
    mock_element.click.return_value = None
    mock_element.set_text.return_value = None
    mock_element.text = "test text"
    mock_element.tap_hold.return_value = None
    
    mock_session.return_value = mock_element
    mock_session.side_effect = lambda **kwargs: mock_element
    
    return mock_client


# 标记装饰器
requires_device = pytest.mark.requires_device
requires_wda = pytest.mark.requires_wda
slow = pytest.mark.slow
integration = pytest.mark.integration
unit = pytest.mark.unit
