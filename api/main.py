from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import os
import logging
import stripe
from alipay import AliPay
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.auth import verify_password, get_password_hash, create_access_token

from core.config import settings
from core.intent import ArtIntent
from core.plan import Compiler
from core.runtime import Runtime
from backends.mock import MockBackend
from db.session import SessionLocal, init_db
from db.models import AgentExecution, ExecutionStatus, UserAccount, PaymentTransaction, UserRole, AuditLog
from core.exporter import Exporter
from core.worker import run_agent_task_celery

# 初始化数据库
init_db()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("artfish.api")

# Stripe 初始化
stripe.api_key = settings.STRIPE_API_KEY

# 支付宝初始化 (保留插件代码)
alipay_client = None
alipay_config_errors = []

def init_alipay():
    global alipay_client, alipay_config_errors
    alipay_config_errors = []
    
    if not settings.ALIPAY_APP_ID:
        alipay_config_errors.append("Missing ALIPAY_APP_ID")
    if not settings.ALIPAY_PRIVATE_KEY:
        alipay_config_errors.append("Missing ALIPAY_PRIVATE_KEY")
    if not settings.ALIPAY_PUBLIC_KEY:
        alipay_config_errors.append("Missing ALIPAY_PUBLIC_KEY")
        
    if not alipay_config_errors:
        try:
            alipay_client = AliPay(
                appid=settings.ALIPAY_APP_ID,
                app_notify_url=None,
                app_private_key_string=settings.ALIPAY_PRIVATE_KEY,
                alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY,
                sign_type="RSA2",
                debug=settings.ALIPAY_DEBUG
            )
            logger.info("Alipay configuration detected and client initialized.")
            return True
        except Exception as e:
            error_msg = f"Alipay initialization failed: {e}"
            logger.error(error_msg)
            alipay_config_errors.append(error_msg)
            return False
    return False

alipay_status = init_alipay()

# 初始化速率限制器
limiter = Limiter(key_func=get_remote_address)

import secrets
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # 简单 CSRF 校验逻辑
            csrf_token_cookie = request.cookies.get("csrf_token")
            csrf_token_header = request.headers.get("X-CSRF-Token")
            
            if not csrf_token_cookie or csrf_token_cookie != csrf_token_header:
                # 即使在 DEBUG 模式下也记录警告，但不阻塞请求
                if not settings.DEBUG:
                    logger.warning(f"CSRF check failed: cookie={csrf_token_cookie}, header={csrf_token_header}")
                    return JSONResponse(
                        status_code=403, 
                        content={"detail": "Security validation failed (CSRF). Please refresh the page and try again."}
                    )
                else:
                    logger.debug("CSRF check failed in DEBUG mode, allowing request.")
        
        response = await call_next(request)
        
        # 为响应设置新的 CSRF Cookie
        if not request.cookies.get("csrf_token"):
            response.set_cookie(
                key="csrf_token", 
                value=secrets.token_urlsafe(32), 
                httponly=False, # 前端需要读取这个值设置到 Header
                samesite="strict",
                secure=not settings.DEBUG
            )
        return response

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
app.add_middleware(CSRFMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "message": str(exc) if settings.DEBUG else "Please contact support"}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database connection error"}
    )

# 安全中间件：强制 HTTPS (生产环境建议开启)
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)

