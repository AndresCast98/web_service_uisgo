import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import "./App.css";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [forgotLoading, setForgotLoading] = useState(false);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [resetToken, setResetToken] = useState(null);

  const isLogin = mode === "login";
  const logoSrc = `${process.env.PUBLIC_URL || ""}/logo.png`;

  useEffect(() => {
    const token = localStorage.getItem("uisgo_token");
    if (token) {
      navigate("/groups", { replace: true });
    }
  }, [navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const clearMessages = () => {
    setError(null);
    setFeedback(null);
    setResetToken(null);
  };

  const switchMode = (nextMode) => {
    if (nextMode === mode) return;
    setMode(nextMode);
    setForm({ email: "", password: "", full_name: "" });
    setShowPassword(false);
    clearMessages();
  };

  const persistSession = (data) => {
    localStorage.setItem("uisgo_token", data.access_token);
    localStorage.setItem(
      "uisgo_user",
      JSON.stringify({
        email: data.email,
        full_name: data.full_name,
        role: data.role,
      })
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.email || !form.password) {
      setError("Ingrese su correo y contraseña.");
      return;
    }
    if (!isLogin && !form.full_name.trim()) {
      setError("Ingrese su nombre completo.");
      return;
    }

    clearMessages();
    setLoading(true);
    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      const payload = isLogin
        ? { email: form.email, password: form.password }
        : {
            email: form.email,
            password: form.password,
            full_name: form.full_name.trim(),
          };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const detail =
          data.detail ||
          (isLogin ? "Error al iniciar sesión." : "Error al crear la cuenta.");
        throw new Error(detail);
      }

      const data = await response.json();
      persistSession(data);
      setFeedback(
        isLogin
          ? "Ingreso exitoso. Redirigiendo al panel..."
          : "Cuenta creada con éxito. Redirigiendo al panel..."
      );
      setTimeout(() => navigate("/groups", { replace: true }), 600);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (event) => {
    event.preventDefault();
    if (!form.email) {
      setError("Ingrese su correo para recuperar la contraseña.");
      return;
    }

    clearMessages();
    setForgotLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = data.detail || "Error al solicitar el cambio de contraseña.";
        throw new Error(detail);
      }

      setFeedback(data.message || "Revisa tu correo para continuar con el proceso.");
      if (data.reset_token) {
        setResetToken(data.reset_token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setForgotLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <img src={logoSrc} alt="UIS logo" />
        </div>
        <div className="login-form">
          <header className="login-header">
            <h1>{isLogin ? "Bienvenido" : "Crear cuenta"}</h1>
            {isLogin ? (
              <p>
                ¿No tiene cuenta?{" "}
                <button
                  type="button"
                  className="link-button"
                  onClick={() => switchMode("register")}
                >
                  Cree una
                </button>
              </p>
            ) : (
              <p>
                ¿Ya tiene cuenta?{" "}
                <button
                  type="button"
                  className="link-button"
                  onClick={() => switchMode("login")}
                >
                  Ingrese
                </button>
              </p>
            )}
          </header>

          <form className="form-body" onSubmit={handleSubmit}>
            <label className="input-label" htmlFor="email">
              Correo
            </label>
            <input
              className="text-input"
              type="email"
              id="email"
              name="email"
              placeholder="Correo@gmail.com"
              autoComplete="email"
              value={form.email}
              onChange={handleChange}
            />

            {!isLogin && (
              <>
                <label className="input-label" htmlFor="full_name">
                  Nombre completo
                </label>
                <input
                  className="text-input"
                  type="text"
                  id="full_name"
                  name="full_name"
                  placeholder="Nombre y apellido"
                  autoComplete="name"
                  value={form.full_name}
                  onChange={handleChange}
                />
              </>
            )}

            <label className="input-label" htmlFor="password">
              Contraseña
            </label>
            <div className="password-wrapper">
              <input
                className="text-input"
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                placeholder="Digite la contraseña"
                autoComplete={isLogin ? "current-password" : "new-password"}
                value={form.password}
                onChange={handleChange}
              />
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowPassword((prev) => !prev)}
              >
                {showPassword ? "Ocultar" : "Mostrar"}
              </button>
            </div>

            {isLogin && (
              <div className="form-links">
                <button
                  type="button"
                  className="link-button"
                  onClick={handleForgotPassword}
                  disabled={forgotLoading}
                >
                  {forgotLoading ? "Enviando..." : "¿Olvidó la contraseña?"}
                </button>
              </div>
            )}

            {error && <div className="feedback error">{error}</div>}
            {feedback && <div className="feedback success">{feedback}</div>}
            {resetToken && isLogin && (
              <div className="feedback info">
                Token temporal para pruebas: <code>{resetToken}</code>
              </div>
            )}

            <button className="submit-button" type="submit" disabled={loading}>
              {loading
                ? isLogin
                  ? "Ingresando..."
                  : "Creando..."
                : isLogin
                ? "Ingresar"
                : "Crear cuenta"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
