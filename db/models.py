from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ExecutionStatus(PyEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

class AgentExecution(Base):
    """
    Top-level execution record: Represents a complete Agent run task.
    """
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    
    # Store snapshot of original intent and plan
    intent_snapshot = Column(JSON, nullable=False)
    plan_snapshot = Column(JSON)
    
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    # Relationships
    actions = relationship("ActionTrace", back_populates="execution", cascade="all, delete-orphan")

class ActionTrace(Base):
    """
    Operation record: Represents an AtomicAction in the execution plan.
    """
    __tablename__ = "action_traces"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    
    action_id = Column(String(64), nullable=False)
    action_type = Column(String(32), index=True)
    
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    
    # Data snapshot
    input_params = Column(JSON)
    output_payload = Column(JSON)
    error_message = Column(Text)
    
    duration_ms = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)

    execution = relationship("AgentExecution", back_populates="actions")
