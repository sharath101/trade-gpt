import React, { useState, useEffect, useRef } from 'react';
import { Editor } from '@monaco-editor/react';
import '../css/codeeditor.css';

export const CodeEditor = () => {
  const [files, setFiles] = useState([{ id: 1, filename: 'main.py', code: '' }]);
  const [activeFileId, setActiveFileId] = useState(1);
  const [output, setOutput] = useState({ error: null, warning: null, results: null });
  const [outputHeight, setOutputHeight] = useState(200);
  const outputPaneRef = useRef(null);
  const isResizingRef = useRef(false);
  const lastYRef = useRef(0);

  const addFile = () => {
    const newId = Math.max(...files.map(file => file.id), 0) + 1;
    setFiles([...files, { id: newId, filename: '', code: '' }]);
    setActiveFileId(newId);
  };

  const deleteFile = id => {
    const updatedFiles = files.filter(file => file.id !== id);
    setFiles(updatedFiles);
    if (updatedFiles.length > 0) {
      setActiveFileId(updatedFiles[0].id);
    } else {
      setActiveFileId(null);
    }
  };

  const handleChange = (id, value) => {
    setFiles(files.map(file => (file.id === id ? { ...file, code: value } : file)));
  };

  const handleFilenameChange = (id, value) => {
    setFiles(files.map(file => (file.id === id ? { ...file, filename: value } : file)));
  };

  const analyzeCode = async () => {
    try {
      let fileData = {};
      for (let f in files) {
        console.log(files);
        fileData[files[f].filename] = files[f].code;
      }
      console.log(fileData);
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"files": fileData}),
      });
      const result = await response.json();
      if (result.output) {
        setOutput((previous) => ({error: null, warning: null, results: result.output}))
      }
      if (result.error) {
        setOutput((previous) => ({error: null, warning: null, results: result.error}))
      }
      if (result.errors) {
        setOutput((previous) => ({error: null, warning: result.errors, results: null}))
      }
      if (result.suspicious) {
        setOutput((previous) => ({error: null, warning: result.suspicious, results: null}))
      }
    } catch (error) {
      console.error('Error analyzing code:', error);
    }
  };

  const runCode = async () => {
    try {
      let fileData = {};
      for (let f in files) {
        console.log(files);
        fileData[files[f].filename] = files[f].code;
      }
      const response = await fetch('http://localhost:5000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"files": fileData}),
      });
      const result = await response.json();
      if (result.output) {
        setOutput((previous) => ({error: null, warning: null, results: result.output}))
      }
      if (result.error) {
        setOutput((previous) => ({error: null, warning: null, results: result.error}))
      }
      if (result.errors) {
        setOutput((previous) => ({error: null, warning: result.errors, results: null}))
      }
      if (result.suspicious) {
        setOutput((previous) => ({error: null, warning: result.suspicious, results: null}))
      }
    } catch (error) {
      console.error('Error running code:', error);
    }
  };

  const activeFile = files.find(file => file.id === activeFileId);

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="file-tree">
          {files.map(file => (
            <div
              className={activeFileId === file.id ? 'file active' : 'file'}
              key={file.id}
              onClick={() => setActiveFileId(file.id)}
            >
              {file.filename || 'Untitled'}
              <span
                className="close-btn"
                onClick={e => {
                  e.stopPropagation();
                  deleteFile(file.id);
                }}
              >
                &times;
              </span>
            </div>
          ))}
          <div className="add-file" onClick={addFile}>
            + Add File
          </div>
        </div>
      </div>
      <div className="editor-container">
        <div className="editor-toolbar">
          <button className="btn" onClick={analyzeCode}>
            Analyze
          </button>
          <button className="btn" onClick={runCode}>
            Run
          </button>
        </div>
        <div className="editor">
          {activeFile ? (
            <div>
              <div className="editor-content-active">
                Filename:
                <span>
                  <input
                    type="text"
                    className="filename"
                    placeholder="Filename (e.g., module.py)"
                    value={activeFile.filename}
                    onChange={e => handleFilenameChange(activeFile.id, e.target.value)}
                  />
                </span>
              </div>

              <Editor
                height="70vh"
                language="python"
                theme="vs-dark"
                value={activeFile.code}
                onChange={value => handleChange(activeFile.id, value)}
              />
            </div>
          ) : (
            <div>Please add or select a file</div>
          )}
        </div>
        <div className="output-pane" ref={outputPaneRef}>
          <div className="output">
          {output.error && Array.isArray(output.error) && output.error.length > 0 && (
            <div>
              <h3>Errors:</h3>
              <ul>
                {output.error.map(item => (
                  <li key={item.id}>{item.name}</li>
                ))}
              </ul>
            </div>
          )}
            {output.warning && Array.isArray(output.warning) && output.warning.length > 0 && (
              <div>
                <h3>Warning:</h3>
                <ul>
                  {output.warning.map(item => (
                    <li key={item.id}>{item.name}</li>
                  ))}
                </ul>
              </div>
            )}
            {output.results ? (
              <div>
                <h3>Output:</h3>
                <ul>
                  {output.results.map(item => (
                    <li key={item.id}>{item.name}</li>
                  ))}
                </ul>
              </div>
            ) : <div></div>}
          </div>
        </div>

      </div>
    </div>
  );
};