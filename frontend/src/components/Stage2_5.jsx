import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Stage2_5.css';

export default function Stage2_5({ corrections }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!corrections || corrections.length === 0) {
    return null;
  }

  return (
    <div className="stage stage2-5">
      <h3 className="stage-title">Stage 2.5: Self-Corrections</h3>
      <p className="stage-description">
        Each model revised its answer based on peer feedback. Below you can see both the original response and the corrected version.
      </p>

      {/* Tab bar */}
      <div className="tabs">
        {corrections.map((corr, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            {corr.model.split('/')[1] || corr.model}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="tab-content">
        <div className="correction-model">
          {corrections[activeTab].model}
        </div>

        {/* Original Response Section */}
        <div className="response-section original">
          <h4>Original Response</h4>
          <div className="response-content markdown-content">
            <ReactMarkdown>{corrections[activeTab].original_response}</ReactMarkdown>
          </div>
        </div>

        {/* Corrected Response Section */}
        <div className="response-section corrected">
          <h4>Corrected Response</h4>
          <div className="response-content markdown-content">
            <ReactMarkdown>{corrections[activeTab].corrected_response}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
