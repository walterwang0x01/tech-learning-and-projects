"""Crew 组装测试"""

from unittest.mock import patch, MagicMock

from app.agents.researcher import create_researcher
from app.agents.writer import create_writer
from app.agents.editor import create_editor
from app.agents.seo_optimizer import create_seo_optimizer
from app.crews.content_crew import ContentCreationCrew
from app.tasks.content_tasks import (
    create_research_task,
    create_writing_task,
    create_editing_task,
    create_seo_task,
)


class TestAgentCreation:
    """Agent 创建测试"""

__author__ = "Walter Wang"

    @patch("app.agents.researcher.SerperDevTool")
    @patch("app.agents.researcher.ScrapeWebsiteTool")
    def test_create_researcher(self, mock_scrape, mock_serper):
        """测试研究员 Agent 创建"""
        mock_serper.return_value = MagicMock()
        mock_scrape.return_value = MagicMock()
        agent = create_researcher()
        assert agent.role == "高级研究员"
        assert len(agent.tools) == 2

    def test_create_writer(self):
        """测试作家 Agent 创建"""
        agent = create_writer()
        assert agent.role == "技术作家"
        assert len(agent.tools) == 2

    def test_create_editor(self):
        """测试编辑 Agent 创建"""
        agent = create_editor()
        assert agent.role == "内容编辑"
        assert len(agent.tools) == 0

    @patch("app.agents.seo_optimizer.SerperDevTool")
    def test_create_seo_optimizer(self, mock_serper):
        """测试 SEO 优化师 Agent 创建"""
        mock_serper.return_value = MagicMock()
        agent = create_seo_optimizer()
        assert agent.role == "SEO 优化师"
        assert len(agent.tools) == 2


class TestTaskCreation:
    """任务创建测试"""

    def test_create_research_task(self, sample_topic: str):
        """测试研究任务创建"""
        mock_agent = MagicMock()
        task = create_research_task(mock_agent, sample_topic)
        assert sample_topic in task.description
        assert task.agent == mock_agent

    def test_create_writing_task(self, sample_topic: str):
        """测试写作任务创建"""
        mock_agent = MagicMock()
        mock_context = [MagicMock()]
        task = create_writing_task(mock_agent, sample_topic, context=mock_context)
        assert sample_topic in task.description
        assert task.context == mock_context

    def test_create_editing_task(self):
        """测试编辑任务创建"""
        mock_agent = MagicMock()
        mock_context = [MagicMock()]
        task = create_editing_task(mock_agent, context=mock_context)
        assert "审校" in task.description
        assert task.context == mock_context

    def test_create_seo_task(self, sample_topic: str):
        """测试 SEO 任务创建"""
        mock_agent = MagicMock()
        mock_context = [MagicMock()]
        task = create_seo_task(mock_agent, sample_topic, context=mock_context)
        assert sample_topic in task.description
        assert task.context == mock_context


class TestContentCreationCrew:
    """Crew 组装测试"""

    def test_crew_init_sequential(self):
        """测试顺序模式初始化"""
        from crewai import Process

        crew = ContentCreationCrew(process="sequential")
        assert crew.process == Process.sequential

    def test_crew_init_hierarchical(self):
        """测试层级模式初始化"""
        from crewai import Process

        crew = ContentCreationCrew(process="hierarchical")
        assert crew.process == Process.hierarchical
