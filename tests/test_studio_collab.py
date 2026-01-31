import pytest
from core.gateway import StudioGateway
from core.intent import ArtIntent
from core.trace import ActionStatus

@pytest.fixture
def gateway():
    return StudioGateway()

def test_project_creation_and_agent_joining(gateway):
    # 1. 创建艺术项目
    project_id = gateway.create_project(
        title="星空下的咖啡馆",
        description="一幅具有强烈对比色彩的后印象派风格习作"
    )
    assert len(project_id) == 8
    
    # 2. Agent 加入项目
    gateway.join_agent(project_id, "agent_tutor_01", "tutor")
    gateway.join_agent(project_id, "agent_artist_01", "artist")
    
    assert len(gateway._active_projects[project_id]["agents"]) == 2

def test_multi_agent_collaboration_flow(gateway):
    project_id = gateway.create_project("色彩习作", "探索冷色调的艺术表现力")
    
    # 场景：Tutor 提供理论 -> Artist 接收并计划 -> Critic 进行点评
    
    # Step 1: Tutor 提供色彩建议
    tutor_intent = ArtIntent(goals=["获取适合忧郁氛围的配色方案"], constraints={"skill": "art_tutor"})
    trace1 = gateway.execute_collaborative_task(project_id, "agent_tutor", tutor_intent)
    assert any("art_tutor" in str(event.metadata.get("skill")) for event in trace1.events)

    # Step 2: Critic 进行审美点评
    critique_intent = ArtIntent(
        goals=["对当前冷色调构思进行评审"], 
        constraints={"query": "使用了深蓝和墨绿的组合"}
    )
    trace2 = gateway.execute_collaborative_task(project_id, "agent_critic", critique_intent)
    results2 = trace2.get_all_results()
    
    # 验证网关是否正确路由到了鉴赏技能（即使意图中没有显式指定）
    assert any("art_critique" in str(event.metadata.get("skill")) for event in trace2.events)

def test_studio_collab_skills(gateway):
    # 验证协作技能工具
    res = gateway.skill_manager.execute(
        "studio_collab", "handoff_task", 
        task_id="paint_01", target_role="critic", context={"layer": "background"}
    )
    assert "成功转交给角色 [critic]" in res
