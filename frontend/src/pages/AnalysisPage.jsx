import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import CategoryPieChart from "../components/CategoryPieChart";

export default function AnalysisPage() {
  const { courseId } = useParams(); // videoId from URL
  const [videoData, setVideoData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [openAspects, setOpenAspects] = useState(false);

  const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY;

  function handleShowAspects() {
    openAspects ? setOpenAspects(false) : setOpenAspects(true);
  }

  async function handleGetReview(courseId) {
    setAnalysisLoading(true);
    setError("");
    try {
      const res = await fetch(
        `http://127.0.0.1:5000/course/${courseId}/analysis`
      );
      const data = await res.json();
      console.log(data);

      if (!res.ok) throw new Error(data.error || "Failed to analyze comments.");
      setAnalysis(data);
    } catch (err) {
      console.error(err);
      setError("Error analyzing video. Please try again.");
    } finally {
      setAnalysisLoading(false);
    }
  }

  useEffect(() => {
    if (!courseId || courseId === "nothing" || courseId.trim() === "") {
      setError(
        "No video to show. Please go back and enter a valid YouTube URL."
      );
      return;
    }

    async function fetchVideoInfo() {
      setLoading(true);
      try {
        const response = await fetch(
          `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=${courseId}&key=${API_KEY}`
        );
        const data = await response.json();

        if (!data.items || data.items.length === 0) {
          setError("No video found for this ID.");
          return;
        }

        const vid = data.items[0];
        setVideoData({
          title: vid.snippet.title,
          channel: vid.snippet.channelTitle,
          thumbnail: vid.snippet.thumbnails.high.url,
          likes: vid.statistics.likeCount || "N/A",
          views: vid.statistics.viewCount || "N/A",
        });
      } catch (err) {
        console.error(err);
        setError("Failed to fetch video info.");
      } finally {
        setLoading(false);
      }
    }

    fetchVideoInfo();
  }, [courseId]);

  if (!courseId || courseId === "nothing" || error) {
    return (
      <div className="card">
        <h2>No video to show</h2>
        <p>{error || "Please go back and enter a valid YouTube link."}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="card">
        <p>Loading video details...</p>
      </div>
    );
  }

  // ✅ Corrected main return
  return (
    <div className="analysis">
      {videoData && (
        <>
          <div className="analysis-container">
            <div className="analysis-video-details card">
              <h1 className="video-title">{videoData.title}</h1>

              <div className="video-details">
                <p className="channel-name">{videoData.channel}</p>

                <div className="views-likes">
                  {/* --- Views Icon --- */}
                  <div className="views">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 512 512"
                      className="icons"
                      width="20"
                      height="20"
                    >
                      <path
                        d="M255.66 112c-77.94 0-157.89 45.11-220.83 135.33a16 16 0 00-.27 17.77C82.92 340.8 161.8 400 255.66 400c92.84 0 173.34-59.38 221.79-135.25a16.14 16.14 0 000-17.47C428.89 172.28 347.8 112 255.66 112z"
                        fill="none"
                        stroke="#1d4ed8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="50"
                      />
                      <circle
                        cx="256"
                        cy="256"
                        r="80"
                        fill="none"
                        stroke="#1d4ed8"
                        strokeMiterlimit="10"
                        strokeWidth="50"
                      />
                    </svg>
                    <p>{videoData.views}</p>
                  </div>

                  {/* --- Likes Icon --- */}
                  <div className="likes">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="#1d4ed8"
                      className="icons"
                      width="20"
                      height="20"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2.5"
                        d="M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75
                        2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126
                        c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285
                        a11.95 11.95 0 0 1-2.649 7.521
                        c-.388.482-.987.729-1.605.729H13.48
                        c-.483 0-.964-.078-1.423-.23l-3.114-1.04
                        a4.501 4.501 0 0 0-1.423-.23H5.904
                        m10.598-9.75H14.25
                        M5.904 18.5
                        c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908
                        c-.889 0-1.713-.518-1.972-1.368
                        a12 12 0 0 1-.521-3.507
                        c0-1.553.295-3.036.831-4.398
                        C3.387 9.953 4.167 9.5 5 9.5h1.053
                        c.472 0 .745.556.5.96
                        a8.958 8.958 0 0 0-1.302 4.665
                        c0 1.194.232 2.333.654 3.375Z"
                      />
                    </svg>
                    <p>{videoData.likes}</p>
                  </div>
                </div>
              </div>

              <img
                src={videoData.thumbnail}
                alt="thumbnail"
                className="thumbnail"
              />
            </div>

            {/* --- Show Analysis Results --- */}
            <div className="analysis-results card">
              <div className="details-header">
                <h1 style={{ color: "black" }}>Detailed Analysis</h1>
                <button
                  className="analysis-button"
                  onClick={() => handleGetReview(courseId)}
                  disabled={analysisLoading}
                >
                  {analysisLoading ? "Analyzing video..." : "Get Review"}
                </button>
              </div>

              {analysisLoading ? (
                <p>Fetching detailed review...</p>
              ) : analysis ? (
                <>
                  <h3>
                    Overall Sentiment:{" "}
                    <span
                      style={{
                        textTransform: "uppercase",
                        color:
                          analysis.aggregate.overall_sentiment === "positive"
                            ? "green"
                            : analysis.aggregate.overall_sentiment === "neutral"
                            ? "yellow"
                            : "red",
                      }}
                    >
                      {analysis.aggregate.overall_sentiment}
                    </span>
                  </h3>
                  <h3>
                    Analysed score:{" "}
                    <span
                      style={{
                        color:
                          analysis.aggregate.adjusted_score >= 8
                            ? "green"
                            : analysis.aggregate.adjusted_score >= 5 &&
                              analysis.aggregate.adjusted_score < 8
                            ? "#d2cc1b"
                            : "red",
                      }}
                    >
                      {analysis.aggregate.adjusted_score} / 10
                    </span>
                    {"   "}
                    <span className="comment_text">
                      (based on {analysis.raw_count} comments)
                    </span>
                  </h3>
                  <h3>
                    Absolute score:{" "}
                    <span
                      style={{
                        color:
                          analysis.aggregate.scaled_score >= 8
                            ? "green"
                            : analysis.aggregate.scaled_score >= 5 &&
                              analysis.aggregate.scaled_score < 8
                            ? "#d2cc1b"
                            : "red",
                      }}
                    >
                      {analysis.aggregate.scaled_score} / 10
                    </span>
                    {"   "}
                    <span className="comment_text">(undamped)</span>
                  </h3>
                  <div className="review">
                    <h3 className="review-title">
                      Review:{" "}
                      <span className="review-desc">
                        {analysis.review.summary}
                      </span>
                    </h3>
                  </div>
                  <CategoryPieChart categories={analysis.review.categories} />
                  <h4>
                    Aspects:{" "}
                    <span className="show-aspects" onClick={handleShowAspects}>
                      {openAspects
                        ? `Hide individual aspects`
                        : `Show individual aspects`}
                    </span>
                  </h4>
                  {openAspects && (
                    <ul>
                      {analysis.aspect_list?.map((a, idx) => (
                        <li key={idx}>
                          <strong>{a.aspect}</strong>: {a.sentiment} (
                          {a.confidence?.toFixed(3)})
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              ) : (
                <p>No reviews to show</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
