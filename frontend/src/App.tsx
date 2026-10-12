import axios from "axios";
import { useState } from "react";
import UploadForm from "./components/UploadForm";
import SummaryPanel from "./components/SummaryPanel";
import TestResultsTable from "./components/TestResultsTable";
import type { Report } from "./types";

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL ?? "http://127.0.0.1:8000";

function App() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload_spec`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Upload success", response.data);
      setReport(response.data as Report);
      setUploadedFileName(file.name);
    } catch (err) {
      console.error("Upload failed", err);
      setReport(null);
      if (axios.isAxiosError(err)) {
        const detail = (err.response?.data as { detail?: string })?.detail;
        setError(detail ?? "Upload failed");
      } else {
        setError("Unexpected error");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ marginBottom: "2rem" }}>
        <h1>SpecFuzzer</h1>
        <p style={{ color: "#475569", marginBottom: "1.5rem" }}>
          Upload an OpenAPI spec and generate adversarial tests. Tests come from
          the configured OpenAI-compatible LLM endpoint, with built-in heuristic
          tests used when the LLM call fails.
        </p>
        <UploadForm
          disabled={loading}
          uploadedFileName={uploadedFileName}
          onFileSelected={handleFileSelect}
        />
        {error ? (
          <p style={{ color: "#dc2626", marginTop: "1rem" }}>{error}</p>
        ) : null}
      </div>

      {report ? (
        <div className="card" style={{ marginBottom: "2rem" }}>
          <SummaryPanel summary={report.summary} loading={loading} />
        </div>
      ) : null}

      {report ? (
        <div className="card">
          <TestResultsTable findings={report.findings} loading={loading} />
        </div>
      ) : null}
    </div>
  );
}

export default App;
