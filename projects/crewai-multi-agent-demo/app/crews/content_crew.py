"""内容创作 Crew — 组装 Agent 团队并执行流水线"""

from crewai import Crew, Process

from app.agents.researcher import create_researcher
from app.agents.writer import create_writer
from app.agents.editor import create_editor
from app.agents.seo_optimizer import create_seo_optimizer
from app.tasks.content_tasks import (
    create_research_task,
    create_writing_task,
    create_editing_task,
    create_seo_task,
)


class ContentCreationCrew:
    """技术博客内容创作 Crew

__author__ = "Walter Wang"

    组装四个专业 Agent，按流水线顺序协作完成内容创作：
    研究员 → 作家 → 编辑 → SEO 优化师
    """

    def __init__(self, process: str = "sequential"):
        """初始化 Crew

        Args:
            process: 执行模式，'sequential'（顺序）或 'hierarchical'（层级）
        """
        self.process = Process.sequential if process == "sequential" else Process.hierarchical

    def kickoff(self, topic: str) -> str:
        """启动内容创作流水线

        Args:
            topic: 创作主题

        Returns:
            最终生成的文章内容
        """
        # 创建 Agent
        researcher = create_researcher()
        writer = create_writer()
        editor = create_editor()
        seo_optimizer = create_seo_optimizer()

        # 创建任务（通过 context 参数串联上下文）
        research_task = create_research_task(researcher, topic)
        writing_task = create_writing_task(writer, topic, context=[research_task])
        editing_task = create_editing_task(editor, context=[writing_task])
        seo_task = create_seo_task(seo_optimizer, topic, context=[editing_task])

        # 组装 Crew
        crew_kwargs: dict = {
            "agents": [researcher, writer, editor, seo_optimizer],
            "tasks": [research_task, writing_task, editing_task, seo_task],
            "process": self.process,
            "verbose": True,
            "memory": True,  # 启用记忆系统
        }

        # 层级模式需要指定 manager LLM
        if self.process == Process.hierarchical:
            crew_kwargs["manager_llm"] = "gpt-4o"

        crew = Crew(**crew_kwargs)

        # 执行流水线
        result = crew.kickoff()
        return str(result)
