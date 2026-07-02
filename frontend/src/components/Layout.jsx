import NavBar from "./NavBar";
import Footer from "./Footer";

export default function Layout({ children }) {
  return (
    <div className="relative flex min-h-screen flex-col bg-ink-950">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="hero-orb hero-orb--primary -left-32 top-0 h-96 w-96 opacity-40" />
        <div className="hero-orb hero-orb--secondary -right-24 bottom-0 h-80 w-80 opacity-30" />
      </div>
      <NavBar />
      <main className="relative flex-1">{children}</main>
      <Footer />
    </div>
  );
}
