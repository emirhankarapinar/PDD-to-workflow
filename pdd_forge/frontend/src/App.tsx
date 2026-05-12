import { useState } from 'react';
import { FileUpload, SectionReview, GenerationStatus } from '../components/PDDProcessor';
import { generateProject, downloadProject } from '../services/api';
import { useAppStore } from '../store/appStore';
import type { PDDSection } from '../types';
import './App.css';

enum ProcessStep {
  UPLOAD,
  REVIEW,
  GENERATE,
  COMPLETE
}

function App() {
  const [currentStep, setCurrentStep] = useState<ProcessStep>(ProcessStep.UPLOAD);
  const [sections, setSections] = useState<PDDSection[]>([]);
  
  const {
    sessionId,
    isUploading,
    isGenerating,
    qualityScore,
    warnings,
    projectGenerated,
    setSessionId,
    setIsGenerating,
    setQualityScore,
    setWarnings,
    setProjectGenerated,
    reset,
  } = useAppStore();

  const handleUploadComplete = (sessionId: string) => {
    setSessionId(sessionId);
    // In a real app, we'd get sections from the response
    // For now, we'll simulate with mock data
    setSections([
      { id: '1', name: 'Scope', content: '', pages: '1-2', confidence: 0.85 },
      { id: '2', name: 'Process Steps', content: '', pages: '3-8', confidence: 0.92 },
      { id: '3', name: 'Business Rules', content: '', pages: '9-10', confidence: 0.78 },
      { id: '4', name: 'Exceptions', content: '', pages: '11-12', confidence: 0.81 },
    ]);
    setCurrentStep(ProcessStep.REVIEW);
  };

  const handleConfirmSections = async () => {
    if (!sessionId) return;
    
    setIsGenerating(true);
    setCurrentStep(ProcessStep.GENERATE);

    try {
      const response = await generateProject(sessionId);
      setQualityScore(response.quality_score);
      setWarnings(response.warnings);
      setProjectGenerated(true);
      setCurrentStep(ProcessStep.COMPLETE);
    } catch (error) {
      console.error('Generation failed:', error);
      alert('Failed to generate project. Please try again.');
      reset();
      setCurrentStep(ProcessStep.UPLOAD);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!sessionId) return;
    
    try {
      await downloadProject(sessionId);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download project. Please try again.');
    }
  };

  const handleReset = () => {
    reset();
    setSections([]);
    setCurrentStep(ProcessStep.UPLOAD);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔧 PDD Forge</h1>
        <p>Transform Process Design Documents into UiPath Projects</p>
      </header>

      <main className="app-main">
        <div className="progress-indicator">
          <div className={`step ${currentStep >= ProcessStep.UPLOAD ? 'active' : ''}`}>
            <span>1. Upload</span>
          </div>
          <div className={`step ${currentStep >= ProcessStep.REVIEW ? 'active' : ''}`}>
            <span>2. Review</span>
          </div>
          <div className={`step ${currentStep >= ProcessStep.GENERATE ? 'active' : ''}`}>
            <span>3. Generate</span>
          </div>
          <div className={`step ${currentStep >= ProcessStep.COMPLETE ? 'active' : ''}`}>
            <span>4. Download</span>
          </div>
        </div>

        <div className="content-area">
          {currentStep === ProcessStep.UPLOAD && (
            <FileUpload onUploadComplete={handleUploadComplete} />
          )}

          {currentStep === ProcessStep.REVIEW && (
            <SectionReview 
              sections={sections} 
              onConfirm={handleConfirmSections} 
            />
          )}

          {currentStep === ProcessStep.GENERATE && (
            <GenerationStatus
              isGenerating={isGenerating}
              qualityScore={null}
              warnings={[]}
              onDownload={() => {}}
              projectGenerated={false}
            />
          )}

          {currentStep === ProcessStep.COMPLETE && (
            <GenerationStatus
              isGenerating={false}
              qualityScore={qualityScore}
              warnings={warnings}
              onDownload={handleDownload}
              projectGenerated={true}
            />
          )}
        </div>

        {currentStep !== ProcessStep.UPLOAD && (
          <button onClick={handleReset} className="reset-btn">
            Start Over
          </button>
        )}
      </main>

      <footer className="app-footer">
        <p>PDD Forge v0.1.0 - Powered by AI</p>
      </footer>
    </div>
  );
}

export default App;
