import apiClient from "./client";

// ─── Auth routes ────────────────────────────────────────────────────────────

export async function signupUser(payload) {
  const { data } = await apiClient.post("/auth/signup", payload);
  return data;
}

export async function loginUser(payload) {
  const { data } = await apiClient.post("/auth/login", payload);
  return data;
}

// ─── Frontend orchestration routes ───────────────────────────────────────────

export async function uploadResume(file, onUploadProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (evt) => {
      if (onUploadProgress && evt.total) {
        onUploadProgress(Math.round((evt.loaded * 100) / evt.total));
      }
    },
  });
  return data;
}

export async function parseResume(resumeId) {
  const { data } = await apiClient.post("/resume/parse", { resume_id: resumeId });
  return data;
}

export async function submitJobDescription(payload) {
  const { data } = await apiClient.post("/job-description/submit", payload);
  return data;
}

export async function analyzeResume({ resumeId, jdId }) {
  const { data } = await apiClient.post("/analyze", {
    resume_id: resumeId,
    jd_id: jdId,
  });
  return data;
}

export async function getAnalysisById(analysisId) {
  const { data } = await apiClient.get(`/analyze/${analysisId}`);
  return data;
}

export async function getAnalysisHistory() {
  const { data } = await apiClient.get("/resume/history");
  return data;
}

export async function deleteResume(resumeId) {
  const { data } = await apiClient.delete(`/resume/${resumeId}`);
  return data;
}

export async function checkApiHealth() {
  const { data } = await apiClient.get("/health");
  return data;
}

export async function checkRootHealth() {
  const { data } = await apiClient.get("/");
  return data;
}

// ─── Resume routes (resume_controller) ───────────────────────────────────────

export async function getResumeSkills(resumeId) {
  const params = resumeId ? { resume_id: resumeId } : {};
  const { data } = await apiClient.get("/resume-skills", { params });
  return data;
}

export async function getEducation(resumeId) {
  const params = resumeId ? { resume_id: resumeId } : {};
  const { data } = await apiClient.get("/education", { params });
  return data;
}

export async function getExperience(resumeId) {
  const params = resumeId ? { resume_id: resumeId } : {};
  const { data } = await apiClient.get("/experience", { params });
  return data;
}

export async function getResumeAnalysis(resumeId) {
  const params = resumeId ? { resume_id: resumeId } : {};
  const { data } = await apiClient.get("/resume-analysis", { params });
  return data;
}

export async function reanalyzeResume(resumeId) {
  const params = resumeId ? { resume_id: resumeId } : {};
  const { data } = await apiClient.post("/reanalyze-resume", null, { params });
  return data;
}

// ─── Job routes (job_controller) ─────────────────────────────────────────────

export async function analyzeJob({ jobDescription, resumeId }) {
  const { data } = await apiClient.post("/analyze-job", {
    job_description: jobDescription,
    ...(resumeId ? { resume_id: resumeId } : {}),
  });
  return data;
}

export async function matchResume({ jobDescription, resumeId }) {
  const { data } = await apiClient.post("/match-resume", {
    job_description: jobDescription,
    ...(resumeId ? { resume_id: resumeId } : {}),
  });
  return data;
}

export async function mlMatch({ jobDescription, resumeId }) {
  const { data } = await apiClient.post("/ml-match", {
    job_description: jobDescription,
    ...(resumeId ? { resume_id: resumeId } : {}),
  });
  return data;
}

// ─── ATS routes (ats_controller) ─────────────────────────────────────────────

export async function getAtsScore(resumeId) {
  const { data } = await apiClient.post("/ats-score", {
    ...(resumeId ? { resume_id: resumeId } : {}),
  });
  return data;
}
