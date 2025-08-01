import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://127.0.0.1:8000/upload-resume", formData, {
        responseType: "blob",
        headers: { "Content-Type": "multipart/form-data" },
      });

      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "ATS_Resume.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
      console.log(link,blob,url); 
      setMessage("Resume processed successfully!");
    } catch (err) {
        console.error("Upload error:", err);
      setMessage("Upload failed. Make sure your backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-sky-50 text-gray-800 flex flex-col items-center px-4 py-10">
      <h1 className="text-4xl font-bold text-purple-600 mb-2 text-center">
        Transform Your Resume with AI
      </h1>
      <p className="text-center mb-6 text-gray-600 max-w-2xl">
        Upload your resume and get an AI-enhanced version plus a personalized avatar video presentation.
        Stand out from the crowd with cutting-edge technology.
      </p>

      <div className="flex flex-col lg:flex-row gap-8 w-full max-w-5xl">
        {/* Upload Section */}
        <div className="flex-1 bg-white border border-dashed border-gray-300 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-2">📤 Upload Your Resume</h2>
          <p className="text-sm text-gray-500 mb-4">
            Upload your PDF resume to get started. We’ll enhance it and create your avatar video.
          </p>

          <label
            htmlFor="fileUpload"
            className="w-full h-32 flex items-center justify-center border-2 border-dashed rounded cursor-pointer bg-gray-50 hover:bg-gray-100 transition"
          >
            <div className="text-center">
              <span className="block text-gray-600">📎 Drop your resume here or click to browse</span>
              <span className="text-xs text-gray-400">Supports PDF files up to 10MB</span>
            </div>
            <input
              id="fileUpload"
              type="file"
              className="hidden"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </label>

          {/* Uploaded Resume Preview */}
          {file && (
            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">📄 Preview Uploaded Resume</h3>
              <iframe
                src={URL.createObjectURL(file)}
                className="w-full h-64 border rounded"
                title="Uploaded Resume Preview"
              ></iframe>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={loading || !file}
            className={`mt-4 w-full px-4 py-2 rounded font-medium text-white ${
              loading || !file ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {loading ? "Processing..." : "Upload & Download ATS Resume"}
          </button>

          {message && <p className="text-center mt-4 text-sm text-gray-700">{message}</p>}
        </div>

        {/* Avatar Preview Placeholder */}
        <div className="flex-1 bg-white rounded-lg p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-2">🎥 Live Avatar Video Preview</h2>
          <p className="text-sm text-gray-500 mb-4">
            Your personalized avatar will present your resume highlights in an engaging video format.
          </p>
          <div className="h-40 bg-gray-200 flex items-center justify-center rounded">
            <span className="text-gray-500 text-xl">📷 Avatar Video Preview</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
