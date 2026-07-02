import { NavLink, Link } from "react-router-dom";
import { Activity, LogOut, UserCircle2 } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/upload", label: "Upload" },
  { to: "/job-description", label: "Job" },
  { to: "/results", label: "Results" },
  { to: "/resumes", label: "Resumes" },
  { to: "/history", label: "History" },
];

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header
      className="sticky top-0 z-50 border-b border-ink-700/60 backdrop-blur-xl"
      style={{ background: "var(--surface-overlay)", boxShadow: "var(--nav-shadow)" }}
    >
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="group flex shrink-0 items-center gap-2.5">
          <span className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-ink-600 bg-ink-900 shadow-sm transition-all group-hover:border-signal-500/40 group-hover:shadow-[0_0_20px_-4px_var(--hero-glow)]">
            <Activity className="h-4 w-4 text-signal-500" strokeWidth={2.5} />
          </span>
          <span className="font-display text-[15px] font-semibold tracking-tight text-ink-100">
            Resume<span className="text-signal-500">.</span>Analyzer
          </span>
        </Link>

        <div className="hidden items-center gap-0.5 lg:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `relative rounded-lg px-3 py-2 font-mono text-[11.5px] uppercase tracking-wider transition-all ${
                  isActive
                    ? "bg-signal-500/10 text-signal-500"
                    : "text-ink-300 hover:bg-ink-800/80 hover:text-ink-100"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <ThemeToggle />
          {user && (
            <div className="hidden items-center gap-2 rounded-lg border border-ink-700/80 bg-ink-900/60 px-3 py-2 text-ink-300 md:flex">
              <UserCircle2 className="h-4 w-4 text-signal-500" />
              <span className="max-w-36 truncate font-mono text-[11px] uppercase tracking-wider">{user.full_name || user.email}</span>
            </div>
          )}
          <Link to="/upload" className="btn-primary hidden px-4 py-2 text-[13px] sm:inline-flex">
            Run Analysis
          </Link>
          <button
            type="button"
            onClick={handleLogout}
            className="hidden items-center gap-2 rounded-lg border border-ink-600 bg-ink-900/50 px-4 py-2 font-display text-[13px] font-semibold text-ink-200 transition-all hover:border-ink-400 hover:bg-ink-800 sm:inline-flex"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </nav>

      <div className="flex overflow-x-auto border-t border-ink-700/60 lg:hidden">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex-shrink-0 px-4 py-2.5 font-mono text-[10px] uppercase tracking-wider transition-colors ${
                isActive ? "border-b-2 border-signal-500 text-signal-500" : "text-ink-400"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
        <button
          type="button"
          onClick={handleLogout}
          className="flex-shrink-0 px-4 py-2.5 font-mono text-[10px] uppercase tracking-wider text-rose-signal"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
