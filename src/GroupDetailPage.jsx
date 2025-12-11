import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import "./App.css";
import PortalLayout from "./PortalLayout";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const emptyActivityForm = {
  title: "",
  description: "",
  q_text: "",
  options: ["", ""],
  correctIndex: 0,
  coins_on_complete: 0,
  start_at: "",
  end_at: "",
};

export default function GroupDetailPage() {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("uisgo_user") || "{}");
    } catch {
      return {};
    }
  });
  const [group, setGroup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [qrUrl, setQrUrl] = useState(null);
  const [showInvite, setShowInvite] = useState(false);

  const [activities, setActivities] = useState([]);
  const [activitiesLoading, setActivitiesLoading] = useState(true);
  const [activitiesError, setActivitiesError] = useState(null);

  const [activityForm, setActivityForm] = useState(() => ({
    ...emptyActivityForm,
    options: [...emptyActivityForm.options],
  }));
  const [formError, setFormError] = useState(null);
  const [formFeedback, setFormFeedback] = useState(null);
  const [creating, setCreating] = useState(false);

  const token = localStorage.getItem("uisgo_token");

  useEffect(() => {
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    fetchCurrentUser();
    fetchGroupDetail();
    fetchGroupActivities();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupId]);

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

  const fetchGroupDetail = async () => {
    setLoading(true);
    setError(null);
    setShowInvite(false);
    setQrUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });
    try {
      const response = await fetch(`${API_BASE_URL}/groups/${groupId}`, {
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
        throw new Error(data.detail || "No se pudo obtener el detalle del grupo.");
      }
      const data = await response.json();
      setGroup(data);
      if (data.qr_png) {
        fetchQrImage(data.qr_png);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchQrImage = async (endpoint) => {
    try {
      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) return;
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      setQrUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return objectUrl;
      });
    } catch (err) {
      console.error("No se pudo cargar el QR del grupo", err);
    }
  };

  const fetchGroupActivities = async () => {
    setActivitiesLoading(true);
    setActivitiesError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/activities/group/${groupId}`, {
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
        throw new Error(data.detail || "No se pudieron cargar las actividades.");
      }
      const data = await response.json();
      setActivities(data);
    } catch (err) {
      setActivitiesError(err.message);
    } finally {
      setActivitiesLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (qrUrl) {
        URL.revokeObjectURL(qrUrl);
      }
    };
  }, [qrUrl]);

  const handleLogout = () => {
    localStorage.removeItem("uisgo_token");
    localStorage.removeItem("uisgo_user");
    navigate("/login", { replace: true });
  };

  const handleOptionChange = (index, value) => {
    setFormError(null);
    setFormFeedback(null);
    setActivityForm((prev) => {
      const next = { ...prev, options: [...prev.options] };
      next.options[index] = value;
      return next;
    });
  };

  const handleAddOption = () => {
    setFormError(null);
    setFormFeedback(null);
    setActivityForm((prev) => {
      if (prev.options.length >= 6) return prev;
      return { ...prev, options: [...prev.options, ""] };
    });
  };

  const handleRemoveOption = (index) => {
    setFormError(null);
    setFormFeedback(null);
    setActivityForm((prev) => {
      if (prev.options.length <= 2) return prev;
      const nextOptions = prev.options.filter((_, i) => i !== index);
      let nextCorrect = prev.correctIndex;
      if (index === prev.correctIndex) {
        nextCorrect = 0;
      } else if (index < prev.correctIndex) {
        nextCorrect = prev.correctIndex - 1;
      }
      return { ...prev, options: nextOptions, correctIndex: nextCorrect };
    });
  };

  const resetActivityForm = () => {
    setActivityForm({
      ...emptyActivityForm,
      options: [...emptyActivityForm.options],
    });
    setFormError(null);
    setFormFeedback("Actividad creada correctamente.");
  };

  const handleCreateActivity = async (event) => {
    event.preventDefault();
    setFormError(null);
    setFormFeedback(null);

    const trimmedOptions = activityForm.options.map((opt) => opt.trim()).filter(Boolean);
    if (!activityForm.title.trim()) {
      setFormError("El título es obligatorio.");
      return;
    }
    if (!activityForm.q_text.trim()) {
      setFormError("La pregunta es obligatoria.");
      return;
    }
    if (trimmedOptions.length < 2) {
      setFormError("Debe proporcionar al menos dos opciones.");
      return;
    }
    if (activityForm.correctIndex >= trimmedOptions.length) {
      setFormError("Seleccione la respuesta correcta.");
      return;
    }

    setCreating(true);
    try {
      const payload = {
        title: activityForm.title.trim(),
        description: activityForm.description.trim() || null,
        type: "quiz_single",
        q_text: activityForm.q_text.trim(),
        q_type: "single",
        q_options: trimmedOptions,
        q_correct: [activityForm.correctIndex],
        coins_on_complete: Number(activityForm.coins_on_complete) || 0,
        start_at: activityForm.start_at ? new Date(activityForm.start_at).toISOString() : null,
        end_at: activityForm.end_at ? new Date(activityForm.end_at).toISOString() : null,
        target_group_ids: [groupId],
      };

      const response = await fetch(`${API_BASE_URL}/activities/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 401) {
        handleLogout();
        return;
      }
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo crear la actividad.");
      }

      resetActivityForm();
      fetchGroupActivities();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const handlePublish = async (activityId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/activities/${activityId}/publish`, {
        method: "POST",
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
        throw new Error(data.detail || "No se pudo publicar la actividad.");
      }
      fetchGroupActivities();
    } catch (err) {
      setActivitiesError(err.message);
    }
  };

  const formattedActivities = useMemo(() =>
    activities.map((activity) => ({
      ...activity,
      created_at: activity.created_at ? new Date(activity.created_at) : null,
      start_at: activity.start_at ? new Date(activity.start_at) : null,
      end_at: activity.end_at ? new Date(activity.end_at) : null,
    })),
    [activities]
  );

  return (
    <PortalLayout
      user={user}
      onLogout={handleLogout}
      onNavigateProfile={() => navigate("/profile")}
      onNavigateGroups={() => navigate("/groups")}
      onNavigateStats={() => navigate("/stats")}
      activeSection="groups"
    >
      <section className="group-detail-card">
        <div className="groups-header detail-header">
          <div className="header-left">
            <button
              type="button"
              className="secondary-button"
              onClick={() => navigate("/groups")}
            >
              ← Volver a grupos
            </button>
            <h2>{group?.name || "Detalle del grupo"}</h2>
          </div>
          <div className="detail-actions">
            {group?.invite_code && (
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowInvite((prev) => !prev)}
              >
                {showInvite ? "Ocultar QR" : "Mostrar QR"}
              </button>
            )}
          </div>
        </div>

        {loading ? (
          <div className="table-placeholder">Cargando información del grupo...</div>
        ) : error ? (
          <div className="feedback error">{error}</div>
        ) : !group ? (
          <div className="table-placeholder">
            No se encontró el grupo solicitado o no tiene permisos para verlo.
          </div>
        ) : (
          <>
            <div className="group-detail-summary">
              <div>
                <h3>Materia estudiantil</h3>
                <p>{group.subject || "Sin asignar"}</p>
              </div>
              <div>
                <h3>Estudiantes inscritos</h3>
                <p>{group.student_count}</p>
              </div>
              <div>
                <h3>Profesor responsable</h3>
                <p>
                  {group.owner_name || "Sin nombre"} <br />
                  <span className="group-subtitle">{group.owner_email}</span>
                </p>
              </div>
            </div>

            {group.invite_code && showInvite && (
              <div className="group-detail-invite">
                <h3>Invitación activa</h3>
                <div className="invite-code">
                  <span>{group.invite_code}</span>
                </div>
                {group.web_join && (
                  <a
                    className="link-button"
                    href={group.web_join}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Abrir landing
                  </a>
                )}
                {qrUrl ? (
                  <img src={qrUrl} alt="Código QR del grupo" className="invite-qr" />
                ) : (
                  <p className="group-subtitle">Generando vista previa del código QR...</p>
                )}
              </div>
            )}

            <section className="activities-section">
              <div className="activities-header">
                <h3>Actividades</h3>
                <p>Diseña y administra las actividades asignadas a este grupo.</p>
              </div>

              <div className="activity-layout">
                <form className="activity-form" onSubmit={handleCreateActivity}>
                  <h4>Crear nueva actividad</h4>
                  <label htmlFor="activity-title">Título</label>
                  <input
                    id="activity-title"
                    className="text-input"
                    value={activityForm.title}
                    onChange={(event) => {
                      setFormError(null);
                      setFormFeedback(null);
                      setActivityForm((prev) => ({ ...prev, title: event.target.value }));
                    }}
                    placeholder="Quiz sobre el tema..."
                  />

                  <label htmlFor="activity-description">Descripción</label>
                  <textarea
                    id="activity-description"
                    className="text-input"
                    value={activityForm.description}
                    onChange={(event) => {
                      setFormError(null);
                      setFormFeedback(null);
                      setActivityForm((prev) => ({ ...prev, description: event.target.value }));
                    }}
                    placeholder="Descripción breve (opcional)"
                  />

                  <label htmlFor="activity-question">Pregunta</label>
                  <textarea
                    id="activity-question"
                    className="text-input"
                    value={activityForm.q_text}
                    onChange={(event) => {
                      setFormError(null);
                      setFormFeedback(null);
                      setActivityForm((prev) => ({ ...prev, q_text: event.target.value }));
                    }}
                    placeholder="Escribe la pregunta para los estudiantes"
                  />

                  <div className="options-header">
                    <span>Opciones de respuesta</span>
                    <button type="button" className="link-button" onClick={handleAddOption}>
                      + Agregar opción
                    </button>
                  </div>

                  {activityForm.options.map((option, index) => (
                    <div key={index} className="option-row">
                      <input
                        className="text-input"
                        value={option}
                        onChange={(event) => handleOptionChange(index, event.target.value)}
                        placeholder={`Opción ${index + 1}`}
                      />
                      <label className="option-correct">
                        <input
                          type="radio"
                          name="correctOption"
                          checked={activityForm.correctIndex === index}
                          onChange={() => {
                            setFormError(null);
                            setFormFeedback(null);
                            setActivityForm((prev) => ({ ...prev, correctIndex: index }));
                          }}
                        />
                        Correcta
                      </label>
                      {activityForm.options.length > 2 && (
                        <button
                          type="button"
                          className="icon-button"
                          onClick={() => handleRemoveOption(index)}
                          aria-label="Eliminar opción"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}

                  <label htmlFor="activity-coins">Coins al completar</label>
                  <input
                    id="activity-coins"
                    type="number"
                    min="0"
                    className="text-input"
                    value={activityForm.coins_on_complete}
                    onChange={(event) => {
                      setFormError(null);
                      setFormFeedback(null);
                      setActivityForm((prev) => ({
                        ...prev,
                        coins_on_complete: event.target.value,
                      }));
                    }}
                  />

                  <div className="dates-row">
                    <div>
                      <label htmlFor="activity-start">Inicio</label>
                      <input
                        id="activity-start"
                        type="datetime-local"
                        className="text-input"
                        value={activityForm.start_at}
                        onChange={(event) => {
                          setFormError(null);
                          setFormFeedback(null);
                          setActivityForm((prev) => ({ ...prev, start_at: event.target.value }));
                        }}
                      />
                    </div>
                    <div>
                      <label htmlFor="activity-end">Fin</label>
                      <input
                        id="activity-end"
                        type="datetime-local"
                        className="text-input"
                        value={activityForm.end_at}
                        onChange={(event) => {
                          setFormError(null);
                          setFormFeedback(null);
                          setActivityForm((prev) => ({ ...prev, end_at: event.target.value }));
                        }}
                      />
                    </div>
                  </div>

                  {formError && <div className="feedback error">{formError}</div>}
                  {formFeedback && <div className="feedback success">{formFeedback}</div>}

                  <button className="primary-button" type="submit" disabled={creating}>
                    {creating ? "Creando..." : "Guardar actividad"}
                  </button>
                </form>

                <div className="activities-list">
                  <h4>Actividades creadas</h4>
                  {activitiesLoading ? (
                    <div className="table-placeholder">Cargando actividades...</div>
                  ) : activitiesError ? (
                    <div className="feedback error">{activitiesError}</div>
                  ) : formattedActivities.length === 0 ? (
                    <div className="table-placeholder">Aún no hay actividades.</div>
                  ) : (
                    formattedActivities.map((activity) => (
                      <div key={activity.id} className="activity-card">
                        <div className="activity-header">
                          <button
                            type="button"
                            className="activity-title-button"
                            onClick={() => navigate(`/activities/${activity.id}`, { state: { groupId } })}
                          >
                            {activity.title}
                          </button>
                          <span className={`status-pill status-${activity.status}`}>
                            {activity.status}
                          </span>
                        </div>
                        {activity.description && <p>{activity.description}</p>}
                        <ul className="activity-meta">
                          <li>
                            <strong>Coins:</strong> {activity.coins_on_complete}
                          </li>
                          <li>
                            <strong>Inicio:</strong>{" "}
                            {activity.start_at ? activity.start_at.toLocaleString() : "--"}
                          </li>
                          <li>
                            <strong>Fin:</strong>{" "}
                            {activity.end_at ? activity.end_at.toLocaleString() : "--"}
                          </li>
                        </ul>
                        <div className="activity-actions">
                          {activity.status !== "published" && (
                            <button
                              type="button"
                              className="link-button"
                              onClick={() => handlePublish(activity.id)}
                            >
                              Publicar
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </section>
          </>
        )}
      </section>
    </PortalLayout>
  );
}
