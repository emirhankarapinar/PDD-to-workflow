import { create } from 'zustand';

interface AppState {
  sessionId: string | null;
  fileName: string | null;
  isUploading: boolean;
  isGenerating: boolean;
  qualityScore: number | null;
  warnings: string[];
  projectGenerated: boolean;
  
  setSessionId: (id: string | null) => void;
  setFileName: (name: string | null) => void;
  setUploading: (status: boolean) => void;
  setGenerating: (status: boolean) => void;
  setQualityScore: (score: number | null) => void;
  setWarnings: (warnings: string[]) => void;
  setProjectGenerated: (generated: boolean) => void;
  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  sessionId: null,
  fileName: null,
  isUploading: false,
  isGenerating: false,
  qualityScore: null,
  warnings: [],
  projectGenerated: false,
  
  setSessionId: (id) => set({ sessionId: id }),
  setFileName: (name) => set({ fileName: name }),
  setUploading: (status) => set({ isUploading: status }),
  setGenerating: (status) => set({ isGenerating: status }),
  setQualityScore: (score) => set({ qualityScore: score }),
  setWarnings: (warnings) => set({ warnings }),
  setProjectGenerated: (generated) => set({ projectGenerated: generated }),
  reset: () => set({
    sessionId: null,
    fileName: null,
    isUploading: false,
    isGenerating: false,
    qualityScore: null,
    warnings: [],
    projectGenerated: false,
  }),
}));