# 安全中间件：信任主机
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] # 生产环境应指定具体域名
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://abwoo.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 安全配置
API_KEY_NAME = "X-API-Key"
GUEST_ID_NAME = "X-Guest-ID"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
guest_id_header = APIKeyHeader(name=GUEST_ID_NAME, auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    api_key: str = Security(api_key_header),
    guest_id: str = Security(guest_id_header),
    token_query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # 1. 优先支持 API Key
    if api_key:
        user = db.query(UserAccount).filter(UserAccount.api_key_hash == api_key).first()
        if user and user.is_active:
            return user

    # 2. 支持 Guest ID (匿名付费模式核心)
    if guest_id:
        user = db.query(UserAccount).filter(UserAccount.user_id == guest_id).first()
        if not user:
            # 自动创建匿名账户
            logger.info(f"Creating auto-account for Guest: {guest_id}")
            user = UserAccount(
                user_id=guest_id,
                email=f"guest_{guest_id[:8]}@artfish.ai",
                balance=1.0, # 初始赠送 1 USD 体验金
                role=UserRole.USER,
                is_active=1
            )
            # 如果 Guest ID 匹配配置的管理员邮箱（作为特殊 Key），授予管理员权限
            if guest_id == settings.SUPER_ADMIN_EMAIL:
                user.role = UserRole.ADMIN
                user.balance = 99999.0
                
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if user.is_active:
            return user

    # 3. 兼容 JWT Token
    final_token = token or token_query
    if final_token:
        try:
            payload = jwt.decode(final_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
        if user and user.is_active:
            return user

    # 如果都没有，尝试创建/返回演示账号 (开发环境)
    if db.query(UserAccount).count() == 0:
        user = UserAccount(
            user_id="test_user", 
            email="test@artfish.ai",
            hashed_password=get_password_hash("test123456"),
            api_key_hash="sk-artfish-test-key", 
            balance=100.0,
            stripe_customer_id="cus_test_123"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    raise HTTPException(status_code=401, detail="Not authenticated")

# 数据模型
class UserRegister(BaseModel):
    email: str
    password: str
    user_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class IntentRequest(BaseModel):
    goals: List[str]
    constraints: Dict[str, Any] = {}
    user_id: str
    priority: int = 0
    backend_config: Optional[Dict[str, Any]] = None

class ExecutionResponse(BaseModel):
    run_id: str
    status: str
    message: str

# --- 辅助函数与中间件 ---

def log_audit(db: Session, user_id: str, action: str, details: Dict[str, Any], request: Request):
    """记录审计日志"""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=request.client.host if request.client else "unknown"
    )
    db.add(audit)
    db.commit()

async def get_admin_user(current_user: UserAccount = Depends(get_current_user)):
    """仅允许管理员访问"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# --- API 路由 ---

@app.post("/v1/auth/register", response_model=Token)
@limiter.limit("30/minute") # 提升限速以方便测试
async def register(request: Request, user_in: UserRegister, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user: {user_in.email}")
    # 检查邮箱是否已存在
    if db.query(UserAccount).filter(UserAccount.email == user_in.email).first():
        logger.warning(f"Registration failed: Email {user_in.email} already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        user_id = user_in.user_id or str(uuid.uuid4())[:8]
        api_key = f"sk-artfish-{uuid.uuid4().hex[:12]}"
        
        user = UserAccount(
        user_id=user_id,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        api_key_hash=api_key,
        role=UserRole.USER, # 强制为普通用户
        balance=10.0
    )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        log_audit(db, user.user_id, "register", {"email": user.email}, request)
        logger.info(f"User registered successfully: {user.email}")
        
        access_token = create_access_token(data={"sub": user.user_id, "role": user.role.value})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Registration error for {user_in.email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/v1/auth/token", response_model=Token)
@limiter.limit("10/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for: {form_data.username}")
    
    # 检查是否为配置的超级管理员
    user = db.query(UserAccount).filter(UserAccount.email == form_data.username).first()
    
    # 如果是超级管理员邮箱且用户不存在，自动初始化（仅在首次登录时）
    if form_data.username == settings.SUPER_ADMIN_EMAIL and not user:
        logger.info(f"Initializing super admin: {settings.SUPER_ADMIN_EMAIL}")
        user = UserAccount(
            user_id="admin",
            email=settings.SUPER_ADMIN_EMAIL,
            hashed_password=get_password_hash("Admin123!@#"), # 初始默认密码，建议通过 DB 修改
            role=UserRole.ADMIN,
            balance=99999.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    log_audit(db, user.user_id, "login", {}, request)
    
    access_token = create_access_token(data={"sub": user.user_id, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"} # nosec B105

# --- 充值与计费接口 ---

@app.post("/v1/user/topup")
async def user_topup(
    amount: float, 
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """用户自助充值 (模拟)"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    current_user.balance += amount
    db.commit()
    db.refresh(current_user)
    
    log_audit(db, current_user.user_id, "topup", {"amount": amount}, request=None)
    return {"message": "Top-up successful", "new_balance": current_user.balance}

@app.post("/v1/admin/recharge")
async def admin_recharge(
    target_user_id: str,
    amount: float,
    db: Session = Depends(get_db),
    admin: UserAccount = Depends(get_admin_user)
):
    """管理员给用户手动充值"""
    user = db.query(UserAccount).filter(UserAccount.user_id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.balance += amount
    db.commit()
    db.refresh(user)
    
    log_audit(db, admin.user_id, "admin_recharge", {"target": target_user_id, "amount": amount}, request=None)
    return {"message": f"Successfully recharged {target_user_id}", "new_balance": user.balance}

# --- 管理员接口 ---

@app.get("/v1/admin/users")
async def admin_list_users(
    page: int = 1, 
    limit: int = 20, 
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: UserAccount = Depends(get_admin_user)
):
    query = db.query(UserAccount)
    if search:
        query = query.filter(UserAccount.email.contains(search) | UserAccount.user_id.contains(search))
    
    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "users": [
            {
                "id": u.id,
                "user_id": u.user_id,
                "email": u.email,
                "role": u.role.value,
                "balance": u.balance,
                "is_active": u.is_active,
                "created_at": u.created_at
            } for u in users
        ]
    }

@app.patch("/v1/admin/user/{user_id}/status")
async def admin_update_user_status(
    user_id: str, 
    active: bool, 
    request: Request,
    db: Session = Depends(get_db),
    admin: UserAccount = Depends(get_admin_user)
):
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = 1 if active else 0
    db.commit()
    
    log_audit(db, admin.user_id, "update_user_status", {"target": user_id, "active": active}, request)
    return {"status": "success"}

@app.get("/v1/admin/stats")
async def admin_get_stats(
    db: Session = Depends(get_db),
    admin: UserAccount = Depends(get_admin_user)
):
    user_count = db.query(UserAccount).count()
    execution_count = db.query(AgentExecution).count()
    total_revenue = db.query(UserAccount).with_entities(UserAccount.total_spent).all()
    revenue = sum(r[0] for r in total_revenue)
    
    # 获取最近 7 天注册趋势
    # 简化实现
    
    return {
        "total_users": user_count,
        "total_executions": execution_count,
        "total_revenue": revenue,
        "system_status": "healthy"
    }

import csv
import io
from fastapi.responses import StreamingResponse

@app.get("/v1/admin/users/export")
async def admin_export_users(
    db: Session = Depends(get_db),
    admin: UserAccount = Depends(get_admin_user)
):
    users = db.query(UserAccount).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "User ID", "Email", "Role", "Balance", "Is Active", "Created At"])
    
    for u in users:
        writer.writerow([u.id, u.user_id, u.email, u.role.value, u.balance, u.is_active, u.created_at])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )

