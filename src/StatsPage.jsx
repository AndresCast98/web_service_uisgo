import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import "./App.css";
import PortalLayout from "./PortalLayout";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function StatsPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("uisgo_user") || "{}");
    } catch {
      return {};
    }
  });
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const token = localStorage.getItem("uisgo_token");

  useEffect(() => {
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    fetchCurrentUser();
    fetchStats();
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
      console.error(err);
    }
  };

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/my`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.status === 401) {
        handleLogout();
        return;
      }
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo cargar la información de estadísticas.");
      }
      const data = await response.json();
      setSummary(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("uisgo_token");
    localStorage.removeItem("uisgo_user");
    navigate("/login", { replace: true });
  };

  const totalAccuracy = useMemo(() => {
    if (!summary || summary.total_submissions === 0) return 0;
    const correct = summary.groups.reduce((acc, g) => acc + Math.round((g.accuracy / 100) * g.total_submissions), 0);
    return Number(((correct / summary.total_submissions) * 100).toFixed(2));
  }, [summary]);

  return (
    <PortalLayout
      user={user}
      onLogout={handleLogout}
      onNavigateProfile={() => navigate("/profile")}
      onNavigateGroups={() => navigate("/groups")}
      onNavigateStats={() => navigate("/stats")}
      activeSection="stats"
    >
      <section className="stats-card">
        <div className="stats-header">
          <h2>Estadísticas de mis grupos</h2>
          <button type="button" className="secondary-button" onClick={fetchStats} disabled={loading}>
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>

        {loading ? (
          <div className="table-placeholder">Calculando estadísticas...</div>
        ) : error ? (
          <div className="feedback error">{error}</div>
        ) : !summary ? (
          <div className="table-placeholder">No se pudo obtener información por el momento.</div>
        ) : (
          <>
            <div className="stats-summary-grid">
              <div className="stats-summary-card">
                <span className="summary-label">Grupos</span>
                <span className="summary-value">{summary.total_groups}</span>
              </div>
              <div className="stats-summary-card">
                <span className="summary-label">Estudiantes</span>
                <span className="summary-value">{summary.total_students}</span>
              </div>
              <div className="stats-summary-card">
                <span className="summary-label">Actividades</span>
                <span className="summary-value">{summary.total_activities}</span>
              </div>
              <div className="stats-summary-card">
                <span className="summary-label">Respuestas</span>
                <span className="summary-value">{summary.total_submissions}</span>
              </div>
              <div className="stats-summary-card">
                <span className="summary-label">Precisión total</span>
                <span className="summary-value">{totalAccuracy}%</span>
              </div>
              <div className="stats-summary-card">
                <span className="summary-label">Actualizado</span>
                <span className="summary-value">
                  {new Date(summary.generated_at).toLocaleString()}
                </span>
              </div>
            </div>

            <div className="stats-groups-list">
              {summary.groups.length === 0 ? (
                <div className="table-placeholder">
                  Todavía no tienes grupos con estudiantes registrados.
                </div>
              ) : (
                summary.groups.map((group) => (
                  <div key={group.group_id} className="stats-group-card">
                    <div className="stats-group-header">
                      <h3>{group.group_name}</h3>
                      <button
                        type="button"
                        className="link-button"
                        onClick={() => navigate(`/groups/${group.group_id}`)}
                      >
                        Ver grupo
                      </button>
                    </div>
                    <div className="stats-group-grid">
                      <div>
                        <span className="summary-label">Estudiantes</span>
                        <span className="summary-value">{group.total_students}</span>
                      </div>
                      <div>
                        <span className="summary-label">Respondieron</span>
                        <span className="summary-value">
                          {group.responded_students} ({group.response_rate}%)
                        </span>
                      </div>
                      <div>
                        <span className="summary-label">Actividades</span>
                        <span className="summary-value">{group.total_activities}</span>
                      </div>
                      <div>
                        <span className="summary-label">Respuestas</span>
                        <span className="summary-value">{group.total_submissions}</span>
                      </div>
                      <div>
                        <span className="summary-label">Precisión</span>
                        <span className="summary-value">{group.accuracy}%</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </section>
    </PortalLayout>
  );
}
