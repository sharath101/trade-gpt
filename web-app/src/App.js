import { useState } from 'react';
import { SignInSide } from './components/signIn';

function App(props) {
    const [state, setState] = useState("signin");

    if (state == "signin") { return <SignInSide setPage={setState}/>; }
    if (state == "dashboard") { return <h1>Dashboard</h1>; }
    if (state == "register") { return <h1>Register</h1>; }
    
}

export default App;
