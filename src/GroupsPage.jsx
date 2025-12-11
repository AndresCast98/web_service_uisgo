import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import "./App.css";
import PortalLayout from "./PortalLayout";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const emptyModalState = {
  open: false,
  mode: "create",
  group: null,
};

const emptyGroupForm = {
  name: "",
  subject: "",
};

export default function GroupsPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("uisgo_user") || "{}");
    } catch {
      return {};
    }
  });
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [modalState, setModalState] = useState(emptyModalState);
  const [groupForm, setGroupForm] = useState(emptyGroupForm);
  const [submitting, setSubmitting] = useState(false);

  const token = localStorage.getItem("uisgo_token");

  useEffect(() => {
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    fetchCurrentUser();
    fetchGroups();
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

  const fetchGroups = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/groups`, {
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
        throw new Error(data.detail || "No se pudo cargar la lista de grupos.");
      }
      const data = await response.json();
      setGroups(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredGroups = useMemo(() => {
    if (!search.trim()) return groups;
    const term = search.trim().toLowerCase();
    return groups.filter(
      (group) =>
        group.name.toLowerCase().includes(term) ||
        (group.subject || "").toLowerCase().includes(term) ||
        (group.owner_email || "").toLowerCase().includes(term)
    );
  }, [groups, search]);

  const handleSearchChange = (event) => {
    setSearch(event.target.value);
  };

  const handleLogout = () => {
    localStorage.removeItem("uisgo_token");
    localStorage.removeItem("uisgo_user");
    navigate("/login", { replace: true });
  };

  const openCreateModal = () => {
    setModalState({ open: true, mode: "create", group: null });
    setGroupForm(emptyGroupForm);
  };

  const openEditModal = (group) => {
    setModalState({ open: true, mode: "edit", group });
    setGroupForm({
      name: group.name,
      subject: group.subject || "",
    });
  };

  const closeModal = () => {
    setModalState(emptyModalState);
    setGroupForm(emptyGroupForm);
    setSubmitting(false);
  };

  const handleGroupFormChange = (event) => {
    const { name, value } = event.target;
    setGroupForm((prev) => ({ ...prev, [name]: value }));
  };

  const submitGroupForm = async (event) => {
    event.preventDefault();
    if (!groupForm.name.trim()) return;
    setSubmitting(true);
    try {
      const isEdit = modalState.mode === "edit";
      const url = isEdit
        ? `${API_BASE_URL}/groups/${modalState.group.id}`
        : `${API_BASE_URL}/groups`;
      const method = isEdit ? "PUT" : "POST";
      const payload = {
        name: groupForm.name.trim(),
        subject: groupForm.subject.trim() || null,
      };

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(
          data.detail ||
            (isEdit
              ? "No se pudo actualizar el grupo."
              : "No se pudo crear el grupo.")
        );
      }

      await fetchGroups();
      closeModal();
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  const handleDeleteGroup = async (group) => {
    const confirmed = window.confirm(
      `¿Confirma eliminar el grupo "${group.name}"? Esta acción no se puede deshacer.`
    );
    if (!confirmed) return;

    try {
      const response = await fetch(`${API_BASE_URL}/groups/${group.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok && response.status !== 204) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo eliminar el grupo.");
      }
      await fetchGroups();
    } catch (err) {
      setError(err.message);
    }
  };

  const goToGroupDetail = (groupId) => {
    navigate(`/groups/${groupId}`);
  };

  return (
    <PortalLayout
      user={user}
      onLogout={handleLogout}
      onNavigateProfile={() => navigate("/profile")}
      onNavigateGroups={() => navigate("/groups")}
      onNavigateStats={() => navigate("/stats")}
      activeSection="groups"
    >
      <section className="groups-card">
        <div className="groups-header">
          <h2>Grupos</h2>
          <button
            type="button"
            className="icon-button"
            aria-label="Cerrar panel"
            onClick={() => navigate("/")}
          >
            ✕
          </button>
        </div>

        <div className="groups-search">
          <div className="search-box">
            <span aria-hidden="true">🔍</span>
            <input
              type="search"
              placeholder="Buscar grupo..."
              value={search}
              onChange={handleSearchChange}
            />
          </div>
          <button type="button" className="secondary-button">
            Filtros
          </button>
          <button type="button" className="primary-button" onClick={openCreateModal}>
            + Crear Grupo
          </button>
        </div>

        {error && <div className="feedback error">{error}</div>}

        <div className="groups-table-wrapper">
          {loading ? (
            <div className="table-placeholder">Cargando grupos...</div>
          ) : filteredGroups.length === 0 ? (
            <div className="table-placeholder">
              No se encontraron grupos con los criterios actuales.
            </div>
          ) : (
            <table className="groups-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Materia estudiantil</th>
                  <th>Cantidad de estudiantes</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredGroups.map((group) => (
                  <tr key={group.id}>
                    <td>
                      <button
                        type="button"
                        className="group-name"
                        onClick={() => goToGroupDetail(group.id)}
                      >
                        <span className="group-title">{group.name}</span>
                        <span className="group-subtitle">{group.owner_email}</span>
                      </button>
                    </td>
                    <td>{group.subject || "Sin asignar"}</td>
                    <td>{group.student_count}</td>
                    <td className="table-actions">
                      <button
                        type="button"
                        className="icon-button"
                        onClick={() => handleDeleteGroup(group)}
                        aria-label="Eliminar grupo"
                      >
                        🗑️
                      </button>
                      <button
                        type="button"
                        className="icon-button"
                        onClick={() => openEditModal(group)}
                        aria-label="Editar grupo"
                      >
                        ✏️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>

      {modalState.open && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <form className="modal-card" onSubmit={submitGroupForm}>
            <h3>{modalState.mode === "edit" ? "Editar grupo" : "Crear grupo"}</h3>
            <label className="input-label" htmlFor="group-name">
              Nombre del grupo
            </label>
            <input
              id="group-name"
              name="name"
              className="text-input"
              value={groupForm.name}
              onChange={handleGroupFormChange}
              placeholder="Introduce el nombre"
              required
            />

            <label className="input-label" htmlFor="group-subject">
              Materia estudiantil
            </label>
            <input
              id="group-subject"
              name="subject"
              className="text-input"
              value={groupForm.subject}
              onChange={handleGroupFormChange}
              placeholder="Arquitectura de computadores"
            />

            <div className="modal-actions">
              <button type="button" className="secondary-button" onClick={closeModal}>
                Cancelar
              </button>
              <button type="submit" className="primary-button" disabled={submitting}>
                {submitting
                  ? modalState.mode === "edit"
                    ? "Guardando..."
                    : "Creando..."
                  : "Guardar"}
              </button>
            </div>
          </form>
        </div>
      )}
    </PortalLayout>
  );
}
