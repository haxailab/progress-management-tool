from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
import shutil

from database import engine, get_db, Base
from models import User, Project, Issue, Comment, WikiPage, File, Milestone, Category, IssueStatus, IssuePriority, IssueDependency, ProjectMember, ProjectJoinRequest, JoinRequestStatus
from schemas import (
    User as UserSchema, UserCreate, UserUpdate, PasswordReset,
    Token, LoginRequest,
    Project as ProjectSchema, ProjectCreate, ProjectUpdate,
    Issue as IssueSchema, IssueCreate, IssueUpdate,
    Comment as CommentSchema, CommentCreate, CommentUpdate,
    WikiPage as WikiPageSchema, WikiPageCreate, WikiPageUpdate,
    File as FileSchema, FileCreate,
    Milestone as MilestoneSchema, MilestoneCreate, MilestoneUpdate,
    Category as CategorySchema, CategoryCreate, CategoryUpdate,
    IssueDependency as IssueDependencySchema, IssueDependencyCreate,
    DashboardStats,
    ProjectMember as ProjectMemberSchema, ProjectMemberCreate,
    JoinRequest as JoinRequestSchema, JoinRequestCreate, JoinRequestUpdate
)
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# データベース初期化
Base.metadata.create_all(bind=engine)

# マイグレーション実行
try:
    from migrate_db import migrate
    migrate()
except Exception as e:
    print(f"Migration warning: {e}")

app = FastAPI(title="プロジェクト管理システム")

# CORS設定
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ファイルアップロード用ディレクトリ
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_NAME = os.getenv("DEFAULT_ADMIN_NAME", "Administrator")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "changeme-admin-password")
CREATE_DEMO_DATA = os.getenv("CREATE_DEMO_DATA", "true").lower() in {"1", "true", "yes", "on"}

