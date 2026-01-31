from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ExecutionStatus(PyEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

# --- Infrastructure Models ---

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    id = Column(Integer, primary_key=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    intent_snapshot = Column(JSON, nullable=False)
    plan_snapshot = Column(JSON)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime)
    actions = relationship("ActionTrace", back_populates="execution", cascade="all, delete-orphan")

class ActionTrace(Base):
    __tablename__ = "action_traces"
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    action_id = Column(String(64), nullable=False)
    action_type = Column(String(32), index=True)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    input_params = Column(JSON)
    output_payload = Column(JSON)
    error_message = Column(Text)
    duration_ms = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime)
    execution = relationship("AgentExecution", back_populates="actions")

# --- Art Studio Collaboration Models (New) ---

class ArtProject(Base):
    """
    艺术项目：多个 Agent 协作的载体
    """
    __tablename__ = "art_projects"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="concept") # concept, creation, review, finished
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    
    sessions = relationship("ArtSession", back_populates="project")

class ArtSession(Base):
    """
    协作会话：记录 Agent 间的交互与共享上下文
    """
    __tablename__ = "art_sessions"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("art_projects.id"), nullable=False)
    
    shared_context = Column(JSON) # 存储当前画布状态、配色方案等
    interaction_history = Column(JSON) # 记录 Agent 间的对话
    
    project = relationship("ArtProject", back_populates="sessions")
    agent_logs = relationship("AgentCollabLog", back_populates="session")

class AgentRole(PyEnum):
    STUDENT = "student"
    TUTOR = "tutor"
    ARTIST = "artist"
    CRITIC = "critic"

class AgentCollabLog(Base):
    """
    Agent 协作日志：记录自主交互行为
    """
    __tablename__ = "agent_collab_logs"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("art_sessions.id"), nullable=False)
    
    from_agent = Column(String(100)) # Agent 标识
    from_role = Column(Enum(AgentRole))
    to_agent = Column(String(100))
    to_role = Column(Enum(AgentRole))
    
    action_type = Column(String(50)) # e.g., "request_feedback", "handoff_canvas", "propose_style"
    content = Column(Text)
    payload = Column(JSON)
    
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    session = relationship("ArtSession", back_populates="agent_logs")
