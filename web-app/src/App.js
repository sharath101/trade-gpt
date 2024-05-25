import { useState } from 'react';
import { SignInSide } from './components/signIn';
import { Register } from './components/register'
import { CodeEditor } from './components/code_editor'

function App(props) {
    const [state, setState] = useState("signin");

    if (state == "signin") { return <SignInSide setPage={setState}/>; }
    if (state == "register") { return <Register setPage={setState}/>; }
    if (state == "dashboard") { return <CodeEditor setPage={setState}/>; }
    
}

export default App;