# 初期データ作成
def init_db(db: Session):
    # 管理者ユーザーが存在しない場合は作成
    admin = db.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=DEFAULT_ADMIN_EMAIL,
            username=DEFAULT_ADMIN_USERNAME,
            full_name=DEFAULT_ADMIN_NAME,
            hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    if not CREATE_DEMO_DATA:
        return

    existing_project = db.query(Project).filter(Project.owner_id == admin.id).first()
    if existing_project:
        return

    # サンプルプロジェクト1: Webアプリケーション開発
    project1 = Project(
        name="ECサイトリニューアル",
        key="EC",
        description="既存のECサイトを最新技術でフルリニューアル。UX改善とパフォーマンス向上が目標。",
        owner_id=admin.id,
        created_at=datetime.utcnow() - timedelta(days=60),
        updated_at=datetime.utcnow() - timedelta(hours=2)
    )
    db.add(project1)
    db.commit()
    db.refresh(project1)

    db.add(ProjectMember(project_id=project1.id, user_id=admin.id, role="owner"))

    milestone1 = Milestone(
        project_id=project1.id,
        name="フェーズ1: 設計",
        description="要件定義とUI/UX設計",
        start_date=(datetime.now() - timedelta(days=30)).date(),
        due_date=(datetime.now() + timedelta(days=10)).date()
    )
    db.add(milestone1)
    db.commit()
    db.refresh(milestone1)

    category1 = Category(project_id=project1.id, name="フロントエンド", color="#3b82f6")
    category2 = Category(project_id=project1.id, name="バックエンド", color="#10b981")
    db.add_all([category1, category2])
    db.commit()

    # 課題を追加
    issues1 = [
        Issue(
            project_id=project1.id, issue_number=1, title="トップページのデザイン作成",
            description="新しいトップページのデザインを作成する", status=IssueStatus.DONE,
            priority=IssuePriority.HIGH, creator_id=admin.id, assignee_id=admin.id,
            category_id=category1.id, milestone_id=milestone1.id,
            start_date=(datetime.now() - timedelta(days=20)).date(),
            due_date=(datetime.now() - timedelta(days=15)).date(), progress=100
        ),
        Issue(
            project_id=project1.id, issue_number=2, title="商品一覧ページのAPI実装",
            description="商品一覧取得APIを実装", status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.HIGH, creator_id=admin.id, assignee_id=admin.id,
            category_id=category2.id, milestone_id=milestone1.id,
            start_date=(datetime.now() - timedelta(days=10)).date(),
            due_date=(datetime.now() + timedelta(days=5)).date(), progress=60
        ),
        Issue(
            project_id=project1.id, issue_number=3, title="決済システムの統合",
            description="新しい決済サービスとの連携", status=IssueStatus.TODO,
            priority=IssuePriority.CRITICAL, creator_id=admin.id,
            category_id=category2.id, milestone_id=milestone1.id,
            start_date=(datetime.now() + timedelta(days=5)).date(),
            due_date=(datetime.now() + timedelta(days=15)).date(), progress=0
        ),
    ]
    db.add_all(issues1)

    # サンプルプロジェクト2: モバイルアプリ開発
    project2 = Project(
        name="フィールド業務アプリ",
        key="APP",
        description="外出先での作業記録と顧客対応を効率化するモバイルアプリケーション。",
        owner_id=admin.id,
        created_at=datetime.utcnow() - timedelta(days=45),
        updated_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add(project2)
    db.commit()
    db.refresh(project2)

    db.add(ProjectMember(project_id=project2.id, user_id=admin.id, role="owner"))

    milestone2 = Milestone(
        project_id=project2.id,
        name="MVP開発",
        description="最小限の機能でリリース",
        start_date=(datetime.now() - timedelta(days=20)).date(),
        due_date=(datetime.now() + timedelta(days=20)).date()
    )
    db.add(milestone2)
    db.commit()
    db.refresh(milestone2)

    category3 = Category(project_id=project2.id, name="UI実装", color="#f59e0b")
    category4 = Category(project_id=project2.id, name="API", color="#8b5cf6")
    db.add_all([category3, category4])
    db.commit()

    issues2 = [
        Issue(
            project_id=project2.id, issue_number=1, title="ログイン画面の実装",
            description="認証機能を含むログイン画面", status=IssueStatus.DONE,
            priority=IssuePriority.HIGH, creator_id=admin.id, assignee_id=admin.id,
            category_id=category3.id, milestone_id=milestone2.id,
            start_date=(datetime.now() - timedelta(days=15)).date(),
            due_date=(datetime.now() - timedelta(days=10)).date(), progress=100
        ),
        Issue(
            project_id=project2.id, issue_number=2, title="顧客一覧画面の実装",
            description="顧客リストの表示と検索機能", status=IssueStatus.REVIEW,
            priority=IssuePriority.NORMAL, creator_id=admin.id, assignee_id=admin.id,
            category_id=category3.id, milestone_id=milestone2.id,
            start_date=(datetime.now() - timedelta(days=8)).date(),
            due_date=(datetime.now() + timedelta(days=2)).date(), progress=90
        ),
    ]
    db.add_all(issues2)

    # サンプルプロジェクト3: インフラ構築（古いプロジェクト）
    project3 = Project(
        name="クラウド移行プロジェクト",
        key="CLOUD",
        description="オンプレミス環境からクラウド基盤への移行。コスト削減と可用性向上を実現。",
        owner_id=admin.id,
        created_at=datetime.utcnow() - timedelta(days=90),
        updated_at=datetime.utcnow() - timedelta(days=30)
    )
    db.add(project3)
    db.commit()
    db.refresh(project3)

    db.add(ProjectMember(project_id=project3.id, user_id=admin.id, role="owner"))

    milestone3 = Milestone(
        project_id=project3.id,
        name="フェーズ1: 検証環境構築",
        description="開発・ステージング環境の構築",
        start_date=(datetime.now() - timedelta(days=60)).date(),
        due_date=(datetime.now() - timedelta(days=20)).date()
    )
    db.add(milestone3)
    db.commit()
    db.refresh(milestone3)

    category5 = Category(project_id=project3.id, name="インフラ", color="#ef4444")
    db.add(category5)
    db.commit()

    issues3 = [
        Issue(
            project_id=project3.id, issue_number=1, title="VPCの設計と構築",
            description="ネットワーク構成の設計", status=IssueStatus.DONE,
            priority=IssuePriority.HIGH, creator_id=admin.id, assignee_id=admin.id,
            category_id=category5.id, milestone_id=milestone3.id,
            start_date=(datetime.now() - timedelta(days=60)).date(),
            due_date=(datetime.now() - timedelta(days=50)).date(), progress=100
        ),
    ]
    db.add_all(issues3)

    # サンプルプロジェクト4: データ分析基盤
    project4 = Project(
        name="データ分析基盤構築",
        key="DATA",
        description="ビジネスインテリジェンスのためのデータウェアハウスとBIツールの導入。",
        owner_id=admin.id,
        created_at=datetime.utcnow() - timedelta(days=30),
        updated_at=datetime.utcnow()
    )
    db.add(project4)
    db.commit()
    db.refresh(project4)

    db.add(ProjectMember(project_id=project4.id, user_id=admin.id, role="owner"))

    milestone4 = Milestone(
        project_id=project4.id,
        name="PoC完了",
        description="概念実証の完了",
        start_date=datetime.now().date(),
        due_date=(datetime.now() + timedelta(days=30)).date()
    )
    db.add(milestone4)
    db.commit()
    db.refresh(milestone4)

    category6 = Category(project_id=project4.id, name="データエンジニアリング", color="#06b6d4")
    db.add(category6)
    db.commit()

    issues4 = [
        Issue(
            project_id=project4.id, issue_number=1, title="データソースの調査",
            description="既存システムからのデータ抽出方法を調査", status=IssueStatus.IN_PROGRESS,
            priority=IssuePriority.HIGH, creator_id=admin.id, assignee_id=admin.id,
            category_id=category6.id, milestone_id=milestone4.id,
            start_date=(datetime.now() - timedelta(days=5)).date(),
            due_date=(datetime.now() + timedelta(days=10)).date(), progress=40
        ),
        Issue(
            project_id=project4.id, issue_number=2, title="ETLパイプラインの設計",
            description="データ変換処理の設計", status=IssueStatus.TODO,
            priority=IssuePriority.NORMAL, creator_id=admin.id,
            category_id=category6.id, milestone_id=milestone4.id,
            start_date=(datetime.now() + timedelta(days=10)).date(),
            due_date=(datetime.now() + timedelta(days=25)).date(), progress=0
        ),
    ]
    db.add_all(issues4)

    db.commit()
    print("Created 4 sample projects")

# 起動時に初期データ作成
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    init_db(db)
    db.close()

# ===== 認証エンドポイント =====

@app.post("/api/auth/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # メールアドレス重複チェック
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")

    # ユーザー名重複チェック
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="このユーザー名は既に使用されています")

    # 新規ユーザー作成
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# ===== ユーザーエンドポイント =====

@app.get("/api/users", response_model=List[UserSchema])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(User).all()

@app.get("/api/users/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user

@app.put("/api/users/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 管理者または本人のみ編集可能
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="このユーザーを編集する権限がありません")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    # 更新
    update_data = user_update.dict(exclude_unset=True)

    # パスワード更新の場合はハッシュ化
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    # メールアドレス重複チェック
    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="このメールアドレスは既に使用されています")

    # ユーザー名重複チェック
    if "username" in update_data:
        existing_user = db.query(User).filter(
            User.username == update_data["username"],
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="このユーザー名は既に使用されています")

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 管理者のみ削除可能
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="ユーザーを削除する権限がありません")

    # 自分自身は削除できない
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="自分自身を削除することはできません")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    db.delete(user)
    db.commit()
    return {"message": "ユーザーを削除しました"}

