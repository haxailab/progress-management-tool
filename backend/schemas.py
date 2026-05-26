from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from models import IssueStatus, IssuePriority, JoinRequestStatus

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordReset(BaseModel):
    new_password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    key: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Milestone Schemas
class MilestoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None

class MilestoneCreate(MilestoneBase):
    project_id: int

class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None

class Milestone(MilestoneBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    color: Optional[str] = None

class CategoryCreate(CategoryBase):
    project_id: int

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class Category(CategoryBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Issue Schemas
class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[IssueStatus] = IssueStatus.TODO
    priority: Optional[IssuePriority] = IssuePriority.NORMAL
    assignee_id: Optional[int] = None
    milestone_id: Optional[int] = None
    category_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    progress: Optional[int] = 0

class IssueCreate(IssueBase):
    project_id: int

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None
    milestone_id: Optional[int] = None
    category_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    progress: Optional[int] = None

class Issue(IssueBase):
    id: int
    project_id: int
    issue_number: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    assignee: Optional[User] = None
    creator: Optional[User] = None
    milestone: Optional[Milestone] = None
    category: Optional[Category] = None

    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    issue_id: int

class CommentUpdate(BaseModel):
    content: str

class Comment(CommentBase):
    id: int
    issue_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: Optional[User] = None

    class Config:
        from_attributes = True

# Wiki Schemas
class WikiPageBase(BaseModel):
    title: str
    content: Optional[str] = None

class WikiPageCreate(WikiPageBase):
    project_id: int

class WikiPageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class WikiPage(WikiPageBase):
    id: int
    project_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: Optional[User] = None

    class Config:
        from_attributes = True

# File Schemas
class FileBase(BaseModel):
    filename: str
    size: Optional[int] = None
    mime_type: Optional[str] = None

class FileCreate(FileBase):
    project_id: int
    filepath: str
    uploaded_by: int

class File(FileBase):
    id: int
    project_id: int
    filepath: str
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True

# Dependency Schemas
class IssueDependencyBase(BaseModel):
    source_issue_id: int
    target_issue_id: int
    dependency_type: str = "finish-to-start"

class IssueDependencyCreate(IssueDependencyBase):
    pass

class IssueDependency(IssueDependencyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_projects: int
    total_issues: int
    my_assigned_issues: int
    overdue_issues: int
    recent_issues: List[Issue]

# Project Member Schemas
class ProjectMemberBase(BaseModel):
    role: str = "member"

class ProjectMemberCreate(ProjectMemberBase):
    project_id: int
    user_id: int

class ProjectMember(ProjectMemberBase):
    id: int
    project_id: int
    user_id: int
    joined_at: datetime
    user: Optional[User] = None

    class Config:
        from_attributes = True

# Join Request Schemas
class JoinRequestBase(BaseModel):
    message: Optional[str] = None

class JoinRequestCreate(JoinRequestBase):
    project_id: int

class JoinRequestUpdate(BaseModel):
    status: JoinRequestStatus

class JoinRequest(JoinRequestBase):
    id: int
    project_id: int
    user_id: int
    status: JoinRequestStatus
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    user: Optional[User] = None
    project: Optional[Project] = None
    reviewer: Optional[User] = None

    class Config:
        from_attributes = True
