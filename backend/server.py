from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List
import shutil
import tempfile
from datetime import datetime, timezone

from models import (
    UserCreate, User, UserLogin, Token,
    ConferenceCreate, Conference,
    ValidationResult, DashboardStats
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)
from validation_engine import ValidationEngine

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

UPLOAD_DIR = Path("/tmp/woodtech_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    user_dict = user_data.model_dump()
    password = user_dict.pop("password")
    hashed_password = get_password_hash(password)
    
    user = User(**user_dict)
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['hashed_password'] = hashed_password
    
    await db.users.insert_one(doc)
    return user

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    user_doc = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    if not verify_password(credentials.password, user_doc.get('hashed_password', '')):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    user_doc.pop('hashed_password', None)
    user = User(**user_doc)
    
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    return Token(access_token=access_token, user=user)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if isinstance(user_doc['created_at'], str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    user_doc.pop('hashed_password', None)
    return User(**user_doc)

@api_router.post("/conferences", response_model=Conference)
async def create_conference(
    name: str = Form(...),
    description: str = Form(None),
    log2_file: UploadFile = File(...),
    log3_file: UploadFile = File(...),
    cubo_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    conference_data = ConferenceCreate(name=name, description=description)
    conference = Conference(**conference_data.model_dump(), created_by=current_user["id"])
    
    conf_dir = UPLOAD_DIR / conference.id
    conf_dir.mkdir(exist_ok=True)
    
    log2_path = conf_dir / "log2.xlsx"
    log3_path = conf_dir / "log3.xlsx"
    cubo_path = conf_dir / "cubo160.xlsx"
    
    with open(log2_path, "wb") as f:
        shutil.copyfileobj(log2_file.file, f)
    with open(log3_path, "wb") as f:
        shutil.copyfileobj(log3_file.file, f)
    with open(cubo_path, "wb") as f:
        shutil.copyfileobj(cubo_file.file, f)
    
    engine = ValidationEngine()
    try:
        log2_count = engine.load_log2(str(log2_path))
        log3_count = engine.load_log3(str(log3_path))
        cubo_count = engine.load_cubo160(str(cubo_path))
        
        results, stats = engine.validate_all()
        
        conference.log2_count = log2_count
        conference.log3_count = log3_count
        conference.cubo_count = cubo_count
        conference.total_records = stats['total_records']
        conference.matches = stats['matches']
        conference.divergences = stats['divergences']
        conference.duplicates = stats['duplicates']
        conference.status = "completed"
        
        for result in results:
            val_result = ValidationResult(
                conference_id=conference.id,
                **result
            )
            doc = val_result.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.validation_results.insert_one(doc)
        
    except Exception as e:
        conference.status = "error"
        logging.error(f"Erro ao processar conferência: {e}")
    
    doc = conference.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.conferences.insert_one(doc)
    
    return conference

@api_router.get("/conferences", response_model=List[Conference])
async def get_conferences(current_user: dict = Depends(get_current_user)):
    conferences = await db.conferences.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    for conf in conferences:
        if isinstance(conf['created_at'], str):
            conf['created_at'] = datetime.fromisoformat(conf['created_at'])
    
    return [Conference(**conf) for conf in conferences]

@api_router.get("/conferences/{conference_id}", response_model=Conference)
async def get_conference(conference_id: str, current_user: dict = Depends(get_current_user)):
    conf = await db.conferences.find_one({"id": conference_id}, {"_id": 0})
    if not conf:
        raise HTTPException(status_code=404, detail="Conferência não encontrada")
    
    if isinstance(conf['created_at'], str):
        conf['created_at'] = datetime.fromisoformat(conf['created_at'])
    
    return Conference(**conf)

@api_router.get("/conferences/{conference_id}/results", response_model=List[ValidationResult])
async def get_conference_results(
    conference_id: str,
    status_filter: str = None,
    current_user: dict = Depends(get_current_user)
):
    query = {"conference_id": conference_id}
    if status_filter:
        query["status"] = status_filter
    
    results = await db.validation_results.find(query, {"_id": 0}).to_list(10000)
    
    for result in results:
        if isinstance(result['created_at'], str):
            result['created_at'] = datetime.fromisoformat(result['created_at'])
    
    return [ValidationResult(**result) for result in results]

@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    total_conferences = await db.conferences.count_documents({})
    
    conferences = await db.conferences.find({}, {"_id": 0}).to_list(1000)
    
    total_records = sum(c.get('total_records', 0) for c in conferences)
    total_divergences = sum(c.get('divergences', 0) for c in conferences)
    total_duplicates = sum(c.get('duplicates', 0) for c in conferences)
    
    divergence_rate = (total_divergences / total_records * 100) if total_records > 0 else 0
    duplicate_rate = (total_duplicates / total_records * 100) if total_records > 0 else 0
    
    recent_conferences = await db.conferences.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    
    for conf in recent_conferences:
        if isinstance(conf['created_at'], str):
            conf['created_at'] = datetime.fromisoformat(conf['created_at'])
    
    return DashboardStats(
        total_conferences=total_conferences,
        total_records_processed=total_records,
        total_divergences=total_divergences,
        total_duplicates=total_duplicates,
        recent_conferences=[Conference(**c) for c in recent_conferences],
        divergence_rate=round(divergence_rate, 2),
        duplicate_rate=round(duplicate_rate, 2)
    )

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()