@app.post("/api/users/{user_id}/reset-password", response_model=UserSchema)
def reset_password(
    user_id: int,
    password_reset: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 管理者のみパスワードリセット可能
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="パスワードをリセットする権限がありません")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    user.hashed_password = get_password_hash(password_reset.new_password)
    db.commit()
    db.refresh(user)
    return user

# ===== プロジェクトエンドポイント =====

@app.get("/api/projects", response_model=List[ProjectSchema])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 自分が参加しているプロジェクトのみ取得（更新日時の降順）
    member_project_ids = [m.project_id for m in db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()]

    if member_project_ids:
        return db.query(Project).filter(
            Project.id.in_(member_project_ids)
        ).order_by(Project.updated_at.desc()).all()
    else:
        # 参加しているプロジェクトがない場合は空のリストを返す
        return []

@app.get("/api/projects/all")
def list_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 全プロジェクトを取得（更新日時の降順）
    all_projects = db.query(Project).order_by(Project.updated_at.desc()).all()

    # 自分が参加しているプロジェクトのIDを取得
    member_project_ids = {m.project_id for m in db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()}

    # 申請中のプロジェクトIDを取得
    pending_project_ids = {r.project_id for r in db.query(ProjectJoinRequest).filter(
        ProjectJoinRequest.user_id == current_user.id,
        ProjectJoinRequest.status == JoinRequestStatus.PENDING
    ).all()}

    # 各プロジェクトにステータスを追加
    result = []
    for project in all_projects:
        project_dict = {
            "id": project.id,
            "name": project.name,
            "key": project.key,
            "description": project.description,
            "owner_id": project.owner_id,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }

        # ステータスを判定
        if project.id in member_project_ids:
            project_dict["membership_status"] = "joined"  # 参加済み
        elif project.id in pending_project_ids:
            project_dict["membership_status"] = "pending"  # 申請中
        else:
            project_dict["membership_status"] = "available"  # 参加可能

        result.append(project_dict)

    return result

