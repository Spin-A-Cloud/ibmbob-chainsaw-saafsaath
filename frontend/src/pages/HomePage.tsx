import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import styles from "./HomePage.module.css";

export default function HomePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.logo}>
          <span>♻️</span>
          <span className={styles.logoText}>SaafSaath</span>
        </div>
        <button className={styles.logoutBtn} onClick={handleLogout}>
          Log out
        </button>
      </header>

      <main className={styles.main}>
        <div className={styles.greeting}>
          <h2 className={styles.hi}>Hi, {user?.name ?? "there"} 👋</h2>
          <p className={styles.sub}>
            You are signed in as a{" "}
            <span className={styles.role}>{user?.role}</span>.
          </p>
        </div>

        <div className={styles.cards}>
          <div className={styles.card}>
            <span className={styles.cardIcon}>📦</span>
            <h3>Schedule a Pickup</h3>
            <p>Upload your items, choose a slot, and get a quote from our scrap partners.</p>
            <button className={styles.cardBtn} disabled>Coming soon</button>
          </div>
          <div className={styles.card}>
            <span className={styles.cardIcon}>💬</span>
            <h3>My Requests</h3>
            <p>Track the status of your submitted pickup requests and quotations.</p>
            <button className={styles.cardBtn} disabled>Coming soon</button>
          </div>
          <div className={styles.card}>
            <span className={styles.cardIcon}>💳</span>
            <h3>Payments</h3>
            <p>View your payment history and receipts.</p>
            <button className={styles.cardBtn} disabled>Coming soon</button>
          </div>
        </div>
      </main>
    </div>
  );
}
