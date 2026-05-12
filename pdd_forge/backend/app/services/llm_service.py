"""
LLM Service - Semantic analysis and extraction from PDD text.

Uses LLM (GPT-4o or mock) for:
- Section classification (Pass 2)
- Content extraction (Pass 3)
- IR assembly (Pass 4)

Implements structured output with Pydantic models.
"""
import json
import logging
from typing import List, Dict, Optional
from app.core.config import settings
from app.models.ir import (
    IntermediateRepresentation, ProcessInfo, ProcessType, Step, 
    StepType, BusinessRule, ExceptionDefinition, ExceptionType,
    ConfigItem, PDDSection, TransactionDefinition, TransactionSource
)

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM Service for PDD semantic analysis.
    
    Handles:
    - Section classification
    - Step extraction
    - Business rule extraction
    - Exception classification
    - Configuration extraction
    """
    
    def __init__(self, use_mock: bool = None):
        self.use_mock = use_mock if use_mock is not None else settings.llm_mock
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key
        
        if not self.api_key and not self.use_mock:
            logger.warning("No OpenAI API key found. Using mock mode.")
            self.use_mock = True
    
    def classify_sections(self, full_text: str) -> List[PDDSection]:
        """
        Pass 2: Classify sections in the PDD.
        
        Args:
            full_text: Full extracted text from PDF
            
        Returns:
            List of classified PDD sections
        """
        if self.use_mock:
            return self._mock_classify_sections(full_text)
        
        # TODO: Implement with OpenAI API
        # Use few-shot prompting with known PDD structures
        raise NotImplementedError("Real LLM implementation pending")
    
    def extract_ir(self, sections: List[PDDSection]) -> IntermediateRepresentation:
        """
        Pass 3 & 4: Extract IR from classified sections.
        
        Args:
            sections: Classified PDD sections
            
        Returns:
            IntermediateRepresentation object
        """
        if self.use_mock:
            return self._mock_extract_ir(sections)
        
        # TODO: Implement with OpenAI API
        raise NotImplementedError("Real LLM implementation pending")
    
    def _mock_classify_sections(self, full_text: str) -> List[PDDSection]:
        """Mock section classification for testing."""
        # Simple heuristic-based section detection
        section_keywords = {
            "Scope": ["scope", "objective", "purpose", "goal"],
            "Process Steps": ["step", "process flow", "workflow", "procedure"],
            "Business Rules": ["business rule", "rule", "condition", "validation"],
            "Exceptions": ["exception", "error", "handling", "recovery"],
            "Applications": ["application", "system", "software", "tool"],
            "Configuration": ["configuration", "setting", "parameter", "constant"]
        }
        
        sections = []
        text_lower = full_text.lower()
        
        for section_name, keywords in section_keywords.items():
            # Check if any keyword appears in text
            if any(kw in text_lower for kw in keywords):
                sections.append(PDDSection(
                    id=f"section_{len(sections)}",
                    name=section_name,
                    content=f"[Mock content for {section_name}]",
                    pages="1-5",
                    confidence=0.75
                ))
        
        # Always add a default scope if nothing found
        if not sections:
            sections.append(PDDSection(
                id="section_0",
                name="Scope",
                content="[Mock scope content]",
                pages="1",
                confidence=0.5
            ))
        
        logger.info(f"Mock classified {len(sections)} sections")
        return sections
    
    def _mock_extract_ir(self, sections: List[PDDSection]) -> IntermediateRepresentation:
        """Mock IR extraction for testing."""
        # Create a sample REFramework-compatible IR
        ir = IntermediateRepresentation(
            process=ProcessInfo(
                name="Automated Invoice Processing",
                description="Process invoices from email and enter into SAP",
                type=ProcessType.TRANSACTIONAL,
                applications=["Outlook", "SAP", "Excel"],
                transaction_definition=TransactionDefinition(
                    source=TransactionSource.QUEUE,
                    queue_name="InvoiceQueue",
                    item_schema={
                        "invoice_id": "string",
                        "vendor": "string",
                        "amount": "number",
                        "attachment_path": "string"
                    }
                )
            ),
            steps=[
                Step(
                    id="step_1",
                    name="Get Queue Item",
                    description="Retrieve invoice transaction from Orchestrator queue",
                    type=StepType.ACTION,
                    application="Orchestrator",
                    inputs=["Queue Name"],
                    outputs=["Queue Item", "Specific Content"],
                    suggested_activities=["Get Queue Item", "Add Log Message"]
                ),
                Step(
                    id="step_2",
                    name="Download Attachment",
                    description="Download invoice attachment from queue item",
                    type=StepType.ACTION,
                    application="Orchestrator",
                    inputs=["Queue Item"],
                    outputs=["Attachment Path"],
                    suggested_activities=["Get Queue Item", "Write File"]
                ),
                Step(
                    id="step_3",
                    name="Read Invoice Data",
                    description="Extract data from invoice using OCR",
                    type=StepType.ACTION,
                    application="Document Understanding",
                    inputs=["Attachment Path"],
                    outputs=["Invoice ID", "Vendor", "Amount", "Date"],
                    suggested_activities=["OCR Processor", "Extract Document Data"]
                ),
                Step(
                    id="step_4",
                    name="Validate Invoice",
                    description="Validate extracted invoice data against business rules",
                    type=StepType.DECISION,
                    application="Excel",
                    inputs=["Invoice Data"],
                    outputs=["Validation Result"],
                    business_rules=["rule_1", "rule_2"],
                    suggested_activities=["Read Range", "If"]
                ),
                Step(
                    id="step_5",
                    name="Enter SAP",
                    description="Enter validated invoice into SAP",
                    type=StepType.ACTION,
                    application="SAP",
                    inputs=["Validated Invoice Data"],
                    outputs=["SAP Document Number"],
                    exceptions=["ex_sap_timeout", "ex_invalid_vendor"],
                    suggested_activities=["Open Browser", "Type Into", "Click"]
                ),
                Step(
                    id="step_6",
                    name="Update Transaction Status",
                    description="Mark transaction as Successful or Failed in Orchestrator",
                    type=StepType.ACTION,
                    application="Orchestrator",
                    inputs=["Processing Result"],
                    outputs=[],
                    suggested_activities=["Set Transaction Status"]
                )
            ],
            business_rules=[
                BusinessRule(
                    id="rule_1",
                    condition="Invoice amount > 10000",
                    action="Require manager approval",
                    priority=1,
                    pdd_reference="Section: Business Rules"
                ),
                BusinessRule(
                    id="rule_2",
                    condition="Vendor not in approved list",
                    action="Reject invoice and notify requester",
                    priority=2,
                    pdd_reference="Section: Business Rules"
                )
            ],
            exceptions=[
                ExceptionDefinition(
                    id="ex_sap_timeout",
                    name="SAP Connection Timeout",
                    type=ExceptionType.SYSTEM,
                    description="SAP system is not responding",
                    handling_procedure="Retry 3 times with 30 second delay, then escalate",
                    pdd_reference="Section: Exceptions"
                ),
                ExceptionDefinition(
                    id="ex_invalid_vendor",
                    name="Invalid Vendor",
                    type=ExceptionType.BUSINESS,
                    description="Vendor ID not found in master data",
                    handling_procedure="Mark as BRE and continue to next transaction",
                    pdd_reference="Section: Exceptions"
                )
            ],
            configuration={
                "sap_url": ConfigItem(
                    key="sap_url",
                    value="https://sap.company.com",
                    type="string",
                    category="settings",
                    description="SAP login URL"
                ),
                "max_retries": ConfigItem(
                    key="max_retries",
                    value="3",
                    type="int",
                    category="constants",
                    description="Maximum retry attempts"
                ),
                "orchestrator_queue": ConfigItem(
                    key="orchestrator_queue",
                    value="InvoiceQueue",
                    type="string",
                    category="assets",
                    description="Orchestrator queue name"
                )
            },
            pdd_sections=sections,
            quality_score=78.5,
            warnings=[
                "Flowchart images detected but not processed",
                "Configuration section has low confidence score"
            ]
        )
        
        logger.info(f"Mock extracted IR with {len(ir.steps)} steps")
        return ir
    
    def calculate_quality_score(self, sections: List[PDDSection], ir: IntermediateRepresentation) -> float:
        """
        Calculate PDD quality score based on dimensions in implementation plan.
        
        Dimensions:
        - Section completeness (30%)
        - Step granularity (25%)
        - Rule explicitness (20%)
        - Exception coverage (15%)
        - Application specificity (10%)
        """
        scores = {}
        
        # Section completeness (expected: Scope, Steps, Rules, Exceptions, Apps, Config)
        expected_sections = {"Scope", "Process Steps", "Business Rules", "Exceptions", "Applications", "Configuration"}
        found_sections = {s.name for s in sections}
        scores["section_completeness"] = len(found_sections & expected_sections) / len(expected_sections) * 100
        
        # Step granularity (more steps with descriptions = better)
        step_score = min(100, len(ir.steps) * 10)
        steps_with_desc = sum(1 for s in ir.steps if s.description)
        desc_bonus = (steps_with_desc / len(ir.steps) * 20) if ir.steps else 0
        scores["step_granularity"] = min(100, step_score + desc_bonus)
        
        # Rule explicitness
        rule_score = min(100, len(ir.business_rules) * 15)
        scores["rule_explicitness"] = rule_score
        
        # Exception coverage
        ex_score = min(100, len(ir.exceptions) * 20)
        scores["exception_coverage"] = ex_score
        
        # Application specificity
        app_score = min(100, len(ir.process.applications) * 25)
        scores["application_specificity"] = app_score
        
        # Weighted average
        weights = {
            "section_completeness": 0.30,
            "step_granularity": 0.25,
            "rule_explicitness": 0.20,
            "exception_coverage": 0.15,
            "application_specificity": 0.10
        }
        
        total_score = sum(scores[dim] * weight for dim, weight in weights.items())
        
        return round(total_score, 2)
