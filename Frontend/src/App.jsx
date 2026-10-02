import React, { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [activeTab, setActiveTab] = useState("skills");
  const [analysis, setAnalysis] = useState(null);

  // ==========================================================
  // FILE HANDLERS
  // ==========================================================

  const handleResumeChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Please upload the Resume as a PDF.");
      return;
    }

    setResumeFile(file);
    setError("");
  };

  const handleJdChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Please upload the Job Description as a PDF.");
      return;
    }

    setJdFile(file);
    setError("");
  };

  const removeResume = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setResumeFile(null);
  };

  const removeJd = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setJdFile(null);
  };

  // ==========================================================
  // ANALYZE DOCUMENTS
  // ==========================================================

  const analyzeDocuments = async () => {
    if (!resumeFile) {
      setError("Please upload your Resume PDF.");
      return;
    }

    if (!jdFile) {
      setError("Please upload your Job Description PDF.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const formData = new FormData();

      formData.append("resume", resumeFile);
      formData.append("job_description", jdFile);

      formData.append(
        "question",
        "Analyze my resume with this job description and show matching skills, partial matching skills, missing skills, relevant projects, resume suggestions, interview questions, technical questions, and relevant resume sections."
      );

      const response = await fetch(
        `${API_URL}/api/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await response.json();

      console.log("RAG API RESPONSE:", result);

      if (!response.ok) {
        throw new Error(
          result.message || "Analysis failed."
        );
      }

      if (result.status !== "success") {
        throw new Error(
          result.message || "Analysis failed."
        );
      }

      /*
       * Your backend may return:
       *
       * {
       *   status: "success",
       *   data: {...}
       * }
       *
       * OR:
       *
       * {
       *   status: "success",
       *   analysis: {...}
       * }
       *
       * OR the analysis directly.
       */

      const data =
        result.data ||
        result.analysis ||
        result;

      console.log("Analysis data:", data);

      const normalizedData = {
        matching_skills:
          Array.isArray(data.matching_skills)
            ? data.matching_skills
            : [],

        partial_match_skills:
          Array.isArray(data.partial_match_skills)
            ? data.partial_match_skills
            : [],

        missing_skills:
          Array.isArray(data.missing_skills)
            ? data.missing_skills
            : [],

        relevant_projects:
          Array.isArray(data.relevant_projects)
            ? data.relevant_projects
            : [],

        resume_suggestions:
          Array.isArray(data.resume_suggestions)
            ? data.resume_suggestions
            : [],

        interview_questions:
          Array.isArray(data.interview_questions)
            ? data.interview_questions
            : [],

        technical_questions:
          Array.isArray(data.technical_questions)
            ? data.technical_questions
            : [],

        relevant_resume_sections:
          Array.isArray(data.relevant_resume_sections)
            ? data.relevant_resume_sections
            : Array.isArray(data.section_relevance)
            ? data.section_relevance
            : [],

        match_percentage:
          Number(
            data.match_percentage ??
            data.matchPercentage ??
            0
          ),

        retrieval:
          data.retrieval || {
            resume_chunks: 0,
            job_description_chunks: 0,
          },
      };

      console.log(
        "Normalized analysis:",
        normalizedData
      );

      setAnalysis(normalizedData);
      setActiveTab("skills");

    } catch (err) {
      console.error("Analysis error:", err);

      setError(
        err.message ||
        "Failed to connect to backend."
      );

      setAnalysis(null);

    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // HELPERS
  // ==========================================================

  const getItemText = (item) => {
    if (typeof item === "string") {
      return item;
    }

    if (!item || typeof item !== "object") {
      return "";
    }

    return (
      item.skill ||
      item.name ||
      item.title ||
      item.project ||
      item.question ||
      item.text ||
      item.suggestion ||
      item.section ||
      ""
    );
  };

  const getProjectTitle = (item) => {
    if (typeof item === "string") {
      return item;
    }

    return (
      item?.project ||
      item?.name ||
      item?.title ||
      item?.project_name ||
      "Relevant Project"
    );
  };

  const getProjectDescription = (item) => {
    if (typeof item === "string") {
      return "";
    }

    return (
      item?.relevance ||
      item?.description ||
      item?.reason ||
      item?.details ||
      ""
    );
  };

  const getSuggestionText = (item) => {
    if (typeof item === "string") {
      return item;
    }

    return (
      item?.suggestion ||
      item?.text ||
      item?.recommendation ||
      item?.title ||
      ""
    );
  };

  const getQuestionText = (item) => {
    if (typeof item === "string") {
      return item;
    }

    return (
      item?.question ||
      item?.text ||
      item?.query ||
      ""
    );
  };

  const matchPercentage = Math.min(
    100,
    Math.max(
      0,
      Math.round(
        Number(
          analysis?.match_percentage || 0
        )
      )
    )
  );

  const matchedSkills =
    analysis?.matching_skills || [];

  const partialSkills =
    analysis?.partial_match_skills || [];

  const missingSkills =
    analysis?.missing_skills || [];

  const projects =
    analysis?.relevant_projects || [];

  const suggestions =
    analysis?.resume_suggestions || [];

  const interviewQuestions =
    analysis?.interview_questions || [];

  const technicalQuestions =
    analysis?.technical_questions || [];

  const sections =
    analysis?.relevant_resume_sections || [];

  const totalSkills =
    matchedSkills.length +
    partialSkills.length +
    missingSkills.length;

  // ==========================================================
  // FIT MESSAGE
  // ==========================================================

  const getFitMessage = () => {
    if (matchPercentage >= 75) {
      return {
        title: "Strong Match",
        text:
          "Your resume shows strong alignment with the requirements found in the job description.",
      };
    }

    if (matchPercentage >= 50) {
      return {
        title: "Potential Fit",
        text:
          "Your resume has several relevant skills, with some additional requirements to address.",
      };
    }

    return {
      title: "Needs Improvement",
      text:
        "The analysis found several requirements that are not explicitly supported by the retrieved resume content.",
    };
  };

  const fit = getFitMessage();

  // ==========================================================
  // SKILL CHIP
  // ==========================================================

  const SkillChip = ({
    item,
    type,
  }) => {
    const text = getItemText(item);

    if (!text) return null;

    return (
      <span
        className={`skill-chip ${type}`}
      >
        {text}
      </span>
    );
  };

  // ==========================================================
  // EMPTY STATE
  // ==========================================================

  const EmptyState = ({ message }) => (
    <div className="empty-result">
      {message}
    </div>
  );

  // ==========================================================
  // SKILL MATCH CONTENT
  // ==========================================================

  const renderSkillMatch = () => {
    return (
      <div className="skill-analysis">

        {/* SUMMARY CARD */}

        <div className="match-summary-card">

          <div className="summary-left">

            <div
              className="donut"
              style={{
                "--percentage": `${matchPercentage * 3.6}deg`,
              }}
            >
              <div className="donut-inner">
                <strong>
                  {matchPercentage}%
                </strong>

                <span>
                  Overall Match
                </span>
              </div>
            </div>

          </div>

          <div className="summary-middle">

            <div className="summary-row">
              <span className="summary-dot matched-dot"></span>

              <span>
                Matched Skills
              </span>

              <strong>
                {matchedSkills.length}
                {totalSkills > 0
                  ? ` / ${totalSkills}`
                  : ""}
              </strong>
            </div>

            <div className="summary-row">
              <span className="summary-dot partial-dot"></span>

              <span>
                Partial Match
              </span>

              <strong>
                {partialSkills.length}
                {totalSkills > 0
                  ? ` / ${totalSkills}`
                  : ""}
              </strong>
            </div>

            <div className="summary-row">
              <span className="summary-dot missing-dot"></span>

              <span>
                Missing Skills
              </span>

              <strong>
                {missingSkills.length}
                {totalSkills > 0
                  ? ` / ${totalSkills}`
                  : ""}
              </strong>
            </div>

          </div>

          <div className="fit-card">

            <div className="fit-icon">
              ✓
            </div>

            <div>
              <h3>
                {fit.title}
              </h3>

              <p>
                {fit.text}
              </p>
            </div>

          </div>

        </div>

        {/* MATCHED SKILLS */}

        <div className="skill-section">

          <div className="section-title-row">

            <span className="section-icon matched-icon">
              ✓
            </span>

            <div>
              <h3>
                Matched Skills ({matchedSkills.length})
              </h3>

              <p>
                Skills found in both your resume and the job description.
              </p>
            </div>

          </div>

          {matchedSkills.length > 0 ? (
            <div className="skill-chip-container">
              {matchedSkills.map(
                (skill, index) => (
                  <SkillChip
                    key={index}
                    item={skill}
                    type="matched"
                  />
                )
              )}
            </div>
          ) : (
            <EmptyState
              message="No matching skills returned by the analysis."
            />
          )}

        </div>

        {/* PARTIAL MATCH */}

        <div className="skill-section">

          <div className="section-title-row">

            <span className="section-icon partial-icon">
              ◐
            </span>

            <div>
              <h3>
                Partial Match Skills ({partialSkills.length})
              </h3>

              <p>
                Skills that are related to or partially supported by the resume.
              </p>
            </div>

          </div>

          {partialSkills.length > 0 ? (
            <div className="skill-chip-container">
              {partialSkills.map(
                (skill, index) => (
                  <SkillChip
                    key={index}
                    item={skill}
                    type="partial"
                  />
                )
              )}
            </div>
          ) : (
            <EmptyState
              message="No partial matches returned."
            />
          )}

        </div>

        {/* MISSING SKILLS */}

        <div className="skill-section">

          <div className="section-title-row">

            <span className="section-icon missing-icon">
              !
            </span>

            <div>
              <h3>
                Missing Skills ({missingSkills.length})
              </h3>

              <p>
                Job-description requirements not explicitly supported by the resume context.
              </p>
            </div>

          </div>

          {missingSkills.length > 0 ? (
            <div className="skill-chip-container">
              {missingSkills.map(
                (skill, index) => (
                  <SkillChip
                    key={index}
                    item={skill}
                    type="missing"
                  />
                )
              )}
            </div>
          ) : (
            <EmptyState
              message="No missing skills returned."
            />
          )}

        </div>

      </div>
    );
  };

  // ==========================================================
  // PROJECTS
  // ==========================================================

  const renderProjects = () => {
    if (!projects.length) {
      return (
        <EmptyState
          message="No relevant projects returned by the analysis."
        />
      );
    }

    return (
      <div className="content-list">

        {projects.map(
          (project, index) => (
            <div
              className="project-card"
              key={index}
            >
              <div className="project-number">
                {index + 1}
              </div>

              <div>
                <h3>
                  {getProjectTitle(project)}
                </h3>

                {getProjectDescription(
                  project
                ) && (
                  <p>
                    {getProjectDescription(
                      project
                    )}
                  </p>
                )}
              </div>
            </div>
          )
        )}

      </div>
    );
  };

  // ==========================================================
  // SUGGESTIONS
  // ==========================================================

  const renderSuggestions = () => {
    if (!suggestions.length) {
      return (
        <EmptyState
          message="No resume improvement suggestions returned."
        />
      );
    }

    return (
      <div className="content-list">

        {suggestions.map(
          (suggestion, index) => (
            <div
              className="suggestion-card"
              key={index}
            >
              <div className="suggestion-number">
                {index + 1}
              </div>

              <div>
                <h3>
                  Resume Improvement
                </h3>

                <p>
                  {getSuggestionText(
                    suggestion
                  )}
                </p>

                {typeof suggestion ===
                  "object" &&
                  suggestion.reason && (
                    <div className="reason">
                      <strong>
                        Reason:
                      </strong>{" "}
                      {suggestion.reason}
                    </div>
                  )}
              </div>

            </div>
          )
        )}

      </div>
    );
  };

  // ==========================================================
  // QUESTIONS
  // ==========================================================

  const renderQuestions = (
    questions,
    emptyMessage
  ) => {
    if (!questions.length) {
      return (
        <EmptyState
          message={emptyMessage}
        />
      );
    }

    return (
      <div className="question-list">

        {questions.map(
          (question, index) => (
            <div
              className="question-card"
              key={index}
            >
              <div className="question-number">
                {index + 1}
              </div>

              <p>
                {getQuestionText(
                  question
                )}
              </p>

            </div>
          )
        )}

      </div>
    );
  };

  // ==========================================================
  // RESUME SECTIONS
  // ==========================================================

  const renderSections = () => {
    if (!sections.length) {
      return (
        <EmptyState
          message="No relevant resume sections returned."
        />
      );
    }

    return (
      <div className="section-list">

        {sections.map(
          (section, index) => {

            const title =
              typeof section ===
              "string"
                ? section
                : section.section ||
                  section.name ||
                  section.title ||
                  "Resume Section";

            const relevance =
              typeof section ===
              "object"
                ? section.relevance ||
                  section.reason ||
                  ""
                : "";

            return (
              <div
                className="resume-section-card"
                key={index}
              >
                <div className="resume-section-icon">
                  📄
                </div>

                <div>
                  <h3>
                    {title}
                  </h3>

                  {relevance && (
                    <p>
                      {relevance}
                    </p>
                  )}
                </div>
              </div>
            );
          }
        )}

      </div>
    );
  };

  // ==========================================================
  // ACTIVE TAB
  // ==========================================================

  const renderActiveTab = () => {
    switch (activeTab) {

      case "missing":
        return (
          <div className="tab-page">
            <div className="page-heading">
              <span className="page-icon missing-bg">
                !
              </span>

              <div>
                <h2>
                  Missing Skills
                </h2>

                <p>
                  Skills required by the job description that are not explicitly supported by the resume.
                </p>
              </div>
            </div>

            <div className="large-skill-container">
              {missingSkills.length > 0 ? (
                missingSkills.map(
                  (skill, index) => (
                    <SkillChip
                      key={index}
                      item={skill}
                      type="missing"
                    />
                  )
                )
              ) : (
                <EmptyState
                  message="No missing skills returned."
                />
              )}
            </div>
          </div>
        );

      case "projects":
        return (
          <div className="tab-page">
            <div className="page-heading">
              <span className="page-icon project-bg">
                💼
              </span>

              <div>
                <h2>
                  Relevant Projects
                </h2>

                <p>
                  Projects from your resume that relate to the job description.
                </p>
              </div>
            </div>

            {renderProjects()}
          </div>
        );

      case "suggestions":
        return (
          <div className="tab-page">
            <div className="page-heading">
              <span className="page-icon suggestion-bg">
                ✎
              </span>

              <div>
                <h2>
                  Resume Suggestions
                </h2>

                <p>
                  Suggestions based on the retrieved resume and job-description context.
                </p>
              </div>
            </div>

            {renderSuggestions()}
          </div>
        );

      case "interview":
        return (
          <div className="tab-page">
            <div className="page-heading">
              <span className="page-icon interview-bg">
                ?
              </span>

              <div>
                <h2>
                  Interview Questions
                </h2>

                <p>
                  Questions generated from the job requirements and resume context.
                </p>
              </div>
            </div>

            {renderQuestions(
              interviewQuestions,
              "No interview questions returned."
            )}

            {technicalQuestions.length > 0 && (
              <>
                <div className="sub-heading">
                  Technical Questions
                </div>

                {renderQuestions(
                  technicalQuestions,
                  "No technical questions returned."
                )}
              </>
            )}
          </div>
        );

      default:
        return renderSkillMatch();
    }
  };

  // ==========================================================
  // UI
  // ==========================================================

  return (
    <div className="app">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            📄
          </div>

          <div>
            <h1>
              Resume + Job Description RAG Analyzer
            </h1>

            <p>
              Upload your Resume and Job Description to get AI-powered insights
            </p>
          </div>

        </div>

        <div className="profile">

          <div className="profile-circle">
            S
          </div>

          <span>
            Sukadha
          </span>

          <span className="profile-arrow">
            ▾
          </span>

        </div>

      </header>

      {/* ======================================================
          MAIN
      ====================================================== */}

      <main className="main-container">

        {/* ====================================================
            LEFT PANEL
        ==================================================== */}

        <section className="upload-panel">

          <div className="upload-heading">

            <div className="upload-main-icon">
              ↥
            </div>

            <div>
              <h2>
                Upload Documents
              </h2>

              <p>
                Upload your Resume and Job Description PDFs.
              </p>
            </div>

          </div>

          <div className="divider"></div>

          <div className="upload-grid">

            {/* RESUME */}

            <label className="upload-box">

              <div className="upload-document-icon">
                📄
              </div>

              <strong>
                Upload Resume
              </strong>

              <span>
                (PDF)
              </span>

              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={
                  handleResumeChange
                }
              />

              {resumeFile && (
                <div className="file-info">

                  <div className="pdf-icon">
                    PDF
                  </div>

                  <div className="file-details">

                    <strong>
                      {resumeFile.name}
                    </strong>

                    <span>
                      {Math.ceil(
                        resumeFile.size / 1024
                      )}{" "}
                      KB
                    </span>

                  </div>

                  <button
                    type="button"
                    onClick={removeResume}
                  >
                    ×
                  </button>

                </div>
              )}

            </label>

            {/* JOB DESCRIPTION */}

            <label className="upload-box">

              <div className="upload-document-icon">
                📄
              </div>

              <strong>
                Upload Job Description
              </strong>

              <span>
                (PDF)
              </span>

              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={
                  handleJdChange
                }
              />

              {jdFile && (
                <div className="file-info">

                  <div className="pdf-icon">
                    PDF
                  </div>

                  <div className="file-details">

                    <strong>
                      {jdFile.name}
                    </strong>

                    <span>
                      {Math.ceil(
                        jdFile.size / 1024
                      )}{" "}
                      KB
                    </span>

                  </div>

                  <button
                    type="button"
                    onClick={removeJd}
                  >
                    ×
                  </button>

                </div>
              )}

            </label>

          </div>

          {/* ANALYZE BUTTON */}

          <button
            className="analyze-button"
            onClick={analyzeDocuments}
            disabled={
              loading ||
              !resumeFile ||
              !jdFile
            }
          >

            {loading ? (
              <>
                <span className="button-spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                🔎 Analyze Documents
              </>
            )}

          </button>

          {/* ERROR */}

          {error && (
            <div className="error-box">
              ⚠️ {error}
            </div>
          )}

          {/* ==================================================
              HOW IT WORKS
          ================================================== */}

          <div className="how-it-works">

            <h2>
              ⚙ How it works
            </h2>

            <div className="steps">

              <div className="step">
                <div className="step-number">
                  1
                </div>

                <div>
                  <strong>
                    Document Parsing
                  </strong>

                  <span>
                    Extract text from resume and JD
                  </span>
                </div>
              </div>

              <div className="step">
                <div className="step-number">
                  2
                </div>

                <div>
                  <strong>
                    Chunking
                  </strong>

                  <span>
                    Split into meaningful chunks
                  </span>
                </div>
              </div>

              <div className="step">
                <div className="step-number">
                  3
                </div>

                <div>
                  <strong>
                    Embeddings
                  </strong>

                  <span>
                    Convert text to vector embeddings
                  </span>
                </div>
              </div>

              <div className="step">
                <div className="step-number">
                  4
                </div>

                <div>
                  <strong>
                    Vector Database
                  </strong>

                  <span>
                    Store embeddings in FAISS / ChromaDB
                  </span>
                </div>
              </div>

              <div className="step">
                <div className="step-number">
                  5
                </div>

                <div>
                  <strong>
                    RAG Retrieval
                  </strong>

                  <span>
                    Retrieve relevant context
                  </span>
                </div>
              </div>

              <div className="step">
                <div className="step-number">
                  6
                </div>

                <div>
                  <strong>
                    LLM
                  </strong>

                  <span>
                    Generate personalized analysis
                  </span>
                </div>
              </div>

            </div>

          </div>

        </section>

        {/* ====================================================
            RIGHT PANEL
        ==================================================== */}

        <section className="results-panel">

          {/* TABS */}

          <div className="tabs">

            <button
              className={
                activeTab === "skills"
                  ? "tab active"
                  : "tab"
              }
              onClick={() =>
                setActiveTab("skills")
              }
            >
              <span>📊</span>
              Skill Match
            </button>

            <button
              className={
                activeTab === "missing"
                  ? "tab active"
                  : "tab"
              }
              onClick={() =>
                setActiveTab("missing")
              }
            >
              <span>💡</span>
              Missing Skills
            </button>

            <button
              className={
                activeTab === "projects"
                  ? "tab active"
                  : "tab"
              }
              onClick={() =>
                setActiveTab("projects")
              }
            >
              <span>💼</span>
              Relevant Projects
            </button>

            <button
              className={
                activeTab === "suggestions"
                  ? "tab active"
                  : "tab"
              }
              onClick={() =>
                setActiveTab("suggestions")
              }
            >
              <span>📄</span>
              Resume Suggestions
            </button>

            <button
              className={
                activeTab === "interview"
                  ? "tab active"
                  : "tab"
              }
              onClick={() =>
                setActiveTab("interview")
              }
            >
              <span>❓</span>
              Interview Questions
            </button>

          </div>

          {/* CHAT QUESTION */}

          <div className="user-question">
            <span>
              Analyze my resume with this job description and show the skill match.
            </span>

            <div className="user-avatar">
              S
            </div>
          </div>

          {/* RESULTS */}

          {!analysis && !loading && (
            <div className="empty-analysis">

              <div className="empty-analysis-icon">
                📄
              </div>

              <h2>
                Upload your documents to begin
              </h2>

              <p>
                Upload your Resume PDF and Job Description PDF,
                then click <strong>Analyze Documents</strong>.
              </p>

            </div>
          )}

          {loading && (
            <div className="loading-state">

              <div className="loading-icon">
                🤖
              </div>

              <h2>
                Analyzing your documents...
              </h2>

              <p>
                Retrieving resume and job-description
                chunks and generating the RAG analysis.
              </p>

              <div className="loading-bar">
                <div></div>
              </div>

            </div>
          )}

          {analysis && !loading && (
            <div className="analysis-container">

              <div className="analysis-header">

                <div className="bot-avatar">
                  🤖
                </div>

                <div>
                  <h2>
                    {activeTab === "skills"
                      ? "Skill Matching Analysis"
                      : activeTab === "missing"
                      ? "Missing Skills"
                      : activeTab === "projects"
                      ? "Relevant Projects"
                      : activeTab === "suggestions"
                      ? "Resume Suggestions"
                      : "Interview Questions"}
                  </h2>

                  <p>
                    Comparison between your resume and the job description.
                  </p>
                </div>

              </div>

              {renderActiveTab()}

            </div>
          )}

          {/* FOLLOW UP */}

          {analysis && !loading && (
            <div className="follow-up">

              <span className="paperclip">
                📎
              </span>

              <input
                type="text"
                placeholder="Ask follow-up questions (e.g., show missing skills, relevant projects, interview questions...)"
                onKeyDown={(e) => {
                  if (
                    e.key === "Enter" &&
                    e.target.value.trim()
                  ) {
                    setActiveTab("skills");
                  }
                }}
              />

              <button>
                ➤
              </button>

            </div>
          )}

        </section>

      </main>

    </div>
  );
}

export default App;