@app.post("/api/projects", response_model=ProjectSchema)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # プロジェクトキー重複チェック
    existing = db.query(Project).filter(Project.key == project.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="このプロジェクトキーは既に使用されています")

    db_project = Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # オーナーをメンバーとして追加
    owner_member = ProjectMember(
        project_id=db_project.id,
        user_id=current_user.id,
        role="owner"
    )
    db.add(owner_member)
    db.commit()

    return db_project

@app.get("/api/projects/{project_id}", response_model=ProjectSchema)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")
    return project

@app.put("/api/projects/{project_id}", response_model=ProjectSchema)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(project, key, value)

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project

@app.delete("/api/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    if project.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="このプロジェクトを削除する権限がありません")

    db.delete(project)
    db.commit()
    return {"message": "プロジェクトを削除しました"}

# ===== プロジェクトメンバーエンドポイント =====

@app.get("/api/projects/{project_id}/members", response_model=List[ProjectMemberSchema])
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # プロジェクトメンバーのみアクセス可能
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not is_member and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="このプロジェクトのメンバーではありません")

    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()

@app.delete("/api/projects/{project_id}/members/{user_id}")
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 既存メンバーのみ削除可能
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not is_member and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="メンバーを削除する権限がありません")

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")

    # オーナーは削除できない
    if member.role == "owner":
        raise HTTPException(status_code=400, detail="オーナーは削除できません")

    db.delete(member)
    db.commit()
    return {"message": "メンバーを削除しました"}

# ===== 参加申請エンドポイント =====

@app.post("/api/projects/{project_id}/join-requests", response_model=JoinRequestSchema)
def create_join_request(
    project_id: int,
    request: JoinRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # プロジェクトの存在確認
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")

    # 既にメンバーでないか確認
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if is_member:
        raise HTTPException(status_code=400, detail="既にこのプロジェクトのメンバーです")

    # 既に申請していないか確認
    existing_request = db.query(ProjectJoinRequest).filter(
        ProjectJoinRequest.project_id == project_id,
        ProjectJoinRequest.user_id == current_user.id,
        ProjectJoinRequest.status == JoinRequestStatus.PENDING
    ).first()

    if existing_request:
        raise HTTPException(status_code=400, detail="既に申請済みです")

    # 参加申請作成
    db_request = ProjectJoinRequest(
        project_id=project_id,
        user_id=current_user.id,
        message=request.message,
        status=JoinRequestStatus.PENDING
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

@app.get("/api/projects/{project_id}/join-requests", response_model=List[JoinRequestSchema])
def list_join_requests(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # プロジェクトメンバーのみアクセス可能
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not is_member and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="このプロジェクトのメンバーではありません")

    return db.query(ProjectJoinRequest).filter(
        ProjectJoinRequest.project_id == project_id,
        ProjectJoinRequest.status == JoinRequestStatus.PENDING
    ).all()

@app.post("/api/join-requests/{request_id}/approve", response_model=JoinRequestSchema)
def approve_join_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 申請を取得
    join_request = db.query(ProjectJoinRequest).filter(ProjectJoinRequest.id == request_id).first()
    if not join_request:
        raise HTTPException(status_code=404, detail="申請が見つかりません")

    # 既存メンバーのみ承認可能
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == join_request.project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not is_member and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="承認する権限がありません")

    if join_request.status != JoinRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="この申請は既に処理されています")

    # 承認処理
    join_request.status = JoinRequestStatus.APPROVED
    join_request.reviewed_by = current_user.id
    join_request.reviewed_at = datetime.utcnow()

    # メンバーとして追加
    new_member = ProjectMember(
        project_id=join_request.project_id,
        user_id=join_request.user_id,
        role="member"
    )
    db.add(new_member)
    db.commit()
    db.refresh(join_request)
    return join_request

