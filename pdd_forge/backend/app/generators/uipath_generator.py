"""
UiPath Project Generator - Creates UiPath project structure from IR.

Implements template-based generation strategy:
- REFramework (Queue) template support
- Template composition with Jinja2
- XAML fragment library
- Config.xlsx generation
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
import openpyxl
from openpyxl.utils import get_column_letter

from app.models.ir import IntermediateRepresentation, ProcessType, TransactionSource
from app.core.config import settings

logger = logging.getLogger(__name__)


class UiPathGenerator:
    """
    UiPath Project Generator.
    
    Generates:
    - Project folder structure
    - project.json
    - XAML workflow files (from templates)
    - Config.xlsx
    - nuget.config
    """
    
    def __init__(self, template_dir: str = None):
        self.template_dir = Path(template_dir or settings.template_dir)
        self.output_dir = Path(settings.output_dir)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['xml', 'xaml'])
        )
    
    def generate(self, ir: IntermediateRepresentation, output_path: Path = None) -> Path:
        """
        Generate complete UiPath project from IR.
        
        Args:
            ir: Intermediate Representation
            output_path: Optional output path (default: auto-generated)
            
        Returns:
            Path to generated project folder
        """
        if output_path is None:
            # Sanitize process name for folder
            safe_name = "".join(c if c.isalnum() else "_" for c in ir.process.name)
            output_path = self.output_dir / safe_name
        
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating UiPath project to {output_path}")
        
        # Select template based on IR
        template_name = self._select_template(ir)
        template_path = self.template_dir / template_name
        
        # Generate project structure
        self._create_folder_structure(output_path, template_name)
        
        # Generate project.json
        self._generate_project_json(ir, output_path, template_path)
        
        # Generate XAML files
        self._generate_xaml_files(ir, output_path, template_path)
        
        # Generate Config.xlsx
        self._generate_config_excel(ir, output_path, template_path)
        
        # Generate nuget.config
        self._generate_nuget_config(output_path)
        
        logger.info(f"Project generated successfully: {output_path}")
        return output_path
    
    def _select_template(self, ir: IntermediateRepresentation) -> str:
        """Select appropriate template based on IR."""
        if ir.process.type == ProcessType.TRANSACTIONAL:
            if ir.process.transaction_definition and \
               ir.process.transaction_definition.source == TransactionSource.QUEUE:
                return "reframework-queue"
            elif ir.process.transaction_definition and \
                 ir.process.transaction_definition.source == TransactionSource.DATATABLE:
                return "reframework-tabular"  # TODO: Implement
            else:
                return "reframework-queue"  # Default to queue
        else:
            return "linear"  # TODO: Implement linear template
    
    def _create_folder_structure(self, output_path: Path, template_name: str):
        """Create standard UiPath folder structure."""
        folders = [
            "",
            "Framework",
            "Process",
            "Data",
            "Screenshots",
            "Documents",
            ".local",
            ".settings"
        ]
        
        for folder in folders:
            (output_path / folder).mkdir(exist_ok=True)
    
    def _generate_project_json(self, ir: IntermediateRepresentation, 
                                output_path: Path, template_path: Path):
        """Generate project.json file."""
        project_json = {
            "name": ir.process.name,
            "projectId": f"gen-{ir.process.name.lower().replace(' ', '-')}",
            "description": ir.process.description,
            "main": "Main.xaml",
            "dependencies": {
                "UiPath.System.Activities": "[23.10.3]",
                "UiPath.UIAutomation.Activities": "[23.10.2]",
                "UiPath.Orchestrator.Activities": "[23.10.0]",
                "UiPath.DocumentUnderstanding.Activities": "[23.10.0]"
            },
            "webServices": [],
            "entitiesStores": [],
            "schemaVersion": "4.0",
            "studioVersion": "23.10.3",
            "projectVersion": "1.0.0",
            "runtimeOptions": {
                "autoDispose": False,
                "netFrameworkCompatibility": "Legacy",
                "arguments": {
                    "input": [],
                    "output": []
                },
                "queuesProcessing": {
                    "isQueueItemProcessingEnabled": True
                }
            },
            "language": "en-US",
            "expressionLanguage": "VisualBasic",
            "entryPoints": [
                {
                    "filePath": "Main.xaml",
                    "uniqueId": "main-entry",
                    "input": [],
                    "output": []
                }
            ],
            "isTemplate": False,
            "templateProjectIds": [],
            "publishData": {}
        }
        
        with open(output_path / "project.json", "w") as f:
            json.dump(project_json, f, indent=2)
        
        logger.debug("Generated project.json")
    
    def _generate_xaml_files(self, ir: IntermediateRepresentation,
                              output_path: Path, template_path: Path):
        """Generate all XAML workflow files."""
        # Generate Main.xaml (REFramework state machine)
        self._generate_main_xaml(ir, output_path, template_path)
        
        # Generate Framework workflows
        self._generate_framework_workflows(ir, output_path, template_path)
        
        # Generate Process workflows
        self._generate_process_workflows(ir, output_path, template_path)
    
    def _generate_main_xaml(self, ir: IntermediateRepresentation,
                            output_path: Path, template_path: Path):
        """Generate Main.xaml with REFramework state machine."""
        # For MVP, create a simplified Main.xaml structure
        # This is a template-based approach - in production, use Jinja2 templates
        
        main_xaml_content = self._create_reframework_main(ir)
        
        with open(output_path / "Main.xaml", "w") as f:
            f.write(main_xaml_content)
        
        logger.debug("Generated Main.xaml")
    
    def _generate_framework_workflows(self, ir: IntermediateRepresentation,
                                       output_path: Path, template_path: Path):
        """Generate REFramework framework workflows."""
        framework_workflows = [
            "InitAllSettings.xaml",
            "InitAllApplications.xaml",
            "GetTransactionData.xaml",
            "SetTransactionStatus.xaml",
            "CloseAllApplications.xaml",
            "KillAllProcesses.xaml"
        ]
        
        for workflow_name in framework_workflows:
            content = self._create_framework_workflow_stub(workflow_name, ir)
            with open(output_path / "Framework" / workflow_name, "w") as f:
                f.write(content)
        
        logger.debug(f"Generated {len(framework_workflows)} framework workflows")
    
    def _generate_process_workflows(self, ir: IntermediateRepresentation,
                                     output_path: Path, template_path: Path):
        """Generate individual process step workflows."""
        process_dir = output_path / "Process"
        
        for i, step in enumerate(ir.steps, 1):
            # Create workflow file for each step
            step_filename = f"Step{i:02d}_{step.name.replace(' ', '_')}.xaml"
            content = self._create_process_workflow_stub(step, i)
            
            with open(process_dir / step_filename, "w") as f:
                f.write(content)
        
        # Also create Process.xaml that orchestrates all steps
        process_xaml_content = self._create_process_orchestrator(ir)
        with open(output_path / "Process.xaml", "w") as f:
            f.write(process_xaml_content)
        
        logger.debug(f"Generated {len(ir.steps)} process workflows + Process.xaml")
    
    def _create_reframework_main(self, ir: IntermediateRepresentation) -> str:
        """Create REFramework Main.xaml state machine."""
        # Simplified REFramework Main.xaml structure
        # In production, this would be a full Jinja2 template
        
        return f'''<?xml version="1.0" encoding="utf-8"?>
<Activity mc:Ignorable="sap sap2010 sads" x:Class="Main" 
          xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" 
          xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" 
          xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" 
          xmlns:sads="http://schemas.itdlln.net/sads" 
          xmlns:sco="clr-namespace:System.Collections.ObjectModel;assembly=System" 
          xmlns:ui="http://schemas.uipath.com/workflow/activities" 
          xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <x:Members>
    <x:Property Name="in_Config" Type="InArgument(sco:Dictionary(x:String, ui:GenericValue))" />
  </x:Members>
  <sap:VirtualizedContainerService.HintSize>1152,1152</sap:VirtualizedContainerService.HintSize>
  <sap2010:WorkflowViewState.IdRef>Main_1</sap2010:WorkflowViewState.IdRef>
  <TextExpression.NamespacesForImplementation>
    <sco:Collection x:TypeArguments="x:String">
      <x:String>System</x:String>
      <x:String>System.Collections.Generic</x:String>
      <x:String>System.Data</x:String>
      <x:String>System.Linq</x:String>
      <x:String>System.Drawing</x:String>
      <x:String>System.Activities.Statements</x:String>
    </sco:Collection>
  </TextExpression.NamespacesForImplementation>
  <TextExpression.ReferencesForImplementation>
    <sco:Collection x:TypeArguments="AssemblyReference">
      <AssemblyReference>System</AssemblyReference>
      <AssemblyReference>System.Data</AssemblyReference>
      <AssemblyReference>System.Core</AssemblyReference>
      <AssemblyReference>UiPath.System.Activities</AssemblyReference>
      <AssemblyReference>UiPath.Workflow</AssemblyReference>
    </sco:Collection>
  </TextExpression.ReferencesForImplementation>
  <StateMachine DisplayName="{ir.process.name} - Main Workflow" sap2010:WorkflowViewState.IdRef="StateMachine_1">
    <!-- 
      REFramework State Machine
      Generated by PDD Forge
      Process: {ir.process.name}
      Description: {ir.process.description}
      
      ⚠️ TODO: Review and complete this workflow before running
    -->
    <StateMachine.InitialState>
      <State x:Name="__ReferenceID0" DisplayName="Init" sap2010:WorkflowViewState.IdRef="State_Init">
        <State.Entry>
          <InvokeWorkflowFile ContinueOnError="False" DisplayName="Invoke InitAllSettings" 
                             sap2010:WorkflowViewState.IdRef="InvokeInitSettings">
            <InvokeWorkflowFile.WorkflowFilePath>Framework\\InitAllSettings.xaml</InvokeWorkflowFile.WorkflowFilePath>
          </InvokeWorkflowFile>
          <InvokeWorkflowFile ContinueOnError="False" DisplayName="Invoke InitAllApplications" 
                             sap2010:WorkflowViewState.IdRef="InvokeInitApps">
            <InvokeWorkflowFile.WorkflowFilePath>Framework\\InitAllApplications.xaml</InvokeWorkflowFile.WorkflowFilePath>
          </InvokeWorkflowFile>
        </State.Entry>
        <State.Transitions>
          <Transition DisplayName="To Get Transaction Data" sap2010:WorkflowViewState.IdRef="Transition_Init_Get">
            <Transition.To>
              <State x:Name="__ReferenceID1" DisplayName="Get Transaction Data" sap2010:WorkflowViewState.IdRef="State_Get">
                <State.Entry>
                  <InvokeWorkflowFile ContinueOnError="False" DisplayName="Invoke GetTransactionData" 
                                     sap2010:WorkflowViewState.IdRef="InvokeGetTransaction">
                    <InvokeWorkflowFile.WorkflowFilePath>Framework\\GetTransactionData.xaml</InvokeWorkflowFile.WorkflowFilePath>
                  </InvokeWorkflowFile>
                </State.Entry>
                <State.Transitions>
                  <Transition DisplayName="To Process (if transaction exists)" sap2010:WorkflowViewState.IdRef="Transition_Get_Process">
                    <Transition.To>
                      <State x:Name="__ReferenceID2" DisplayName="Process Transaction" sap2010:WorkflowViewState.IdRef="State_Process">
                        <State.Entry>
                          <InvokeWorkflowFile ContinueOnError="False" DisplayName="Invoke Process" 
                                             sap2010:WorkflowViewState.IdRef="InvokeProcess">
                            <InvokeWorkflowFile.WorkflowFilePath>Process.xaml</InvokeWorkflowFile.WorkflowFilePath>
                          </InvokeWorkflowFile>
                        </State.Entry>
                        <State.Transitions>
                          <Transition DisplayName="Back to Get Transaction Data" sap2010:WorkflowViewState.IdRef="Transition_Process_Get">
                            <Transition.To>
                              <Reference x:Key="__ReferenceID1" />
                            </Transition.To>
                          </Transition>
                        </State.Transitions>
                      </State>
                    </Transition.To>
                  </Transition>
                  <Transition DisplayName="To End (no more transactions)" sap2010:WorkflowViewState.IdRef="Transition_Get_End">
                    <Transition.To>
                      <State x:Name="__ReferenceID3" DisplayName="End Process" sap2010:WorkflowViewState.IdRef="State_End">
                        <State.Entry>
                          <InvokeWorkflowFile ContinueOnError="False" DisplayName="Invoke CloseAllApplications" 
                                             sap2010:WorkflowViewState.IdRef="InvokeCloseApps">
                            <InvokeWorkflowFile.WorkflowFilePath>Framework\\CloseAllApplications.xaml</InvokeWorkflowFile.WorkflowFilePath>
                          </InvokeWorkflowFile>
                        </State.Entry>
                      </State>
                    </Transition.To>
                  </Transition>
                </State.Transitions>
              </State>
            </Transition.To>
          </Transition>
        </State.Transitions>
      </State>
    </StateMachine.InitialState>
    <!-- Additional states referenced above -->
    <x:Member Name="__ReferenceID1" Type="State" />
    <x:Member Name="__ReferenceID2" Type="State" />
    <x:Member Name="__ReferenceID3" Type="State" />
  </StateMachine>
</Activity>
'''
    
    def _create_framework_workflow_stub(self, workflow_name: str, ir: IntermediateRepresentation) -> str:
        """Create stub for framework workflow."""
        descriptions = {
            "InitAllSettings.xaml": "Initialize configuration settings from Config.xlsx",
            "InitAllApplications.xaml": "Open applications needed for the process",
            "GetTransactionData.xaml": "Get next transaction item from queue",
            "SetTransactionStatus.xaml": "Update transaction status in Orchestrator",
            "CloseAllApplications.xaml": "Close all applications gracefully",
            "KillAllProcesses.xaml": "Kill all processes in case of system exception"
        }
        
        return f'''<?xml version="1.0" encoding="utf-8"?>
<Activity mc:Ignorable="sap sap2010 sads" x:Class="{workflow_name.replace('.xaml', '')}" 
          xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" 
          xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" 
          xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" 
          xmlns:sads="http://schemas.itdlln.net/sads" 
          xmlns:ui="http://schemas.uipath.com/workflow/activities" 
          xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <sap:VirtualizedContainerService.HintSize>800,600</sap:VirtualizedContainerService.HintSize>
  <sap2010:WorkflowViewState.IdRef>{workflow_name.replace(".xaml", "_1")}</sap2010:WorkflowViewState.IdRef>
  <!-- 
    {descriptions.get(workflow_name, "Framework workflow")}
    Generated by PDD Forge for: {ir.process.name}
    
    ⚠️ TODO: Implement this workflow
  -->
  <Sequence DisplayName="Main Sequence" sap2010:WorkflowViewState.IdRef="Sequence_1">
    <sap:WorkflowViewStateService.ViewState>
      <scg:Dictionary x:TypeArguments="x:String, x:Object">
        <x:Boolean x:Key="IsExpanded">True</x:Boolean>
      </scg:Dictionary>
    </sap:WorkflowViewStateService.ViewState>
    <!-- TODO: Add activities here -->
  </Sequence>
</Activity>
'''
    
    def _create_process_workflow_stub(self, step, step_num: int) -> str:
        """Create stub for individual process step workflow."""
        step_name_safe = step.name.replace(' ', '_')
        
        annotations = []
        if step.description:
            annotations.append(f"Description: {step.description}")
        if step.application:
            annotations.append(f"Application: {step.application}")
        if step.suggested_activities:
            annotations.append(f"Suggested Activities: {', '.join(step.suggested_activities)}")
        if step.business_rules:
            annotations.append(f"Business Rules: {', '.join(step.business_rules)}")
        
        return f'''<?xml version="1.0" encoding="utf-8"?>
<Activity mc:Ignorable="sap sap2010 sads" x:Class="Step{step_num:02d}_{step_name_safe}" 
          xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" 
          xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" 
          xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" 
          xmlns:sads="http://schemas.itdlln.net/sads" 
          xmlns:ui="http://schemas.uipath.com/workflow/activities" 
          xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <x:Members>
    <x:Property Name="io_TransactionItem" Type="InOutArgument(ui:GenericValue)" />
    <x:Property Name="in_Config" Type="InArgument(sco:Dictionary(x:String, ui:GenericValue))" />
  </x:Members>
  <sap:VirtualizedContainerService.HintSize>800,600</sap:VirtualizedContainerService.HintSize>
  <sap2010:WorkflowViewState.IdRef>Step{step_num:02d}_{step_name_safe}_1</sap2010:WorkflowViewState.IdRef>
  <!-- 
    Step {step_num}: {step.name}
    {" | ".join(annotations) if annotations else "Process step"}
    
    Generated by PDD Forge
    
    ⚠️ TODO: Implement this workflow
    ⚠️ TODO: Add selectors for UI interactions
  -->
  <Sequence DisplayName="{step.name}" sap2010:WorkflowViewState.IdRef="Sequence_1">
    <sap:WorkflowViewStateService.ViewState>
      <scg:Dictionary x:TypeArguments="x:String, x:Object">
        <x:Boolean x:Key="IsExpanded">True</x:Boolean>
      </scg:Dictionary>
    </sap:WorkflowViewStateService.ViewState>
    
    <!-- TODO: Add activities for: {step.name} -->
    <!-- Suggested: {', '.join(step.suggested_activities) if step.suggested_activities else 'Review PDD'} -->
    
    <ui:CommentOut DisplayName="Example Log">
      <ui:CommentOut.Body>
        <Sequence>
          <ui:AddLog DisplayName="Add Log" Level="Info">
            <ui:AddLog.Message>
              <InArgument x:TypeArguments="x:String">[ "Executing Step {step_num}: {step.name}" ]</InArgument>
            </ui:AddLog.Message>
          </ui:AddLog>
        </Sequence>
      </ui:CommentOut.Body>
    </ui:CommentOut>
    
  </Sequence>
</Activity>
'''
    
    def _create_process_orchestrator(self, ir: IntermediateRepresentation) -> str:
        """Create Process.xaml that orchestrates all step workflows."""
        invoke_workflows = ""
        for i, step in enumerate(ir.steps, 1):
            step_name_safe = step.name.replace(' ', '_')
            invoke_workflows += f'''
    <!-- Step {i}: {step.name} -->
    <InvokeWorkflowFile ContinueOnError="False" DisplayName="Invoke Step {i}: {step.name}" 
                       sap2010:WorkflowViewState.IdRef="InvokeStep{i}">
      <InvokeWorkflowFile.WorkflowFilePath>Process\\Step{i:02d}_{step_name_safe}.xaml</InvokeWorkflowFile.WorkflowFilePath>
      <InArgument x:TypeArguments="ui:GenericVariable" x:Key="io_TransactionItem">[io_TransactionItem]</InArgument>
      <InArgument x:TypeArguments="scg:Dictionary(x:String, ui:GenericValue)" x:Key="in_Config">[in_Config]</InArgument>
    </InvokeWorkflowFile>
'''
        
        return f'''<?xml version="1.0" encoding="utf-8"?>
<Activity mc:Ignorable="sap sap2010 sads" x:Class="Process" 
          xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" 
          xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" 
          xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation" 
          xmlns:sads="http://schemas.itdlln.net/sads" 
          xmlns:sco="clr-namespace:System.Collections.Generic;assembly=System"
          xmlns:ui="http://schemas.uipath.com/workflow/activities" 
          xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <x:Members>
    <x:Property Name="io_TransactionItem" Type="InOutArgument(ui:GenericValue)" />
    <x:Property Name="in_Config" Type="InArgument(sco:Dictionary(x:String, ui:GenericValue))" />
  </x:Members>
  <sap:VirtualizedContainerService.HintSize>1000,800</sap:VirtualizedContainerService.HintSize>
  <sap2010:WorkflowViewState.IdRef>Process_1</sap2010:WorkflowViewState.IdRef>
  <!-- 
    Process Orchestration Workflow
    Generated by PDD Forge for: {ir.process.name}
    
    This workflow invokes individual step workflows in sequence.
    
    Total Steps: {len(ir.steps)}
    Applications: {', '.join(ir.process.applications)}
    
    ⚠️ TODO: Add error handling and business logic
  -->
  <Sequence DisplayName="Process Transaction" sap2010:WorkflowViewState.IdRef="Sequence_1">
    <sap:WorkflowViewStateService.ViewState>
      <scg:Dictionary x:TypeArguments="x:String, x:Object">
        <x:Boolean x:Key="IsExpanded">True</x:Boolean>
      </scg:Dictionary>
    </sap:WorkflowViewStateService.ViewState>
    
    <TryCatch DisplayName="Try Catch - Process Steps" sap2010:WorkflowViewState.IdRef="TryCatch_1">
      <TryCatch.Try>
        <Sequence DisplayName="Execute Process Steps" sap2010:WorkflowViewState.IdRef="Sequence_2">
{invoke_workflows}
        </Sequence>
      </TryCatch.Try>
      <TryCatch.Catches>
        <Catch x:TypeArguments="sads:Exception" sap2010:WorkflowViewState.IdRef="Catch_1">
          <ActivityAction x:TypeArguments="sads:Exception">
            <ActivityAction.Argument>
              <DelegateInArgument x:TypeArguments="sads:Exception" Name="exception" />
            </ActivityAction.Argument>
            <!-- TODO: Add exception handling logic -->
            <ui:LogMessage DisplayName="Log Exception" Level="Error">
              <ui:LogMessage.Message>
                <InArgument x:TypeArguments="x:String">[ "Process failed: " + exception.Message ]</InArgument>
              </ui:LogMessage.Message>
            </ui:LogMessage>
            <Rethrow sap2010:WorkflowViewState.IdRef="Rethrow_1" />
          </ActivityAction>
        </Catch>
      </TryCatch.Catches>
    </TryCatch>
    
  </Sequence>
</Activity>
'''
    
    def _generate_config_excel(self, ir: IntermediateRepresentation,
                                output_path: Path, template_path: Path):
        """Generate Config.xlsx with Settings, Constants, and Assets sheets."""
        wb = openpyxl.Workbook()
        
        # Remove default sheet
        default_sheet = wb.active
        wb.remove(default_sheet)
        
        # Create Settings sheet
        settings_sheet = wb.create_sheet("Settings")
        settings_headers = ["Key", "Value", "Description"]
        settings_sheet.append(settings_headers)
        
        # Create Constants sheet
        constants_sheet = wb.create_sheet("Constants")
        constants_headers = ["Key", "Value", "Description"]
        constants_sheet.append(constants_headers)
        
        # Create Assets sheet
        assets_sheet = wb.create_sheet("Assets")
        assets_headers = ["AssetName", "ValueType", "Value", "Description"]
        assets_sheet.append(assets_headers)
        
        # Populate from IR configuration
        for key, config_item in ir.configuration.items():
            if config_item.category == "settings":
                settings_sheet.append([config_item.key, config_item.value, config_item.description or ""])
            elif config_item.category == "constants":
                constants_sheet.append([config_item.key, config_item.value, config_item.description or ""])
            elif config_item.category == "assets":
                assets_sheet.append([config_item.key, "String", config_item.value, config_item.description or ""])
        
        # Add default values if empty
        if settings_sheet.max_row == 1:
            settings_sheet.append(["max_retries", "3", "Maximum retry attempts"])
            settings_sheet.append(["timeout_seconds", "30", "Timeout for UI operations"])
        
        if constants_sheet.max_row == 1:
            constants_sheet.append(["MaxRetryAttempts", "3", "Maximum number of retries"])
        
        if assets_sheet.max_row == 1:
            if ir.process.transaction_definition and ir.process.transaction_definition.queue_name:
                assets_sheet.append(["OrchestratorQueue", "String", ir.process.transaction_definition.queue_name, "Queue name"])
            else:
                assets_sheet.append(["OrchestratorQueue", "String", "DefaultQueue", "Queue name"])
        
        # Save workbook
        config_path = output_path / "Data" / "Config.xlsx"
        wb.save(config_path)
        
        logger.debug(f"Generated Config.xlsx at {config_path}")
    
    def _generate_nuget_config(self, output_path: Path):
        """Generate nuget.config file."""
        nuget_content = '''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="UiPath" value="https://library.uipath.com/api/v2/feed/" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>
</configuration>
'''
        with open(output_path / "nuget.config", "w") as f:
            f.write(nuget_content)
        
        logger.debug("Generated nuget.config")
