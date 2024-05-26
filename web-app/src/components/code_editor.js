import { useState } from 'react';
import { Editor } from '@monaco-editor/react';
import { Box, Button, Container, Grid, IconButton, Paper, TextField, Typography } from '@mui/material';
import { Add, Close } from '@mui/icons-material';
import '../css/codeeditor.css';

export const CodeEditor = ({ setPage }) => {
    const [files, setFiles] = useState([
        { id: 1, filename: 'main.py', code: '' },
    ]);
    const [strategyName, setStrategyName] = useState('');
    const [indicators, setIndicators] = useState('');
    const [activeFileId, setActiveFileId] = useState(1);
    const [output, setOutput] = useState({
        error: null,
        warning: null,
        results: null,
    });

    const addFile = () => {
        const newId = Math.max(...files.map((file) => file.id), 0) + 1;
        setFiles([...files, { id: newId, filename: '', code: '' }]);
        setActiveFileId(newId);
    };

    const deleteFile = (id) => {
        const updatedFiles = files.filter((file) => file.id !== id);
        setFiles(updatedFiles);
        if (updatedFiles.length > 0) {
            setActiveFileId(updatedFiles[0].id);
        } else {
            setActiveFileId(null);
        }
    };

    const handleChange = (id, value) => {
        setFiles(
            files.map((file) =>
                file.id === id ? { ...file, code: value } : file
            )
        );
    };

    const handleFilenameChange = (id, value) => {
        setFiles(
            files.map((file) =>
                file.id === id ? { ...file, filename: value } : file
            )
        );
    };

    const analyzeCode = async () => {
        try {
            let fileData = {};
            for (let f in files) {
                fileData[files[f].filename] = files[f].code;
            }
            const response = await fetch('http://localhost:5000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: fileData }),
            });
            const result = await response.json();
            if (result.output) {
                setOutput({
                    error: null,
                    warning: null,
                    results: result.output,
                });
            }
            if (result.error) {
                setOutput({
                    error: result.error,
                    warning: null,
                    results: null,
                });
            }
            if (result.errors) {
                setOutput({
                    error: null,
                    warning: result.errors,
                    results: null,
                });
            }
            if (result.suspicious) {
                setOutput({
                    error: null,
                    warning: result.suspicious,
                    results: null,
                });
            }
        } catch (error) {
            console.error('Error analyzing code:', error);
        }
    };

    const runCode = async () => {
        try {
            let fileData = {};
            for (let f in files) {
                fileData[files[f].filename] = files[f].code;
            }
            const response = await fetch('http://localhost:5000/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: fileData }),
            });
            const result = await response.json();
            if (result.output) {
                setOutput({
                    error: null,
                    warning: null,
                    results: result.output,
                });
            }
            if (result.error) {
                setOutput({
                    error: result.error,
                    warning: null,
                    results: null,
                });
            }
            if (result.errors) {
                setOutput({
                    error: null,
                    warning: result.errors,
                    results: null,
                });
            }
            if (result.suspicious) {
                setOutput({
                    error: null,
                    warning: result.suspicious,
                    results: null,
                });
            }
        } catch (error) {
            console.error('Error running code:', error);
        }
    };

    const uploadStrategy = async () => {
        try {
            const data = {
                strategy_name: strategyName,
                indicators: indicators,
                description: 'Your Strategy Description',
            };

            const formData = new FormData();
            formData.append('strategy_name', data.strategy_name);
            formData.append('indicators', JSON.stringify(data.indicators));
            formData.append('description', data.description);

            // Append files
            files.forEach((file) => {
                const blob = new Blob([file.code], { type: 'text/plain' });
                formData.append('files', blob, file.filename);
            });

            const response = await fetch(
                'http://localhost:5000/upload_strategy',
                {
                    method: 'POST',
                    body: formData,
                }
            );

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();
            alert(
                'Strategy and files uploaded successfully: ' + result.message
            );
        } catch (error) {
            console.error('Error uploading strategy:', error);
            alert('Error uploading strategy');
        }
    };

    const activeFile = files.find((file) => file.id === activeFileId);

    return (
        <Container maxWidth="xl" style={{ marginTop: '20px' }}>
            <Grid container spacing={2}>
                <Grid item xs={3}>
                    <Paper elevation={3} style={{ padding: '10px' }}>
                        <Typography variant="h6">Files</Typography>
                        {files.map((file) => (
                            <Box
                                key={file.id}
                                display="flex"
                                justifyContent="space-between"
                                alignItems="center"
                                bgcolor={activeFileId === file.id ? 'lightgray' : 'white'}
                                p={1}
                                mb={1}
                                onClick={() => setActiveFileId(file.id)}
                                sx={{ cursor: 'pointer' }}
                            >
                                <Typography variant="body2">
                                    {file.filename || 'Untitled'}
                                </Typography>
                                <IconButton
                                    size="small"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        deleteFile(file.id);
                                    }}
                                >
                                    <Close fontSize="small" />
                                </IconButton>
                            </Box>
                        ))}
                        <Button
                            variant="contained"
                            color="primary"
                            startIcon={<Add />}
                            onClick={addFile}
                            fullWidth
                        >
                            Add File
                        </Button>
                    </Paper>
                </Grid>
                <Grid item xs={9}>
                    <Paper elevation={3} style={{ padding: '10px' }}>
                        <Box mb={2}>
                            <TextField
                                label="Strategy Name"
                                variant="outlined"
                                fullWidth
                                value={strategyName}
                                onChange={(e) => setStrategyName(e.target.value)}
                                margin="normal"
                            />
                            <TextField
                                label="Indicators"
                                variant="outlined"
                                fullWidth
                                value={indicators}
                                onChange={(e) => setIndicators(e.target.value)}
                                margin="normal"
                            />
                            <Box display="flex" justifyContent="space-between" mt={2}>
                                <Button variant="contained" color="secondary" onClick={analyzeCode}>
                                    Analyze
                                </Button>
                                <Button variant="contained" color="secondary" onClick={runCode}>
                                    Run
                                </Button>
                                <Button variant="contained" color="primary" onClick={uploadStrategy}>
                                    Upload Strategy
                                </Button>
                            </Box>
                        </Box>
                        <Box mb={2}>
                            {activeFile ? (
                                <>
                                    <TextField
                                        label="Filename"
                                        variant="outlined"
                                        fullWidth
                                        value={activeFile.filename}
                                        onChange={(e) => handleFilenameChange(activeFile.id, e.target.value)}
                                        margin="normal"
                                    />
                                    <Box style={{ height: '75vh', marginTop: '10px' }}>
                                        <Editor
                                            height="100%"
                                            language="python"
                                            theme="vs-dark"
                                            value={activeFile.code}
                                            onChange={(value) => handleChange(activeFile.id, value)}
                                            options={{
                                                automaticLayout: true,
                                                scrollBeyondLastLine: true,
                                                minimap: { enabled: true },
                                            }}
                                        />
                                    </Box>
                                </>
                            ) : (
                                <Typography variant="body1">Please add or select a file</Typography>
                            )}
                        </Box>
                        <Box mt={2}>
                            {output.error && (
                                <Paper elevation={3} style={{ padding: '10px', marginBottom: '10px' }}>
                                    <Typography variant="h6" color="error">Errors:</Typography>
                                    <ul>
                                        {output.error.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </Paper>
                            )}
                            {output.warning && (
                                <Paper elevation={3} style={{ padding: '10px', marginBottom: '10px' }}>
                                    <Typography variant="h6" color="warning.main">Warnings:</Typography>
                                    <ul>
                                        {output.warning.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </Paper>
                            )}
                            {output.results && (
                                <Paper elevation={3} style={{ padding: '10px' }}>
                                    <Typography variant="h6">Output:</Typography>
                                    <ul>
                                        {output.results.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </Paper>
                            )}
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};