@app.post("/api/join-requests/{request_id}/reject", response_model=JoinRequestSchema)
def reject_join_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 申請を取得
    join_request = db.query(ProjectJoinRequest).filter(ProjectJoinRequest.id == request_id).first()
    if not join_request:
        raise HTTPException(status_code=404, detail="申請が見つかりません")

    # 既存メンバーのみ却下可能
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == join_request.project_id,
        ProjectMember.user_id == current_user.id
    ).first()

    if not is_member and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="却下する権限がありません")

    if join_request.status != JoinRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="この申請は既に処理されています")

    # 却下処理
    join_request.status = JoinRequestStatus.REJECTED
    join_request.reviewed_by = current_user.id
    join_request.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(join_request)
    return join_request

@app.get("/api/my-join-requests", response_model=List[JoinRequestSchema])
def list_my_join_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(ProjectJoinRequest).filter(
        ProjectJoinRequest.user_id == current_user.id
    ).all()

# ===== マイルストーンエンドポイント =====

@app.get("/api/projects/{project_id}/milestones", response_model=List[MilestoneSchema])
def list_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Milestone).filter(Milestone.project_id == project_id).all()

@app.post("/api/milestones", response_model=MilestoneSchema)
def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_milestone = Milestone(**milestone.dict())
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

@app.put("/api/milestones/{milestone_id}", response_model=MilestoneSchema)
def update_milestone(
    milestone_id: int,
    milestone_update: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="マイルストーンが見つかりません")

    for key, value in milestone_update.dict(exclude_unset=True).items():
        setattr(milestone, key, value)

    db.commit()
    db.refresh(milestone)
    return milestone

@app.delete("/api/milestones/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="マイルストーンが見つかりません")

    db.delete(milestone)
    db.commit()
    return {"message": "マイルストーンを削除しました"}

# ===== カテゴリエンドポイント =====

@app.get("/api/projects/{project_id}/categories", response_model=List[CategorySchema])
def list_categories(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Category).filter(Category.project_id == project_id).all()

@app.post("/api/categories", response_model=CategorySchema)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.put("/api/categories/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")

    for key, value in category_update.dict(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category

@app.delete("/api/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="カテゴリが見つかりません")

    db.delete(category)
    db.commit()
    return {"message": "カテゴリを削除しました"}

# ===== 課題エンドポイント =====

@app.get("/api/projects/{project_id}/issues", response_model=List[IssueSchema])
def list_issues(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Issue).filter(Issue.project_id == project_id).all()

@app.get("/api/issues/multi-project", response_model=List[IssueSchema])
def list_multi_project_issues(
    project_ids: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # カンマ区切りのプロジェクトIDを解析
    try:
        id_list = [int(pid.strip()) for pid in project_ids.split(',') if pid.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="無効なプロジェクトIDです")

    if not id_list:
        return []

    # プロジェクトメンバーシップの確認
    member_project_ids = {m.project_id for m in db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id,
        ProjectMember.project_id.in_(id_list)
    ).all()}

    # アクセス権のないプロジェクトIDがあればエラー
    unauthorized_ids = set(id_list) - member_project_ids
    if unauthorized_ids and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="一部のプロジェクトへのアクセス権がありません")

    # 課題を取得
    issues = db.query(Issue).filter(Issue.project_id.in_(id_list)).all()
    return issues

@app.post("/api/issues", response_model=IssueSchema)
def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # プロジェクト内での連番を計算
    max_issue = db.query(Issue).filter(
        Issue.project_id == issue.project_id
    ).order_by(Issue.issue_number.desc()).first()

    next_number = 1 if not max_issue else max_issue.issue_number + 1

    db_issue = Issue(
        **issue.dict(),
        issue_number=next_number,
        creator_id=current_user.id
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@app.get("/api/issues/{issue_id}", response_model=IssueSchema)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="課題が見つかりません")
    return issue

@app.put("/api/issues/{issue_id}", response_model=IssueSchema)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="課題が見つかりません")

    for key, value in issue_update.dict(exclude_unset=True).items():
        setattr(issue, key, value)

    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return issue

@app.delete("/api/issues/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="課題が見つかりません")

    db.delete(issue)
    db.commit()
    return {"message": "課題を削除しました"}

# ===== コメントエンドポイント =====

@app.get("/api/issues/{issue_id}/comments", response_model=List[CommentSchema])
def list_comments(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Comment).filter(Comment.issue_id == issue_id).all()

@app.post("/api/comments", response_model=CommentSchema)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_comment = Comment(**comment.dict(), author_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.put("/api/comments/{comment_id}", response_model=CommentSchema)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="コメントが見つかりません")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="このコメントを編集する権限がありません")

    comment.content = comment_update.content
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)
    return comment

