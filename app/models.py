from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#DeclarativeBase : Base class for every table
#Mapped : type annotation recognised by SQLAlchemy
# mapped_coloumn() : creates a database column
# relationships() : Links tables together

# 1. The Declarative Base
# All your database models must inherit from this class so SQLAlchemy can track them.
class Base(DeclarativeBase):
    pass


# 2. The Asset Model (The Core Entity)
class Asset(Base):
    """The central source of truth. Targets you own/control."""
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    target: Mapped[str] = mapped_column(String, unique=True, index=True)  # e.g., '192.168.1.5', 'myportfolio.com'
    asset_type: Mapped[str] = mapped_column(String)  # 'IP', 'DOMAIN', 'DIRECTORY'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships (Allows easy Pythonic access to related records)
    scan_jobs: Mapped[list["ScanJob"]] = relationship(back_populates="asset", cascade="all, delete")
    findings: Mapped[list["Finding"]] = relationship(back_populates="asset", cascade="all, delete")


# 3. The ScanJob Model (Append-Only Audit Log)
class ScanJob(Base):
    """Tracks every execution of your 4 modules (OSINT, FIM, Port Scan, Log Analysis)."""
    __tablename__ = "scan_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    module_name: Mapped[str] = mapped_column(String)  # 'osint', 'port_scan', 'fim', 'log_analysis'
    status: Mapped[str] = mapped_column(String)  # 'SUCCESS', 'FAILED'
    raw_output: Mapped[dict] = mapped_column(JSON)  # The full raw JSON artifact from the script
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="scan_jobs")
    findings: Mapped[list["Finding"]] = relationship(back_populates="scan_job")


# 4. The Finding Model (Differential Alerts)
class Finding(Base):
    """Created ONLY when state changes (e.g., a new port opens, a hash mutates)."""
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    scan_job_id: Mapped[int] = mapped_column(ForeignKey("scan_jobs.id"))

    severity: Mapped[str] = mapped_column(String)  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    title: Mapped[str] = mapped_column(String)  # e.g., "New Open Port: 22"
    details: Mapped[dict] = mapped_column(JSON)  # Specific structural context for the AI agent
    resolved: Mapped[bool] = mapped_column(default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="findings")
    scan_job: Mapped["ScanJob"] = relationship(back_populates="findings")


# 5. The LogEvent Model (High-Volume Traffic Stream)
class LogEvent(Base):
    """High-volume append-only table for web server logs and ML anomaly detection."""
    __tablename__ = "log_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))

    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    source_ip: Mapped[str] = mapped_column(String)
    http_method: Mapped[str] = mapped_column(String)
    endpoint: Mapped[str] = mapped_column(String)
    status_code: Mapped[int] = mapped_column(Integer)
    user_agent: Mapped[str] = mapped_column(String)

    # Updated later by your scikit-learn Isolation Forest model
    anomaly_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)