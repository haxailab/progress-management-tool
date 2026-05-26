from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class IssueStatus(str, enum.Enum):
    TODO = "未対応"
    IN_PROGRESS = "処理中"
    REVIEW = "レビュー"
    DONE = "完了"
    CLOSED = "終了"

class IssuePriority(str, enum.Enum):
    LOW = "低"
    NORMAL = "中"
    HIGH = "高"
    CRITICAL = "最重要"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    assigned_issues = relationship("Issue", back_populates="assignee", foreign_keys="Issue.assignee_id")
    created_issues = relationship("Issue", back_populates="creator", foreign_keys="Issue.creator_id")
    comments = relationship("Comment", back_populates="author")
    wiki_pages = relationship("WikiPage", back_populates="author")
    project_memberships = relationship("ProjectMember", back_populates="user")
    join_requests = relationship("ProjectJoinRequest", back_populates="user", foreign_keys="ProjectJoinRequest.user_id")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False)  # プロジェクトキー (例: PROJ)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="project", cascade="all, delete-orphan")
    wiki_pages = relationship("WikiPage", back_populates="project", cascade="all, delete-orphan")
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    join_requests = relationship("ProjectJoinRequest", back_populates="project", cascade="all, delete-orphan")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="milestones")
    issues = relationship("Issue", back_populates="milestone")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String)  # Hex color
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="categories")
    issues = relationship("Issue", back_populates="category")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    issue_number = Column(Integer, nullable=False)  # プロジェクト内での連番
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(IssueStatus), default=IssueStatus.TODO)
    priority = Column(SQLEnum(IssuePriority), default=IssuePriority.NORMAL)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    start_date = Column(Date)
    due_date = Column(Date)
    estimated_hours = Column(Integer)  # 予定時間
    actual_hours = Column(Integer)  # 実績時間
    progress = Column(Integer, default=0)  # 進捗率 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="issues")
    assignee = relationship("User", back_populates="assigned_issues", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="created_issues", foreign_keys=[creator_id])
    milestone = relationship("Milestone", back_populates="issues")
    category = relationship("Category", back_populates="issues")
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
    dependencies_as_source = relationship("IssueDependency", back_populates="source_issue", foreign_keys="IssueDependency.source_issue_id", cascade="all, delete-orphan")
    dependencies_as_target = relationship("IssueDependency", back_populates="target_issue", foreign_keys="IssueDependency.target_issue_id", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")

class WikiPage(Base):
    __tablename__ = "wiki_pages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="wiki_pages")
    author = relationship("User", back_populates="wiki_pages")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    size = Column(Integer)  # bytes
    mime_type = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="files")

class IssueDependency(Base):
    __tablename__ = "issue_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    source_issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    target_issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    dependency_type = Column(String, default="finish-to-start")  # finish-to-start, start-to-start, finish-to-finish, start-to-finish
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source_issue = relationship("Issue", back_populates="dependencies_as_source", foreign_keys=[source_issue_id])
    target_issue = relationship("Issue", back_populates="dependencies_as_target", foreign_keys=[target_issue_id])

class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # owner, member
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

class JoinRequestStatus(str, enum.Enum):
    PENDING = "申請中"
    APPROVED = "承認済み"
    REJECTED = "却下"

class ProjectJoinRequest(Base):
    __tablename__ = "project_join_requests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text)  # 申請メッセージ
    status = Column(SQLEnum(JoinRequestStatus), default=JoinRequestStatus.PENDING)
    reviewed_by = Column(Integer, ForeignKey("users.id"))  # 承認/却下したユーザー
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="join_requests")
    user = relationship("User", foreign_keys=[user_id], back_populates="join_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
