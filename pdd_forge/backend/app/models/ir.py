"""
Intermediate Representation (IR) models for PDD data.

This schema decouples PDD understanding from project generation,
enabling multiple output formats and templates.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from enum import Enum


class ProcessType(str, Enum):
    TRANSACTIONAL = "transactional"
    LINEAR = "linear"


class TransactionSource(str, Enum):
    QUEUE = "queue"
    DATATABLE = "datatable"
    API = "api"


class StepType(str, Enum):
    ACTION = "action"
    DECISION = "decision"
    LOOP = "loop"
    EXCEPTION = "exception"


class ExceptionType(str, Enum):
    BUSINESS = "business"  # Business Rule Exception (BRE)
    SYSTEM = "system"  # System Exception (SysEx)


class TransactionDefinition(BaseModel):
    """Transaction definition for transactional processes."""
    source: TransactionSource = Field(..., description="Source of transactions")
    item_schema: Dict[str, Any] = Field(default_factory=dict, description="Schema of transaction item")
    queue_name: Optional[str] = Field(None, description="Orchestrator queue name")


class ProcessInfo(BaseModel):
    """Process-level information."""
    name: str = Field(..., description="Process name")
    description: str = Field("", description="Process description")
    type: ProcessType = Field(ProcessType.LINEAR, description="Process type")
    applications: List[str] = Field(default_factory=list, description="Applications used")
    transaction_definition: Optional[TransactionDefinition] = Field(
        None, description="Transaction definition for transactional processes"
    )
    has_user_interaction: bool = Field(False, description="Whether process has user interaction")


class BusinessRule(BaseModel):
    """Extracted business rule."""
    id: str = Field(..., description="Rule ID")
    condition: str = Field(..., description="Condition expression")
    action: str = Field(..., description="Action to take")
    priority: int = Field(1, description="Rule priority")
    pdd_reference: Optional[str] = Field(None, description="PDD section/page reference")


class Step(BaseModel):
    """Process step."""
    id: str = Field(..., description="Step ID")
    name: str = Field(..., description="Step name")
    description: str = Field("", description="Step description")
    type: StepType = Field(StepType.ACTION, description="Step type")
    application: Optional[str] = Field(None, description="Application used in this step")
    inputs: List[str] = Field(default_factory=list, description="Input data")
    outputs: List[str] = Field(default_factory=list, description="Output data")
    business_rules: List[str] = Field(default_factory=list, description="Applied business rule IDs")
    exceptions: List[str] = Field(default_factory=list, description="Possible exceptions")
    pdd_reference: Optional[str] = Field(None, description="PDD section/page reference")
    suggested_activities: List[str] = Field(default_factory=list, description="Suggested UiPath activities")


class ExceptionDefinition(BaseModel):
    """Exception definition."""
    id: str = Field(..., description="Exception ID")
    name: str = Field(..., description="Exception name")
    type: ExceptionType = Field(..., description="Exception type")
    description: str = Field("", description="Exception description")
    handling_procedure: Optional[str] = Field(None, description="How to handle this exception")
    pdd_reference: Optional[str] = Field(None, description="PDD section/page reference")


class ConfigItem(BaseModel):
    """Configuration item."""
    key: str = Field(..., description="Configuration key")
    value: str = Field(..., description="Configuration value")
    type: str = Field("string", description="Value type")
    category: str = Field("settings", description="Category: settings, constants, assets")
    description: Optional[str] = Field(None, description="Description")


class PDDSection(BaseModel):
    """Extracted PDD section."""
    id: str = Field(..., description="Section ID")
    name: str = Field(..., description="Section name")
    content: str = Field(..., description="Section content")
    pages: Optional[str] = Field(None, description="Page range in PDD")
    confidence: float = Field(1.0, description="Extraction confidence score")


class IntermediateRepresentation(BaseModel):
    """
    Intermediate Representation (IR) - the core data structure.
    
    This decouples PDD parsing from project generation.
    """
    # Metadata
    process: ProcessInfo = Field(..., description="Process information")
    
    # Steps
    steps: List[Step] = Field(default_factory=list, description="Process steps")
    
    # Business rules
    business_rules: List[BusinessRule] = Field(default_factory=list, description="Business rules")
    
    # Exceptions
    exceptions: List[ExceptionDefinition] = Field(default_factory=list, description="Exception definitions")
    
    # Configuration
    configuration: Dict[str, ConfigItem] = Field(default_factory=dict, description="Configuration items")
    
    # PDD sections (for traceability)
    pdd_sections: List[PDDSection] = Field(default_factory=list, description="Extracted PDD sections")
    
    # Quality metrics
    quality_score: float = Field(0.0, description="Overall PDD quality score (0-100)")
    warnings: List[str] = Field(default_factory=list, description="Generation warnings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "process": {
                    "name": "Invoice Processing",
                    "description": "Process invoices from email",
                    "type": "transactional",
                    "applications": ["Outlook", "SAP"],
                    "transaction_definition": {
                        "source": "queue",
                        "queue_name": "InvoiceQueue"
                    }
                },
                "steps": [
                    {
                        "id": "step_1",
                        "name": "Get Queue Item",
                        "type": "action",
                        "suggested_activities": ["Get Queue Item"]
                    }
                ]
            }
        }
