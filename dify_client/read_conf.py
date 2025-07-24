from pathlib import Path
from configparser import ConfigParser


conf_path = Path(__file__).parent / "config.conf"   # 或任意绝对路径
cfg = ConfigParser()
cfg.read(conf_path, encoding="utf-8")


hw_dify_api_base_url = cfg.get('dify_hanwei_api', 'hw_dify_api_base_url')