@app.delete("/v1/admin/user/{user_id}")
async def admin_delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    admin: UserAccount = Depends(get_admin_user)
):
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 级联删除在模型中已配置 (cascade="all, delete-orphan")
    # 但由于 UserAccount 没有直接关联 AgentExecution (是通过 user_id 字符串关联的)
    # 我们需要手动删除相关的 AgentExecution
    executions = db.query(AgentExecution).filter(AgentExecution.user_id == user_id).all()
    for ex in executions:
        db.delete(ex)
        
    db.delete(user)
    db.commit()
    
    log_audit(db, admin.user_id, "delete_user", {"target": user_id}, request)
    return {"status": "success", "message": f"User {user_id} and all related data deleted."}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "alipay_configured": alipay_status,
        "alipay_errors": alipay_config_errors
    }

@app.get("/v1/user/me")
async def get_user_info(user: UserAccount = Depends(get_current_user)):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "balance": user.balance,
        "total_spent": user.total_spent,
        "api_key": user.api_key_hash, # 方便前端展示给用户
        "status": "active" if user.is_active else "disabled"
    }

@app.post("/v1/execute", response_model=ExecutionResponse)
async def execute_intent(
    request: IntentRequest, 
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.balance <= 0:
        raise HTTPException(status_code=402, detail="Insufficient balance")

    run_id = str(uuid.uuid4())
    try:
        execution = AgentExecution(
            run_id=run_id,
            user_id=user.user_id,
            status=ExecutionStatus.PENDING,
            intent_snapshot=request.model_dump(),
            start_time=None
        )
        db.add(execution)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e

    # 提交 Celery 任务
    run_agent_task_celery.delay(run_id, request.model_dump())
    
    return {
        "run_id": run_id,
        "status": "accepted",
        "message": "Task has been queued in Celery worker."
    }

@app.get("/v1/execution/{run_id}")
async def get_execution_status(
    run_id: str, 
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    execution = db.query(AgentExecution).filter(AgentExecution.run_id == run_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return {
        "run_id": execution.run_id,
        "status": execution.status.value,
        "total_cost": execution.total_cost,
        "start_time": execution.start_time,
        "end_time": execution.end_time,
        "actions_count": len(execution.actions)
    }

@app.get("/v1/execution/{run_id}/report")
async def download_report(
    run_id: str, 
    type: str = "pdf", 
    token: Optional[str] = None, # 明确声明接收 token query
    db: Session = Depends(get_db)
):
    # 这里我们手动调用 get_current_user 或者直接在 Depends 中处理
    user = await get_current_user(token_query=token, db=db)
    
    execution = db.query(AgentExecution).filter(AgentExecution.run_id == run_id).first()
    if not execution or execution.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Execution not found")

    ext = "pdf" if type == "pdf" else "json"
    prefix = "report" if type == "pdf" else "trace"
    file_path = os.path.join(settings.EXPORT_DIR, f"{prefix}_{run_id}.{ext}")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not ready")
    
    return FileResponse(file_path, filename=f"artfish_{run_id}.{ext}")

# --- 支付接口保留 (暂不接入流程) ---

@app.post("/v1/payments/stripe/create-checkout-session")
async def create_stripe_checkout_session(amount: float, user: UserAccount = Depends(get_current_user)):
    # 逻辑保留但前端暂不调用
    pass

@app.post("/v1/payments/alipay/create-order")
async def create_alipay_order(amount: float, user: UserAccount = Depends(get_current_user)):
    # 逻辑保留但前端暂不调用
    pass

if __name__ == "__main__":
    import uvicorn
    # 生产环境建议通过环境变量配置 HOST
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=8000) # nosec B104
