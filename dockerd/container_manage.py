'''
Date       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   容器管理程序,超时关闭
'''

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from threading import Lock, Timer

from django.conf import settings
from django.utils import timezone

from common.singletons import Singleton
from dockerd import dockerd
from practices.models import DockerContainers

__all__ = ('ContainerManage',)

logger = logging.getLogger("django.server")


class ContainerManage(metaclass=Singleton):
    """容器管理"""

    def __init__(self):
        self.timeout = settings.DOCKERD['container_timeout'] if hasattr(settings, 'DOCKERD') else 120
        # self.timeout = 10 # debug 容器最多存活10分钟
        self.timers = {}
        self.worker = ThreadPoolExecutor(3)
        self._worker = []
        self.count = 0
        self.stop = False

    @staticmethod
    def stop_container(dcid: int):
        dc = DockerContainers.objects.get(pk=dcid)
        c = dockerd.containers.get(dc.name)
        c.stop()
        # c.reload()
        dc.status = 2
        dc.save()
        logger.info(f'container {dc.name} stopped')

    def time_remaining(self, container) -> int:
        end = container.create_at + timedelta(minutes=self.timeout)
        now = timezone.localtime(timezone.now())
        if now >= end:
            return 0
        remaining = end - now
        return remaining.total_seconds()

    def find(self):
        logger.info(f'{self.__class__.__name__}.find is worker!')
        logger.info(f'container timeout: {self.timeout}')
        while not self.stop:
            with Lock():
                managed = self.timers.keys()
            started = DockerContainers.objects.exclude(id__in=managed)
            started = started.filter(status=0)
            logger.info(f'started count: {started.count()}')
            for std in started:
                time_remaining = self.time_remaining(std)
                job = Timer(time_remaining or 5.0, self.stop_container, [std.id])
                job.start()
                with Lock():
                    if job.is_alive():
                        self.timers.update({std.id: job})
            time.sleep(5)

    def clearup(self):
        logger.info(f'{self.__class__.__name__}.clearup is worker!')
        while not self.stop:
            _doen = []
            with Lock():
                for k, v in self.timers.items():
                    if not v.is_alive():
                        _doen.append(k)
                for d in _doen:
                    self.timers.pop(d)
            time.sleep(5)

    def start(self):
        logger.info('CM Start...')
        self._worker.append(self.worker.submit(self.find))
        self._worker.append(self.worker.submit(self.clearup))
        while not self.stop:
            logger.info(f'The currently managed container：{len(self.timers)}')
            time.sleep(5)

    def stoped(self):
        self.stop = True
        logger.info('stop ...')
        time.sleep(5)
        [c for c in as_completed(self._worker)]
        self.worker.shutdown()
        for _, v in self.timers.items():
            v.cancel()
        logger.info('CM Stop!!!')
