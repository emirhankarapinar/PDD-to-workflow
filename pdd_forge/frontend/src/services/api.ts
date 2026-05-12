import axios from 'axios';
import type { UploadResponse, GenerateResponse, SessionInfo } from '../types';

const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadPDD = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const generateProject = async (sessionId: string): Promise<GenerateResponse> => {
  const response = await apiClient.post<GenerateResponse>(`/generate/${sessionId}`);
  return response.data;
};

export const downloadProject = async (sessionId: string): Promise<void> => {
  const response = await apiClient.get(`/download/${sessionId}`, {
    responseType: 'blob',
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `project-${sessionId}.zip`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const getSessionInfo = async (sessionId: string): Promise<SessionInfo> => {
  const response = await apiClient.get<SessionInfo>(`/session/${sessionId}`);
  return response.data;
};
