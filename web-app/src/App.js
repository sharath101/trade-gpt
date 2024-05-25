import { useState } from 'react';
import { SignInSide } from './components/signIn';
import { Register } from './components/register';
import { CodeEditor } from './components/code_editor';
import { LandingPage } from './components/landingpage';

function App(props) {
    const [state, setState] = useState("landing");

    if (state == "landing") { return <LandingPage setPage={setState}/>; }
    if (state == "signin") { return <SignInSide setPage={setState}/>; }
    if (state == "register") { return <Register setPage={setState}/>; }
    if (state == "dashboard") { return <CodeEditor setPage={setState}/>; }
    
}

export default App;
