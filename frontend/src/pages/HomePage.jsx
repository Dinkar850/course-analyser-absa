import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setMessage("Analyzing video...");

    try {
      // Hit your Flask backend POST route
      const response = await fetch("http://127.0.0.1:5000/collect/youtube", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url, max_results: 50 }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to analyze video");
      }

      console.log(data);
      // The backend returns { video_id, message, count }
      const videoId = data.video_id;

      setMessage(`Fetched ${data.count} comments. Redirecting...`);

      // Delay slightly to show message before navigating
      setTimeout(() => {
        navigate(`/analysis/${videoId}`);
      }, 1000);
    } catch (err) {
      console.error(err);
      setMessage(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Analyze YouTube Course Reviews</h2>
      <p className="helper-text">Paste a YouTube video link to analyze:</p>

      <form onSubmit={handleSubmit}>
        <div className="home-input-section">
          <input
            type="text"
            placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            className="home-input"
          />
          <button className="home-button" type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </form>

      {message && <p style={{ marginTop: "10px" }}>{message}</p>}
    </div>
  );
}
