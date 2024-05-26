import { useState } from 'react';
import { SignInSide } from './components/signIn';
import { Register } from './components/register';
import { StrategyEditor } from './components/strategy';
import { LandingPage } from './components/landingpage';
import { StrategyListPage } from './components/strategyList';

function App(props) {
    const [state, setState] = useState('landing');
    const [strategy, setStrategy] = useState(null);

    if (state === 'landing') {
        return <LandingPage setPage={setState} />;
    }
    if (state === 'signin') {
        return <SignInSide setPage={setState} />;
    }
    if (state === 'register') {
        return <Register setPage={setState} />;
    }
    if (state === 'dashboard') {
        return (
            <StrategyListPage setPage={setState} setStrategy={setStrategy} />
        );
    }
    if (state === 'strategyEditor') {
        return <StrategyEditor setPage={setState} strategyId={strategy} />;
    }
}

export default App;
