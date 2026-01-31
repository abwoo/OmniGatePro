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
from core.auth import verify_password, get_password_hash, create_access_token

from core.config import settings
from core.intent import ArtIntent
from core.plan import Compiler
from core.runtime import Runtime
from backends.mock import MockBackend
from db.session import SessionLocal, init_db
from db.models import AgentExecution, ExecutionStatus, UserAccount, PaymentTransaction
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

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

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

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    api_key: str = Security(api_key_header),
    token_query: Optional[str] = None, # 增加从 Query 参数获取 Token 的支持
    db: Session = Depends(get_db)
):
    # 1. 优先支持 API Key (用于开发者/机器人)
    if api_key:
        user = db.query(UserAccount).filter(UserAccount.api_key_hash == api_key).first()
        if user and user.is_active:
            return user

    # 2. 其次支持 JWT Token (Authorization Header 或 Query Parameter)
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

# --- API 路由 ---

@app.post("/v1/auth/register", response_model=Token)
async def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    if db.query(UserAccount).filter(UserAccount.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = user_in.user_id or str(uuid.uuid4())[:8]
    api_key = f"sk-artfish-{uuid.uuid4().hex[:12]}"
    
    user = UserAccount(
        user_id=user_id,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        api_key_hash=api_key,
        balance=10.0 # 注册送 10 刀
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/v1/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserAccount).filter(UserAccount.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
