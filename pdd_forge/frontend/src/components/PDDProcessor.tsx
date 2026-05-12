import { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import { uploadPDD, generateProject, downloadProject } from '../services/api';
import { useAppStore } from '../store/appStore';
import type { PDDSection } from '../types';

interface FileUploadProps {
  onUploadComplete: (sessionId: string) => void;
}

export function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setUploading = useAppStore((state) => state.setUploading);
  const setFileName = useAppStore((state) => state.setFileName);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const processFile = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are supported');
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const response = await uploadPDD(file);
      setFileName(response.filename);
      onUploadComplete(response.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [onUploadComplete, setUploading, setFileName]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  }, [processFile]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  }, [processFile]);

  return (
    <div className="upload-container">
      <div
        className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="upload-icon" size={48} />
        <h3>Upload PDD Document</h3>
        <p>Drag and drop your PDF here, or click to select</p>
        <input
          type="file"
          accept=".pdf"
          onChange={handleChange}
          className="file-input"
        />
      </div>
      
      {error && (
        <div className="error-message">
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

interface SectionReviewProps {
  sections: PDDSection[];
  onConfirm: () => void;
}

export function SectionReview({ sections, onConfirm }: SectionReviewProps) {
  return (
    <div className="section-review">
      <h3>Extracted Sections</h3>
      <div className="sections-list">
        {sections.map((section) => (
          <div key={section.id} className="section-item">
            <div className="section-header">
              <FileText size={20} />
              <h4>{section.name}</h4>
              <span className={`confidence confidence-${section.confidence >= 0.7 ? 'high' : 'medium'}`}>
                {Math.round(section.confidence * 100)}% match
              </span>
            </div>
            <p className="section-pages">Pages: {section.pages}</p>
          </div>
        ))}
      </div>
      <button onClick={onConfirm} className="confirm-btn">
        <CheckCircle size={20} />
        Confirm & Generate Project
      </button>
    </div>
  );
}

interface GenerationStatusProps {
  isGenerating: boolean;
  qualityScore: number | null;
  warnings: string[];
  onDownload: () => void;
  projectGenerated: boolean;
}

export function GenerationStatus({
  isGenerating,
  qualityScore,
  warnings,
  onDownload,
  projectGenerated,
}: GenerationStatusProps) {
  if (isGenerating) {
    return (
      <div className="generation-status">
        <Loader2 className="spinner" size={48} />
        <h3>Generating UiPath Project...</h3>
        <p>This may take a moment</p>
      </div>
    );
  }

  if (projectGenerated) {
    return (
      <div className="generation-complete">
        <CheckCircle className="success-icon" size={48} />
        <h3>Project Generated Successfully!</h3>
        
        {qualityScore !== null && (
          <div className="quality-score">
            <h4>Quality Score: {qualityScore}/100</h4>
            <div className="score-bar">
              <div 
                className={`score-fill ${qualityScore >= 80 ? 'high' : qualityScore >= 60 ? 'medium' : 'low'}`}
                style={{ width: `${qualityScore}%` }}
              />
            </div>
          </div>
        )}

        {warnings.length > 0 && (
          <div className="warnings">
            <h4>Warnings:</h4>
            <ul>
              {warnings.map((warning, idx) => (
                <li key={idx}>
                  <AlertTriangle size={16} />
                  {warning}
                </li>
              ))}
            </ul>
          </div>
        )}

        <button onClick={onDownload} className="download-btn">
          <DownloadIcon size={20} />
          Download Project ZIP
        </button>
      </div>
    );
  }

  return null;
}

function DownloadIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}
