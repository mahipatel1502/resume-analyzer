import { BrowserRouter, Navigate, Outlet, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import { RequireAuth, PublicOnlyRoute } from "./components/RequireAuth";
import { AnalysisProvider } from "./context/AnalysisContext";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import Home from "./pages/Home";
import ResumeUpload from "./pages/ResumeUpload";
import JobDescription from "./pages/JobDescription";
import ResultsDashboard from "./pages/ResultsDashboard";
import AnalysisHistory from "./pages/AnalysisHistory";
import ResumeLibrary from "./pages/ResumeLibrary";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

function ProtectedLayout() {
  return <Layout><Outlet /></Layout>;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AnalysisProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<PublicOnlyRoute />}>
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
              </Route>

              <Route element={<RequireAuth />}>
                <Route element={<ProtectedLayout />}>
                  <Route path="/" element={<Home />} />
                  <Route path="/upload" element={<ResumeUpload />} />
                  <Route path="/job-description" element={<JobDescription />} />
                  <Route path="/results" element={<ResultsDashboard />} />
                  <Route path="/resumes" element={<ResumeLibrary />} />
                  <Route path="/history" element={<AnalysisHistory />} />
                </Route>
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </AnalysisProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
