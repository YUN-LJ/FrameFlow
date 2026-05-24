"""
任务链监控工具 - 可视化和调试任务依赖关系
"""
import json
import time
from typing import Dict, List
from Fun.BaseTools.TaskClass import Task
from Fun.BaseTools import LogClass

logger = LogClass.get_logger(__name__, console_level='WARNING')


class TaskChainMonitor:
    """
    任务链监控器

    功能:
    - 记录任务依赖关系
    - 生成任务链路图
    - 性能分析
    """

    def __init__(self):
        self.task_graph: Dict[str, dict] = {}
        self.performance_data: Dict[str, float] = {}

    def register_task(self, task: Task, parent: Task = None):
        """注册任务及其依赖关系"""
        task_id = id(task)
        parent_id = id(parent) if parent else None

        self.task_graph[str(task_id)] = {
            'name': task.name,
            'class': task.__class__.__name__,
            'parent': str(parent_id) if parent_id else None,
            'children': [],
            'state': 'created',
            'start_time': None,
            'end_time': None
        }

        if parent_id:
            parent_key = str(parent_id)
            if parent_key in self.task_graph:
                self.task_graph[parent_key]['children'].append(str(task_id))

        # 监听任务状态变化
        task.start_signal.connect(lambda t: self._on_task_start(t))
        task.finish_signal.connect(lambda t: self._on_task_finish(t))
        task.stop_signal.connect(lambda t: self._on_task_stop(t))

    def _on_task_start(self, task: Task):
        """任务开始回调"""
        task_id = str(id(task))
        if task_id in self.task_graph:
            self.task_graph[task_id]['state'] = 'running'
            self.task_graph[task_id]['start_time'] = time.time()

    def _on_task_finish(self, task: Task):
        """任务完成回调"""
        task_id = str(id(task))
        if task_id in self.task_graph:
            self.task_graph[task_id]['state'] = 'finished'
            self.task_graph[task_id]['end_time'] = time.time()

            # 计算耗时
            start = self.task_graph[task_id]['start_time']
            end = self.task_graph[task_id]['end_time']
            if start and end:
                self.performance_data[task.name] = end - start

    def _on_task_stop(self, task: Task):
        """任务停止回调"""
        task_id = str(id(task))
        if task_id in self.task_graph:
            self.task_graph[task_id]['state'] = 'stopped'

    def generate_mermaid_diagram(self) -> str:
        """生成Mermaid流程图"""
        lines = ["graph TD"]

        for task_id, info in self.task_graph.items():
            label = f"{info['name']}\\n({info['state']})"
            lines.append(f'    {task_id}["{label}"]')

            if info['parent']:
                lines.append(f'    {info["parent"]} --> {task_id}')

        return '\n'.join(lines)

    def export_to_json(self, filepath: str):
        """导出任务图到JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'task_graph': self.task_graph,
                'performance': self.performance_data
            }, f, indent=2, ensure_ascii=False)

    def get_performance_report(self) -> str:
        """生成性能报告"""
        report = ["=== 任务性能报告 ===\n"]

        sorted_tasks = sorted(
            self.performance_data.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for task_name, duration in sorted_tasks[:10]:
            report.append(f"{task_name}: {duration:.3f}s")

        return '\n'.join(report)

    def clear(self):
        """清空监控数据"""
        self.task_graph.clear()
        self.performance_data.clear()


# 全局监控实例
TASK_MONITOR = TaskChainMonitor()