@app.delete("/api/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="コメントが見つかりません")

    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="このコメントを削除する権限がありません")

    db.delete(comment)
    db.commit()
    return {"message": "コメントを削除しました"}

# ===== Wikiエンドポイント =====

@app.get("/api/projects/{project_id}/wiki", response_model=List[WikiPageSchema])
def list_wiki_pages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(WikiPage).filter(WikiPage.project_id == project_id).all()

@app.post("/api/wiki", response_model=WikiPageSchema)
def create_wiki_page(
    page: WikiPageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_page = WikiPage(**page.dict(), author_id=current_user.id)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

@app.get("/api/wiki/{page_id}", response_model=WikiPageSchema)
def get_wiki_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wikiページが見つかりません")
    return page

@app.put("/api/wiki/{page_id}", response_model=WikiPageSchema)
def update_wiki_page(
    page_id: int,
    page_update: WikiPageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wikiページが見つかりません")

    for key, value in page_update.dict(exclude_unset=True).items():
        setattr(page, key, value)

    page.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(page)
    return page

@app.delete("/api/wiki/{page_id}")
def delete_wiki_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wikiページが見つかりません")

    db.delete(page)
    db.commit()
    return {"message": "Wikiページを削除しました"}

# ===== 依存関係エンドポイント =====

@app.get("/api/projects/{project_id}/dependencies", response_model=List[IssueDependencySchema])
def list_dependencies(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # プロジェクト内の全課題IDを取得
    issue_ids = [issue.id for issue in db.query(Issue).filter(Issue.project_id == project_id).all()]

    # それらの課題に関連する依存関係を取得
    dependencies = db.query(IssueDependency).filter(
        IssueDependency.source_issue_id.in_(issue_ids)
    ).all()

    return dependencies

@app.post("/api/dependencies", response_model=IssueDependencySchema)
def create_dependency(
    dependency: IssueDependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 循環依存チェック
    if dependency.source_issue_id == dependency.target_issue_id:
        raise HTTPException(status_code=400, detail="課題は自分自身に依存できません")

    # 既存の依存関係チェック
    existing = db.query(IssueDependency).filter(
        IssueDependency.source_issue_id == dependency.source_issue_id,
        IssueDependency.target_issue_id == dependency.target_issue_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="この依存関係は既に存在します")

    db_dependency = IssueDependency(**dependency.dict())
    db.add(db_dependency)
    db.commit()
    db.refresh(db_dependency)
    return db_dependency

@app.delete("/api/dependencies/{dependency_id}")
def delete_dependency(
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    dependency = db.query(IssueDependency).filter(IssueDependency.id == dependency_id).first()
    if not dependency:
        raise HTTPException(status_code=404, detail="依存関係が見つかりません")

    db.delete(dependency)
    db.commit()
    return {"message": "依存関係を削除しました"}

# ===== ダッシュボードエンドポイント =====

@app.get("/api/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    total_projects = db.query(Project).count()
    total_issues = db.query(Issue).count()
    my_assigned_issues = db.query(Issue).filter(Issue.assignee_id == current_user.id).count()

    # 期限切れの課題
    overdue_issues = db.query(Issue).filter(
        Issue.due_date < datetime.now().date(),
        Issue.status != IssueStatus.DONE,
        Issue.status != IssueStatus.CLOSED
    ).count()

    # 最近の課題（最新5件）
    recent_issues = db.query(Issue).order_by(Issue.created_at.desc()).limit(5).all()

    return {
        "total_projects": total_projects,
        "total_issues": total_issues,
        "my_assigned_issues": my_assigned_issues,
        "overdue_issues": overdue_issues,
        "recent_issues": recent_issues
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
