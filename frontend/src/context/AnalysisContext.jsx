import { createContext, useContext, useMemo, useState, useCallback } from "react";

const AnalysisContext = createContext(null);

const initialState = {
  resumeId: null,
  resumeFile: null,
  resumeFilename: null,
  parsedResume: null,
  jdId: null,
  jobTitle: "",
  company: "",
  jobDescriptionText: "",
  result: null,
};

export function AnalysisProvider({ children }) {
  const [state, setState] = useState(initialState);

  const setResume = useCallback((resumeId, file, parsedResume = null, filename = null) => {
    setState((prev) => ({
      ...prev,
      resumeId,
      resumeFile: file,
      resumeFilename: filename ?? file?.name ?? parsedResume?.filename ?? prev.resumeFilename,
      parsedResume,
    }));
  }, []);

  const setJobDescription = useCallback((jdId, { jobTitle, company, descriptionText }) => {
    setState((prev) => ({
      ...prev,
      jdId,
      jobTitle: jobTitle ?? prev.jobTitle,
      company: company ?? prev.company,
      jobDescriptionText: descriptionText ?? prev.jobDescriptionText,
    }));
  }, []);

  const setResult = useCallback((result) => {
    setState((prev) => ({ ...prev, result }));
  }, []);

  const reset = useCallback(() => setState(initialState), []);

  const value = useMemo(
    () => ({ ...state, setResume, setJobDescription, setResult, reset }),
    [state, setResume, setJobDescription, setResult, reset]
  );

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>;
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext);
  if (!ctx) {
    throw new Error("useAnalysis must be used within an AnalysisProvider");
  }
  return ctx;
}
