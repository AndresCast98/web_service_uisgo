import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import "./App.css";
import PortalLayout from "./PortalLayout";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("uisgo_user") || "{}");
    } catch {
      return {};
    }
  });
  const [fullName, setFullName] = useState(user.full_name || "");
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const token = localStorage.getItem("uisgo_token");

  useEffect(() => {
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    fetchCurrentUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.status === 401) {
        handleLogout();
        return;
      }
      if (!response.ok) {
        throw new Error("No se pudo obtener la información del usuario.");
      }
      const data = await response.json();
      setUser(data);
      setFullName(data.full_name || "");
      localStorage.setItem(
        "uisgo_user",
        JSON.stringify({
          email: data.email,
          full_name: data.full_name,
          role: data.role,
          created_at: data.created_at,
        })
      );
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("uisgo_token");
    localStorage.removeItem("uisgo_user");
    navigate("/login", { replace: true });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!fullName.trim()) {
      setError("El nombre no puede estar vacío.");
      return;
    }
    setError(null);
    setStatus(null);
    setSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ full_name: fullName.trim() }),
      });
      if (response.status === 401) {
        handleLogout();
        return;
      }
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo actualizar el perfil.");
      }
      const updated = await response.json();
      setUser(updated);
      localStorage.setItem(
        "uisgo_user",
        JSON.stringify({
          email: updated.email,
          full_name: updated.full_name,
          role: updated.role,
          created_at: updated.created_at,
        })
      );
      setStatus("Nombre actualizado correctamente.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <PortalLayout
      user={user}
      onLogout={handleLogout}
      onNavigateProfile={() => {}}
      onNavigateGroups={() => navigate("/groups")}
      onNavigateStats={() => navigate("/stats")}
      activeSection="profile"
    >
      <section className="profile-card">
        <h2>Perfil del usuario</h2>
        <form className="profile-form" onSubmit={handleSubmit}>
          <label htmlFor="full_name">Nombre completo</label>
          <input
            id="full_name"
            name="full_name"
            className="text-input"
            value={fullName}
            onChange={(event) => {
              setStatus(null);
              setError(null);
              setFullName(event.target.value);
            }}
            placeholder="Nombre y apellido"
          />

          <label htmlFor="email">Correo</label>
          <input
            id="email"
            className="text-input read-only"
            value={user.email || ""}
            disabled
          />

          <label htmlFor="role">Rol</label>
          <input
            id="role"
            className="text-input read-only"
            value={user.role || ""}
            disabled
          />

          {error && <div className="feedback error">{error}</div>}
          {status && <div className="feedback success">{status}</div>}

          <div className="profile-actions">
            <button className="secondary-button" type="button" onClick={() => navigate("/groups")}>Regresar</button>
            <button className="primary-button" type="submit" disabled={saving}>
              {saving ? "Guardando..." : "Guardar cambios"}
            </button>
          </div>
        </form>

        <div className="profile-summary">
          <div>
            <h4>Cuenta creada</h4>
            <p>{user.created_at ? new Date(user.created_at).toLocaleDateString() : "--"}</p>
          </div>
          <div>
            <h4>Correo</h4>
            <p>{user.email || "Sin registrar"}</p>
          </div>
          <div>
            <h4>Rol</h4>
            <p>{user.role || "Desconocido"}</p>
          </div>
        </div>
      </section>
    </PortalLayout>
  );
}
