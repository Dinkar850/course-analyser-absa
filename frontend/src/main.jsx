// src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// routes
import RootLayout from "./pages/RootLayout";
import HomePage from "./pages/HomePage";
import AnalysisPage from "./pages/AnalysisPage";

// global styles
import "./App.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RootLayout />}>
          <Route index element={<HomePage />} />
          <Route path="analysis/:courseId?" element={<AnalysisPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
