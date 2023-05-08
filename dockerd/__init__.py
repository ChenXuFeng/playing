'''
Time       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   docker client
'''


from pathlib import Path

from django.conf import settings
from docker.client import DockerClient
from docker.tls import TLSConfig

__all__ = ('dockerd',)


def _sertificaters(path: Path) -> dict:
    return {
        'ca_cert': path / 'ca.pem',
        'client_cert': (path / 'cert.pem', path / 'key.pem'),
        'verify': True
    }


def _dockerd_url(conf: dict) -> str:
    return f"tcp://{conf['host']}:{conf['port']}"


def _remote_docker(setting: dict):
    tls_config = TLSConfig(
        **_sertificaters(setting['sertificaters'])
    )
    try:
        dockerd = DockerClient(base_url=_dockerd_url(setting), tls=tls_config)
        return dockerd
    except Exception:
        raise Exception('docker服务器连接失败')


def dockerd_factory():
    """从配置文件或本地配置Docker client"""
    setting = hasattr(settings, 'DOCKERD')
    if not setting:
        return DockerClient.from_env()
    setting = settings.DOCKERD
    return _remote_docker(setting)


dockerd = dockerd_factory()
