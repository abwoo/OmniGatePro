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

# --- Infrastructure Models (Inspired by mature systems) ---

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

# --- Education Vertical Models (New) ---

class Student(Base):
    """
    用户画像系统：记录学习行为与核心能力维度
    """
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    grade = Column(String(20), nullable=False) # e.g., "Grade 7"
    
    # 个人学习力评估 (注意力/记忆力/逻辑力)
    attention_score = Column(Float, default=0.0)
    memory_score = Column(Float, default=0.0)
    logic_score = Column(Float, default=0.0)
    
    mastery_records = relationship("MasteryMatrix", back_populates="student")
    error_logs = relationship("ErrorLog", back_populates="student")

class KnowledgePoint(Base):
    """
    教材知识点图谱：细化到章节级别
    """
    __tablename__ = "knowledge_points"
    id = Column(Integer, primary_key=True)
    subject = Column(String(50), nullable=False) # 语数外/理化生...
    chapter = Column(String(200)) # 章节名称
    title = Column(String(200), nullable=False) # 知识点名称
    content = Column(Text) # 核心定义/公式
    difficulty_level = Column(Integer, default=1) # 1-5

class MasteryMatrix(Base):
    """
    知识点掌握度矩阵：实时更新
    """
    __tablename__ = "mastery_matrix"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    kp_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    mastery_level = Column(Float, default=0.0) # 0.0 - 1.0
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    student = relationship("Student", back_populates="mastery_records")
    kp = relationship("KnowledgePoint")

class ErrorLog(Base):
    """
    错题关联的知识漏洞追踪
    """
    __tablename__ = "error_logs"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    kp_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    
    error_type = Column(String(50)) # 计算错误/逻辑错误/知识模糊
    wrong_answer = Column(Text)
    correct_answer = Column(Text)
    context = Column(Text) # 题目背景
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    student = relationship("Student", back_populates="error_logs")
    kp = relationship("KnowledgePoint")
