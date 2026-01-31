from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Text, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ExecutionStatus(PyEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

class AgentExecution(Base):
    """
    顶级执行记录：代表一次完整的 Agent 运行任务。
    """
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(64), index=True)
    
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    
    # 存储原始意图和计划的快照
    intent_snapshot = Column(JSON, nullable=False)
    plan_snapshot = Column(JSON)
    
    total_cost = Column(Float, default=0.0)
    
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    # 关联
    actions = relationship("ActionTrace", back_populates="execution", cascade="all, delete-orphan")

class ActionTrace(Base):
    """
    操作记录：代表执行计划中的一个 AtomicAction。
    """
    __tablename__ = "action_traces"

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    
    action_id = Column(String(64), nullable=False)
    action_type = Column(String(32), index=True)
    
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    
    # 数据快照
    input_params = Column(JSON)
    output_payload = Column(JSON)
    error_message = Column(Text)
    
    cost = Column(Float, default=0.0)
    duration_ms = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)

    execution = relationship("AgentExecution", back_populates="actions")

class UserAccount(Base):
    """
    商业化：用户账户模型，管理余额和 API 权限。
    """
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True)
    hashed_password = Column(String(128))
    api_key_hash = Column(String(128), unique=True, index=True)
    
    stripe_customer_id = Column(String(128), unique=True, index=True)
    
    balance = Column(Float, default=10.0)  # 默认赠送 10 USD
    total_spent = Column(Float, default=0.0)
    
    is_active = Column(Integer, default=1)
    
    # 2FA Support
    is_2fa_enabled = Column(Integer, default=0)
    totp_secret = Column(String(32), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class PaymentTransaction(Base):
    """
    支付流水记录。
    """
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), ForeignKey("user_accounts.user_id"), nullable=False)
    stripe_session_id = Column(String(128), unique=True)
    amount = Column(Float, nullable=False)
    status = Column(String(32))  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
