import { useState } from "react";

import "./App.css";

export default function PortalLayout({
  user,
  onLogout,
  onNavigateProfile,
  onNavigateGroups = () => {},
  onNavigateStats = () => {},
  activeSection = "groups",
  children,
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);
  const toggleUserMenu = () => setUserMenuOpen((prev) => !prev);

  return (
    <div className="portal-shell">
      <aside className={`portal-sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar-section">
          <h4>Gestión Usuarios</h4>
          <button
            type="button"
            className={activeSection === "stats" ? "active" : ""}
            onClick={() => {
              setSidebarOpen(false);
              onNavigateStats?.();
            }}
          >
            Estadísticas
          </button>
          <button type="button" disabled>
            Análisis
          </button>
          <button type="button" disabled>
            Moderación
          </button>
        </div>
        <div className="sidebar-section">
          <h4>Gestión Contenido</h4>
          <button type="button" disabled>
            Preguntas
          </button>
          <button type="button" disabled>
            Actividades
          </button>
          <button
            type="button"
            className={activeSection === "groups" ? "active" : ""}
            onClick={() => {
              setSidebarOpen(false);
              onNavigateGroups?.();
            }}
          >
            Grupos
          </button>
        </div>
      </aside>

      <div className="portal-main">
        <header className="portal-topbar">
          <button
            type="button"
            className="icon-button"
            aria-label={sidebarOpen ? "Cerrar menú" : "Abrir menú"}
            onClick={toggleSidebar}
          >
            {sidebarOpen ? "✕" : "☰"}
          </button>

          <div className="topbar-actions">
            <span className="user-name">{user?.full_name || "Usuario"}</span>
            <div className="user-avatar">
              <button
                type="button"
                className="icon-button avatar-button"
                onClick={toggleUserMenu}
                aria-label="Abrir menú de usuario"
              >
                <svg
                  className="avatar-icon"
                  viewBox="0 0 24 24"
                  focusable="false"
                  aria-hidden="true"
                >
                  <path
                    d="M12 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 12c4.42 0 8 2.24 8 5v1H4v-1c0-2.76 3.58-5 8-5z"
                    fill="currentColor"
                  />
                </svg>
              </button>
              {userMenuOpen && (
                <div className="user-menu">
                  <button
                    type="button"
                    onClick={() => {
                      setUserMenuOpen(false);
                      onNavigateProfile();
                    }}
                  >
                    Editar perfil
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setUserMenuOpen(false);
                      onLogout();
                    }}
                  >
                    Cerrar sesión
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="portal-content">{children}</main>
      </div>
    </div>
  );
}
