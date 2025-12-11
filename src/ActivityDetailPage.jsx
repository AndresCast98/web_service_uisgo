import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import "./App.css";
import PortalLayout from "./PortalLayout";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function formatAnswer(answer, options) {
  if (!answer) return "--";
  if (answer.text) return answer.text;
  if (Array.isArray(answer.selected) && Array.isArray(options)) {
    return answer.selected
      .map((index) => options[index] ?? `Opción ${index + 1}`)
      .join(", ");
  }
  return JSON.stringify(answer);
}

export default function ActivityDetailPage() {
  const { activityId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("uisgo_user") || "{}");
    } catch {
      return {};
    }
  });
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const token = localStorage.getItem("uisgo_token");
  const fallbackGroupId = activity?.target_groups?.[0]?.id;
  const originateGroupId = location.state?.groupId || fallbackGroupId;

  useEffect(() => {
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    fetchCurrentUser();
    fetchActivityDetail();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activityId]);

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

  const fetchActivityDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/activities/${activityId}`, {
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
        throw new Error(data.detail || "No se pudo obtener el detalle de la actividad.");
      }
      const data = await response.json();
      setActivity(data);
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

  const submissions = useMemo(() => activity?.submissions ?? [], [activity]);

  return (
    <PortalLayout
      user={user}
      onLogout={handleLogout}
      onNavigateProfile={() => navigate("/profile")}
      onNavigateGroups={() => navigate(originateGroupId ? `/groups/${originateGroupId}` : "/groups")}
      onNavigateStats={() => navigate("/stats")}
      activeSection="groups"
    >
      <section className="activity-detail-card">
        <div className="groups-header detail-header">
          <div className="header-left">
            <button
              type="button"
              className="secondary-button"
              onClick={() => navigate(originateGroupId ? `/groups/${originateGroupId}` : "/groups")}
            >
              ← Volver al grupo
            </button>
            <h2>{activity?.title || "Detalle de la actividad"}</h2>
          </div>
        </div>

        {loading ? (
          <div className="table-placeholder">Cargando actividad...</div>
        ) : error ? (
          <div className="feedback error">{error}</div>
        ) : !activity ? (
          <div className="table-placeholder">No se encontró la actividad solicitada.</div>
        ) : (
          <>
            <div className="activity-summary">
              <div>
                <h3>Estado</h3>
                <span className={`status-pill status-${activity.status}`}>{activity.status}</span>
              </div>
              <div>
                <h3>Coins al completar</h3>
                <p>{activity.coins_on_complete}</p>
              </div>
              <div>
                <h3>Disponibilidad</h3>
                <p>
                  <strong>Inicio:</strong> {activity.start_at ? new Date(activity.start_at).toLocaleString() : "--"}
                  <br />
                  <strong>Fin:</strong> {activity.end_at ? new Date(activity.end_at).toLocaleString() : "--"}
                </p>
              </div>
            </div>

            <div className="activity-question-card">
              <h3>Pregunta</h3>
              <p className="question-text">{activity.q_text}</p>
              {Array.isArray(activity.q_options) && activity.q_options.length > 0 && (
                <ol className="question-options">
                  {activity.q_options.map((opt, idx) => {
                    const isCorrect = Array.isArray(activity.q_correct) && activity.q_correct.includes(idx);
                    return (
                      <li key={idx} className={isCorrect ? "correct-option" : undefined}>
                        {opt} {isCorrect && <span className="option-tag">Correcta</span>}
                      </li>
                    );
                  })}
                </ol>
              )}
            </div>

            <section className="submissions-section">
              <div className="activities-header">
                <h3>Respuestas de estudiantes</h3>
                <p>Revisa quiénes han respondido y su estado.</p>
              </div>

              {submissions.length === 0 ? (
                <div className="table-placeholder">Aún no hay respuestas para esta actividad.</div>
              ) : (
                <div className="submissions-table-wrapper">
                  <table className="submissions-table">
                    <thead>
                      <tr>
                        <th>Estudiante</th>
                        <th>Correo</th>
                        <th>Respuesta</th>
                        <th>Estado</th>
                        <th>Coins</th>
                        <th>Fecha</th>
                      </tr>
                    </thead>
                    <tbody>
                      {submissions.map((submission) => (
                        <tr key={submission.id}>
                          <td>{submission.student_name || "Sin nombre"}</td>
                      <td>{submission.student_email}</td>
                      <td>{formatAnswer(submission.answer, activity.q_options)}</td>
                      <td>
                        <span className={`status-pill status-${submission.status}`}>
                          {submission.status}
                        </span>
                      </td>
                          <td>{submission.awarded_coins}</td>
                          <td>{new Date(submission.submitted_at).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </section>
    </PortalLayout>
  );
}
